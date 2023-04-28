import numpy as np
from tqdm import tqdm
import math
from clip_tokenizer import SimpleTokenizer , SimpleTokenizerV2
import inspect

from stdin_input import is_avail, get_input
from PIL import Image, ImageOps
import json
import time
import io
from dataclasses import dataclass
import os 
import sys 
import functools

from control_processors.process_body_pose import process_image_body_pose
from control_processors.process_midas_depth import process_image_midas_depth

MAX_TEXT_LEN = 77


dir_path = os.path.dirname(os.path.realpath(__file__))

from tdict import TDict

from schedulers.scheduling_ddim import DDIMScheduler
from schedulers.scheduling_lms_discrete  import LMSDiscreteScheduler
from schedulers.scheduling_pndm import PNDMScheduler
from schedulers.k_euler_ancestral import KEulerAncestralSampler
from schedulers.k_euler import KEulerSampler

from utils.logging import log_object
from utils.extra_model_utils import add_lora_ti_weights

image_preprocess_model_paths = {
    "body_pose" : None , 
    "midas_depth" : None
}


def process_inp_img(input_image):
    input_image = Image.open(input_image)
    input_image = input_image.convert('RGB')
    w , h = input_image.size
    
    if w > h:
        new_w = 512
        new_h  = round((h * new_w / w)/64)*64
    else:
        new_h = 512
        new_w  = round((w * new_h / h)/64)*64

    input_image_downscaled = ImageOps.fit(input_image, (new_w//8, new_h//8), method = Image.BILINEAR ,
                   bleed = 0.0, centering =(0.5, 0.5))

    input_image = ImageOps.fit(input_image, (new_w, new_h), method = Image.BILINEAR ,
                   bleed = 0.0, centering =(0.5, 0.5))
    input_image = np.array(input_image)[... , :3]
    input_image_downscaled = np.array(input_image_downscaled)[... , :3]
    input_image = (input_image.astype("float32") / 255.0)*2 - 1 
    input_image_downscaled = (input_image_downscaled.astype("float32") / 255.0)*2 - 1 
    return new_h , new_w  , input_image , input_image_downscaled



@dataclass
class SDRun():
    
    prompt: str

    mode:str="txt2img"
    tdict_path:str=None
    dtype:str= "float16"

    starting_img_given:bool = False 
    do_masking:bool = False # if you wanna mask the latent at every sd step
    img_height: int = None
    img_width: int = None

    inp_img_preprocesser:str = None # name of the preprocess fn 

    negative_prompt:str=""

    batch_size:int =1
    num_steps:int =25
    guidance_scale:float=7.5
    seed:int=None
    seed_type:str="np"
    soft_seed:int=None
    img_id:int = 1 

    combine_unet_run:bool = False  # if it should do the cond + uncond in single batch

    input_image:str =None
    mask_image:str =None
    
    input_image_strength:float=0.5
    second_tdict_path:str = None
    weight_additions:tuple = ()


def get_scheduler(name):
    if name == "ddim":
        return DDIMScheduler(
            beta_start=0.00085,
            beta_end=0.012,
            beta_schedule="scaled_linear",
            clip_sample= False,
            num_train_timesteps= 1000,
            set_alpha_to_one=False,
            # steps_offset= 1,
            trained_betas= None,
            tensor_format="np",
        )

    if name == "ddim_v":
        return DDIMScheduler(
            beta_start=0.00085,
            beta_end=0.012,
            beta_schedule="scaled_linear",
            clip_sample= False,
            num_train_timesteps= 1000,
            set_alpha_to_one=False,
            # steps_offset= 1,
            trained_betas= None,
            tensor_format="np",
            prediction_type="v_prediction"
        )

    if name == "lmsd":
        return LMSDiscreteScheduler(
            beta_start=0.00085,
            beta_end=0.012,
            beta_schedule="scaled_linear",
            tensor_format="np")

    if name == "pndm":
        return PNDMScheduler(
            beta_start=0.00085,
            beta_end=0.012,
            beta_schedule="scaled_linear",
            skip_prk_steps = True,
            tensor_format="np")

    if name == "k_euler_ancestral":
        return KEulerAncestralSampler()

    if name == "k_euler":
        return KEulerSampler()


def dummy_callback(state="" , progress=-1):
    pass



def get_preprocess_function(preprocess_function_name):
    if preprocess_function_name == "body_pose":
        body_pose_model_path = image_preprocess_model_paths['body_pose']
        return functools.partial(process_image_body_pose, model_path=body_pose_model_path)
    elif preprocess_function_name == "midas_depth":
        midas_depth_model_path = image_preprocess_model_paths['midas_depth']
        return functools.partial(process_image_midas_depth, model_path=midas_depth_model_path)

    else:
        raise ValueError("invalid function name")


tdict_model_versions = {}
def get_tdict_model_version(tdict_path):
    if tdict_path in tdict_model_versions:
        return tdict_model_versions[tdict_path]
    f = TDict(tdict_path, mode='r')
    tdict_model_versions[ tdict_path] = f.ctdict_version
    return tdict_model_versions[ tdict_path] 


class StableDiffusion:
    def __init__(self , ModelInterfaceClass ,  tdict_path , model_name="sd_1x",   callback=None , debug_output_path=None ):

        self.ModelInterfaceClass = ModelInterfaceClass

        if callback is None:
            callback = dummy_callback
       
        self.tokenizer = SimpleTokenizer()
        self.tokenizerv2 = SimpleTokenizerV2()

        self.current_mode = None
        self.callback = callback

        self.debug_output_path = debug_output_path

        self.current_model_name = model_name 
        self.current_tdict_path = tdict_path
        self.second_current_tdict_path = None
        self.current_weight_additions = () #represents weights which are added on top, eg. Lora, TI etc
        self.current_dtype = self.ModelInterfaceClass.default_float_type

        if model_name is not None:
            self.model = self.ModelInterfaceClass( TDict(self.current_tdict_path ), dtype=self.current_dtype, model_name=self.current_model_name )
        else:
            self.model = None


    def prepare_model_interface(self , sd_run=None ):

        dtype = sd_run.dtype
        tdict_path = sd_run.tdict_path
        second_tdict_path = sd_run.second_tdict_path

        tdict_model_version = get_tdict_model_version(tdict_path) % 1000

        if sd_run.mode == 'inpaint_15':
            model_name = "sd_1x_inpaint"
            if tdict_model_version != 13:
                raise ValueError("The model selected is not compatable with SD1.5 inpainting.")
        elif sd_run.mode == "controlnet":
            model_name = "sd_1x_controlnet"
            if tdict_model_version != 12:
                raise ValueError("Only SD 1.x models are supported with controlnet")
        else:
            if tdict_model_version == 12 :
                model_name = "sd_1x"
            elif tdict_model_version == 15 :
                if "sd_2x" in self.ModelInterfaceClass.avail_models:
                    model_name = "sd_2x"
                else:
                    raise ValueError("SD 2.x is not supported with this version")
            else:
                raise ValueError("This model is not compatable with this operation")


       

        if self.current_model_name != model_name or self.current_dtype != dtype :
            print("[SD] Creating model interface")
            assert tdict_path is not None

            if self.model is not None:
                self.model.destroy()

            if second_tdict_path is not None:
                tdict2 = TDict(second_tdict_path)
            else:
                tdict2 = None

            self.model = self.ModelInterfaceClass(TDict(tdict_path ) , dtype=dtype, model_name=model_name , second_tdict=tdict2)
            self.current_tdict_path = tdict_path
            self.second_current_tdict_path = second_tdict_path
            self.current_dtype = dtype
            self.current_model_name = model_name

        weight_additions = sd_run.weight_additions

        if tdict_path != self.current_tdict_path or second_tdict_path != self.second_current_tdict_path or weight_additions != self.current_weight_additions:
            assert tdict_path is not None

            tdict_1 = None

            if (tdict_path == self.current_tdict_path and second_tdict_path == self.second_current_tdict_path and self.current_weight_additions == ()):
                pass
                # current weigh has already been loaded with some tdicts , and nothing has been added
            else:
                if second_tdict_path is not None:
                    tdict2 = TDict(second_tdict_path)
                else:
                    tdict2 = None

                tdict_1 = TDict(tdict_path)

                self.model.load_from_tdict(tdict_1, tdict2 )

                self.current_tdict_path = tdict_path
                self.second_current_tdict_path = second_tdict_path

            if weight_additions is not None and weight_additions != ():
                if tdict_1 is None:
                    tdict_1 = TDict(tdict_path)

                print("[SD] Loading LoRA weights")
                extra_weights = add_lora_ti_weights(tdict_1 , weight_additions )
                self.model.load_from_state_dict(extra_weights )
                self.current_weight_additions = weight_additions


    def tokenize(self , prompt):
        if self.current_model_name == "sd_2x":
            inputs = self.tokenizerv2.encode(prompt)
        else:
            inputs = self.tokenizer.encode(prompt)
            
        if len(inputs) >= 77:
            print("[SD] Prompt is too long, stripping it ")
            inputs = inputs[:77]
        if self.current_model_name == "sd_2x":
            phrase = inputs + [0] * (77 - len(inputs))
        else:
            phrase = inputs + [49407] * (77 - len(inputs))
        phrase = np.array(phrase)[None].astype("int32")
        return phrase



    def generate_text_emb(self, sd_run):
        sd_run.tokens = self.tokenize(sd_run.prompt)
        if sd_run.negative_prompt is None:
            sd_run.negative_prompt = ""
        sd_run.unconditional_tokens = self.tokenize(sd_run.negative_prompt)

        pos_ids = np.array(list(range(77)))[None].astype("int32")

        context = self.model.run_text_enc(sd_run.tokens, pos_ids)
        unconditional_context = self.model.run_text_enc(sd_run.unconditional_tokens, pos_ids)

        sd_run.context = np.repeat(context, sd_run.batch_size, axis=0)
        sd_run.unconditional_context = np.repeat(unconditional_context, sd_run.batch_size, axis=0)

        if self.debug_output_path  is not None:
            log_object(sd_run.unconditional_context   , self.debug_output_path  , key="unconditional_context")
            log_object(sd_run.context  , self.debug_output_path  , key="context")

     
    def maybe_process_inp_imgs(self, sd_run):

        if sd_run.inp_img_preprocesser is not None: #if you want to preprocess input image
            sd_run.input_image_orig = sd_run.input_image
            outfname = sd_run.input_image + ".controlnet_processed_" + sd_run.inp_img_preprocesser  + ".jpg"
            if not os.path.exists(outfname):
                preprocess_function = get_preprocess_function(sd_run.inp_img_preprocesser)
                preprocess_function(inp_fname=sd_run.input_image , out_fname=outfname)
                assert os.path.exists(outfname)
            sd_run.input_image = outfname


        if sd_run.input_image is not None and sd_run.input_image != "": 
            sd_run.img_height, sd_run.img_width, sd_run.input_image_processed , sd_run.input_image_processed_downscaled = process_inp_img(sd_run.input_image)
            sd_run.input_image_processed = sd_run.input_image_processed[None]
            sd_run.input_image_processed_downscaled = sd_run.input_image_processed_downscaled[None]

        if sd_run.mask_image is not None and sd_run.mask_image != "":
            h , w , mask_image , _ = process_inp_img(sd_run.mask_image)
            assert h == sd_run.img_height , "Mask should be of the same size as inp image"
            assert w == sd_run.img_width , "Mask should be of the same size as inp image"
            mask_image = (mask_image + 1 )/2 
            mask_image = mask_image[None]
            mask_image = 1 - mask_image # repaint white keep black
            mask_image = np.copy(mask_image[... , :1 ])
            mask_image_sm = np.copy(mask_image[: , ::8 , ::8  ])

            mask_image[mask_image < 0.5] = 0
            mask_image[mask_image >= 0.5] = 1

            mask_image_sm[mask_image_sm < 0.5] = 0
            mask_image_sm[mask_image_sm >= 0.5] = 1

            sd_run.processed_mask_downscaled = mask_image_sm
            sd_run.processed_mask = mask_image


    def prepare_timesteps(self, sd_run):
        accepts_offset = "offset" in set(inspect.signature(self.scheduler.set_timesteps).parameters.keys())
        extra_set_kwargs = {}
        offset = 0
        if accepts_offset:
            offset = 1
            extra_set_kwargs["offset"] = 1

        self.scheduler.set_timesteps(sd_run.num_steps, **extra_set_kwargs)

        sd_run.working_timesteps = self.scheduler.timesteps

        if sd_run.starting_img_given: 
            init_timestep = int(sd_run.num_steps * (1-sd_run.input_image_strength)) + offset
            init_timestep = min(init_timestep, sd_run.num_steps)
            sd_run.start_timestep = self.scheduler.timesteps[-init_timestep]
            
            t_start = max(sd_run.num_steps - init_timestep + offset, 0)
            sd_run.working_timesteps = sd_run.working_timesteps[t_start:]




    def get_noise(self, seed, shape, seed_type):
        if  seed_type == 'np':
            return np.random.RandomState(seed).normal(size=shape).astype('float32')
        elif seed_type == 'pt':
            import torch
            torch.manual_seed(seed)
            if len(shape) == 4:
                shape = (shape[0] , shape[3] , shape[1] , shape[2])
            a = torch.randn( (1,4,64,64) ).numpy().astype('float32')
            return np.rollaxis(a , 1 , 4 )
        else:
            raise ValueError("Invalid seed type")


    def get_encoded_img(self, sd_run , processes_img):
        enc_out = self.model.run_enc(processes_img)
        enc_out = np.repeat(enc_out, sd_run.batch_size, axis=0 )
        enc_out_mu = enc_out[... , :4 ]
        enc_out_logvar = enc_out[... , 4:]
        enc_out_std = np.exp(0.5 * enc_out_logvar)

        latent = enc_out_mu + enc_out_std*self.get_noise(sd_run.seed+1, enc_out_mu.shape , seed_type=sd_run.seed_type)
        latent = 0.18215 * latent
        return latent



    def prepare_init_latent(self , sd_run):
        n_h = sd_run.img_height // 8
        n_w = sd_run.img_width // 8
  
        if not sd_run.starting_img_given:
            latent_np = self.get_noise(sd_run.seed ,(sd_run.batch_size, n_h, n_w, 4) ,  seed_type=sd_run.seed_type)

            if self.debug_output_path is not None:
                log_object(latent_np , self.debug_output_path  , key="latent_np")

            if sd_run.soft_seed is not None and sd_run.soft_seed >= 0:
                # latent_np = latent_np + 0.1*self.get_noise(sd_run.soft_seed, latent_np.shape, seed_type=sd_run.seed_type ) #option 1 
                nmask = (np.random.RandomState(sd_run.soft_seed).rand(*latent_np.shape ) > 0.99)
                latent_np = latent_np*(1-nmask) + nmask*self.get_noise(sd_run.soft_seed, latent_np.shape , seed_type=sd_run.seed_type )

            # latent_np = latent_np * np.float64(self.scheduler.init_noise_sigma)
            sd_run.latent = latent_np

            sd_run.latent  = sd_run.latent  * self.scheduler.initial_scale

        else:
            latent = self.get_encoded_img(sd_run , sd_run.input_image_processed )

            if self.debug_output_path is not None:
                log_object(latent  , self.debug_output_path  , key="encoded_img")

            sd_run.encoded_img_unmasked = np.copy(latent)

            start_timestep = np.array([self.t_to_i(sd_run.start_timestep)] * sd_run.batch_size, dtype=np.int64 )
           
            noise = self.get_noise(sd_run.seed , latent.shape , seed_type=sd_run.seed_type )

            if self.debug_output_path is not None:
                log_object(noise , self.debug_output_path  , key="noise_e")

            latent = self.scheduler.add_noise(latent, noise, start_timestep )
            sd_run.latent = latent

        sd_run.init_latent = sd_run.latent

        if self.debug_output_path is not None:
            log_object(sd_run.init_latent  , self.debug_output_path  , key="sd_run_init_latent")

        if sd_run.mode == "inpaint_15":
            masked_img  = sd_run.input_image_processed * sd_run.processed_mask
            sd_run.encoded_masked_img = self.get_encoded_img(sd_run , masked_img)


        

    def t_to_i(self, t):
        i = list(self.scheduler.timesteps).index(t)
        assert i >= 0
        return i

    def prepare_seed(self , sd_run):
        try:
            sd_run.seed = int(sd_run.seed)
            if sd_run.seed < 1:
                sd_run.seed = int(time.time()*100)%1002487 
        except:
            pass

        if sd_run.seed is None:
            sd_run.seed = int(time.time()*100)%1002487

        if sd_run.soft_seed is not None and sd_run.soft_seed >= 0 :
            sd_run.soft_seed = sd_run.soft_seed + 1234*sd_run.img_id
        else:
            sd_run.seed = sd_run.seed  + 1234*sd_run.img_id

    def get_unet_out(self, sd_run):

        t = sd_run.current_t
        timestep_batch = np.array([t])
        t_emb = self.timestep_embedding(timestep_batch)
        t_emb = np.repeat(t_emb, sd_run.batch_size, axis=0)

        latent_model_input = sd_run.latent
        if sd_run.mode == "inpaint_15":
            latent_model_input = np.concatenate([
                latent_model_input , 
                np.repeat( (1 - sd_run.processed_mask_downscaled ), sd_run.batch_size , axis=0) , 
                sd_run.encoded_masked_img 
            ], axis=-1)
   
        latent_model_input =  latent_model_input * self.scheduler.get_input_scale(self.t_to_i(t))

        if sd_run.mode == "controlnet":
            hint_img = (sd_run.input_image_processed+1)/2

            if self.debug_output_path is not None:
                log_object(hint_img , self.debug_output_path  , "hint_img")

            if sd_run.combine_unet_run:
                hint_img = np.repeat(hint_img, sd_run.batch_size, axis=0)
            controls = self.model.run_controlnet(unet_inp=latent_model_input, time_emb=t_emb, text_emb=sd_run.context, hint_img=hint_img )
        else:
            controls = None

        if self.debug_output_path is not None:
            log_object(latent_model_input  , self.debug_output_path  , key="latent_model_input")
            log_object(t_emb  , self.debug_output_path  , key="t_emb")
            log_object(controls  , self.debug_output_path  , key="controls")

        if sd_run.combine_unet_run:
            latent_combined = np.concatenate([latent_model_input,latent_model_input])
            temb_combined = np.concatenate([t_emb,t_emb])
            text_emb_combined = np.concatenate([sd_run.unconditional_context , sd_run.context ])

            o = self.model.run_unet(unet_inp=latent_combined, time_emb=temb_combined, text_emb=text_emb_combined , control_inp=controls)
            sd_run.predicted_unconditional_latent = o[0: o.shape[0]//2 ]
            sd_run.predicted_latent = o[o.shape[0]//2 :]
        else:
            sd_run.predicted_unconditional_latent = self.model.run_unet(unet_inp=latent_model_input, time_emb=t_emb, text_emb=sd_run.unconditional_context , control_inp=controls)
            sd_run.predicted_latent = self.model.run_unet(unet_inp=latent_model_input, time_emb=t_emb, text_emb=sd_run.context, control_inp=controls)

        if self.debug_output_path is not None:
            log_object(sd_run.predicted_unconditional_latent  , self.debug_output_path  , key="unet_out_uncond")
            log_object(sd_run.predicted_latent  , self.debug_output_path  , key="unet_out_cond")


    def get_next_latent(self, sd_run ):
        t = sd_run.current_t
        noise_pred = sd_run.predicted_unconditional_latent + sd_run.guidance_scale * (sd_run.predicted_latent  - sd_run.predicted_unconditional_latent)

        if self.debug_output_path is not None:
            log_object(noise_pred  , self.debug_output_path  , key="noise_pred")
        
        accepts_eta = "eta" in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta:
            eta = 0.0 # should be between 0 and 1, but 0 for now
            extra_step_kwargs["eta"] = eta

        step_seed = sd_run.seed + 10000 + self.t_to_i(t)*4242
        latents = self.scheduler.step(noise_pred, self.t_to_i(t), sd_run.latent , seed=step_seed , **extra_step_kwargs)["prev_sample"]

        if self.debug_output_path is not None:
            log_object(latents  , self.debug_output_path  , key="latents_step")

        if sd_run.do_masking:

            latent_proper = np.copy(sd_run.encoded_img_unmasked)

            noise = self.get_noise(sd_run.seed , latent_proper.shape , seed_type=sd_run.seed_type )
            latent_proper = self.scheduler.add_noise(latent_proper, noise, np.array([self.t_to_i(sd_run.current_t)] * sd_run.batch_size, dtype=np.int64 ) )

            latents = (latent_proper  * sd_run.processed_mask_downscaled) + (latents * (1 - sd_run.processed_mask_downscaled))

        if self.debug_output_path is not None:
            log_object(latents  , self.debug_output_path  , key="latents_mm")

        # latents = self.scheduler.step(model_output=noise_pred, timestep=t , sample=sd_run.latent , **extra_step_kwargs)["prev_sample"]
        sd_run.latent = latents



    def generate(
        self,
        prompt, 
        img_height, img_width,
        batch_size=1,
        num_steps=25,
        guidance_scale=7.5,
        temperature=None, 
        seed=None,
        seed_type="np",
        soft_seed=None,
        img_id=0,
        input_image=None,
        mask_image=None,
        negative_prompt="",
        input_image_strength=0.5,
        scheduler='k_euler',
        tdict_path=None, # if none then it will just use current one
        second_tdict_path=None,
        lora_tdict_paths={}, # {tdict_path: ratio}
        inp_img_preprocesser=None, # for controlnet
        dtype='float16',
        mode="txt2img", # txt2img , img2img, inpaint_15
    ):



        self.scheduler = get_scheduler(scheduler)

        assert mode in ['txt2img' , 'img2img' , 'inpaint_15', 'controlnet']

        if dtype not in self.ModelInterfaceClass.avail_float_types:
            dtype = self.ModelInterfaceClass.default_float_type

        if tdict_path is None:
            tdict_path = self.current_tdict_path

        weight_additions = ()
        for tpath in lora_tdict_paths:
            weight_additions += (('lora' ,tpath , lora_tdict_paths[tpath] ),)

        sd_run = SDRun(
                prompt=prompt,
                img_height=img_height,
                img_width=img_width,
                batch_size=batch_size,
                num_steps=num_steps,
                guidance_scale=guidance_scale,
                seed=seed,
                seed_type=seed_type,
                soft_seed=soft_seed,
                img_id=img_id,
                input_image=input_image,
                mask_image=mask_image,
                negative_prompt=negative_prompt,
                input_image_strength=input_image_strength,
                tdict_path=tdict_path,
                second_tdict_path=second_tdict_path,
                weight_additions=weight_additions,
                mode=mode,
                dtype=dtype,
                inp_img_preprocesser=inp_img_preprocesser,
            )

        if mode == "img2img":
            assert input_image is not None and input_image != ""
            sd_run.starting_img_given = True

            if mask_image is not None and mask_image != "":
                sd_run.do_masking = True

        if mode == "controlnet":
            assert input_image is not None and input_image != ""

        signal = self.callback(state="Starting" , progress=-1  )
        if signal == "stop":
            return

        self.prepare_model_interface(sd_run)

        signal = self.callback(state="Encoding" , progress=-1  )
        if signal == "stop":
            return

        self.prepare_seed(sd_run)
        self.prepare_timesteps(sd_run)

        if self.debug_output_path is not None:
            log_object(sd_run , self.debug_output_path  , key="sd_run")

        self.maybe_process_inp_imgs(sd_run)
                
        # Tokenize prompt (i.e. starting context)
        self.generate_text_emb(sd_run)
        self.prepare_init_latent(sd_run)

        signal = self.callback(state="Generating" , progress=-1  )
        if signal == "stop":
            return

        for i, t in tqdm(enumerate(sd_run.working_timesteps)):

            sd_run.current_t = t
            self.get_unet_out(sd_run)
            self.get_next_latent(sd_run)

            signal = self.callback(state="Generating" , progress=(100*(i+1)/len(sd_run.working_timesteps)) )
            if signal == "stop":
                return

        signal = self.callback(state="Decoding" , progress=-1  )
        if signal == "stop":
            return

        # Decoding stage
        sd_run.latent = sd_run.latent/0.18215
        decoded = self.model.run_dec(sd_run.latent)

        if sd_run.do_masking:
            decoded = (sd_run.input_image_processed  * sd_run.processed_mask) + (decoded * (1 - sd_run.processed_mask ))
        
        decoded = ((decoded + 1) / 2) * 255
        ret = ({"img" : np.clip(decoded, 0, 255).astype("uint8")})

        if sd_run.inp_img_preprocesser is not None:
            ret['aux_img'] = sd_run.input_image

        return ret


    def timestep_embedding(self, timesteps, dim=320, max_period=10000):
        half = dim // 2
        freqs = np.exp(
            -math.log(max_period) * np.arange(0, half, dtype="float32") / half
        )
        args = np.array(timesteps) * freqs
        embedding = np.concatenate([np.cos(args), np.sin(args)])
        return np.reshape(embedding , (1 , -1 ))

 


