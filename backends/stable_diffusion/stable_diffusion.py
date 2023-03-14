import numpy as np
from tqdm import tqdm
import math
from clip_tokenizer import SimpleTokenizer
import inspect

from stdin_input import is_avail, get_input
from PIL import Image, ImageOps
import json
import time
import io
from dataclasses import dataclass
import os 
import importlib
import sys 

MAX_TEXT_LEN = 77

USE_DUMMY_INTERFACE = False

# get the model interface form the environ
if not USE_DUMMY_INTERFACE :
    model_interface_path = os.environ.get('MODEL_INTERFACE_PATH') or "../stable_diffusion_tf_models"

    print("model_interface_path", model_interface_path )

    if model_interface_path[-1] == "/":
        model_interface_path = model_interface_path[:-1]

    module_name = model_interface_path.split("/")[-1]
    module_path = "/".join(model_interface_path.split("/")[:-1])

    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append( os.path.join(dir_path , module_path) )


    ModelInterface = importlib.import_module( module_name +  ".interface").ModelInterface
else:
    from fake_interface import ModelInterface

from schedulers.scheduling_ddim import DDIMScheduler
from schedulers.scheduling_lms_discrete  import LMSDiscreteScheduler
from schedulers.scheduling_pndm import PNDMScheduler
from schedulers.k_euler_ancestral import KEulerAncestralSampler
from schedulers.k_euler import KEulerSampler

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

    negative_prompt:str=""

    batch_size:int =1
    num_steps:int =25
    guidance_scale:float=7.5
    seed:int=None
    soft_seed:int=None
    img_id:int = 1 

    combine_unet_run:bool = False  # if it should do the cond + uncond in single batch

    input_image:str =None
    mask_image:str =None
    
    input_image_strength:float=0.5


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
            tensor_format="np"
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

class StableDiffusion:
    def __init__(self ,  tdict_path , model_name="sd_1x",   callback=None ):


        if callback is None:
            callback = dummy_callback
       
        self.tokenizer = SimpleTokenizer()

        self.current_mode = None
        self.callback = callback

        self.current_model_name = model_name 
        self.current_tdict_path = tdict_path
        self.current_dtype = ModelInterface.default_float_type

        self.model = ModelInterface( self.current_tdict_path , dtype=self.current_dtype, model_name=self.current_model_name )


    def prepare_model_interface(self , sd_run=None ):

        if sd_run.mode == 'inpaint_15':
            model_name = "sd_1x_inpaint"
        else:
            model_name = "sd_1x"

        dtype = sd_run.dtype
        tdict_path = sd_run.tdict_path

        if self.current_model_name != model_name or self.current_dtype != dtype :
            print("Creating model interface")
            assert tdict_path is not None
            self.model.destroy()
            self.model = ModelInterface(tdict_path , dtype=dtype, model_name=model_name )
            self.current_tdict_path = tdict_path
            self.current_dtype = dtype
            self.current_model_name = model_name

        if tdict_path != self.current_tdict_path:
            assert tdict_path is not None
            self.model.load_from_tdict(tdict_path)
            self.current_tdict_path = tdict_path


    def tokenize(self , prompt):
        inputs = self.tokenizer.encode(prompt)
        if len(inputs) >= 77:
            print("Prompt is too long, stripping it ")
            inputs = inputs[:77]
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

     
    def maybe_process_inp_imgs(self, sd_run):
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




    def get_noise(self, seed, shape):
        return np.random.RandomState(seed).normal(size=shape).astype('float32')


    def get_encoded_img(self, sd_run , processes_img):
        enc_out = self.model.run_enc(processes_img)
        enc_out = np.repeat(enc_out, sd_run.batch_size, axis=0 )
        enc_out_mu = enc_out[... , :4 ]
        enc_out_logvar = enc_out[... , 4:]
        enc_out_std = np.exp(0.5 * enc_out_logvar)

        latent = enc_out_mu + enc_out_std*self.get_noise(sd_run.seed+1, enc_out_mu.shape )
        latent = 0.18215 * latent
        return latent



    def prepare_init_latent(self , sd_run):
        n_h = sd_run.img_height // 8
        n_w = sd_run.img_width // 8
  
        if not sd_run.starting_img_given:
            latent_np = self.get_noise(sd_run.seed ,(sd_run.batch_size, n_h, n_w, 4) )

            if sd_run.soft_seed is not None and sd_run.soft_seed >= 0:
                # latent_np = latent_np + 0.1*self.get_noise(sd_run.soft_seed, latent_np.shape ) #option 1 
                nmask = (np.random.RandomState(sd_run.soft_seed).rand(*latent_np.shape ) > 0.99)
                latent_np = latent_np*(1-nmask) + nmask*self.get_noise(sd_run.soft_seed, latent_np.shape )

            # latent_np = latent_np * np.float64(self.scheduler.init_noise_sigma)
            sd_run.latent = latent_np

            sd_run.latent  = sd_run.latent  * self.scheduler.initial_scale

        else:
            latent = self.get_encoded_img(sd_run , sd_run.input_image_processed )
            sd_run.encoded_img_unmasked = np.copy(latent)

            start_timestep = np.array([self.t_to_i(sd_run.start_timestep)] * sd_run.batch_size, dtype=np.int64 )
           
            noise = self.get_noise(sd_run.seed , latent.shape )
            latent = self.scheduler.add_noise(latent, noise, start_timestep )
            sd_run.latent = latent

        sd_run.init_latent = sd_run.latent

        if sd_run.mode == "inpaint_15":
            masked_img  = sd_run.input_image_processed * sd_run.processed_mask
            sd_run.encoded_masked_img = self.get_encoded_img(sd_run , masked_img)


        

    def t_to_i(self, t):
        i = list(self.scheduler.timesteps).index(t)
        print("t 2 i " , i )
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

        if sd_run.combine_unet_run:
            latent_combined = np.concatenate([latent_model_input,latent_model_input])
            temb_combined = np.concatenate([t_emb,t_emb])
            text_emb_combined = np.concatenate([sd_run.unconditional_context , sd_run.context ])

            o = self.model.run_unet(unet_inp=latent_combined, time_emb=temb_combined, text_emb=text_emb_combined )
            sd_run.predicted_unconditional_latent = o[0: o.shape[0]//2 ]
            sd_run.predicted_latent = o[o.shape[0]//2 :]
        else:
            sd_run.predicted_unconditional_latent = self.model.run_unet(unet_inp=latent_model_input, time_emb=t_emb, text_emb=sd_run.unconditional_context )
            sd_run.predicted_latent = self.model.run_unet(unet_inp=latent_model_input, time_emb=t_emb, text_emb=sd_run.context)


    def get_next_latent(self, sd_run ):
        t = sd_run.current_t
        noise_pred = sd_run.predicted_unconditional_latent + sd_run.guidance_scale * (sd_run.predicted_latent  - sd_run.predicted_unconditional_latent)
        
        accepts_eta = "eta" in set(inspect.signature(self.scheduler.step).parameters.keys())
        extra_step_kwargs = {}
        if accepts_eta:
            eta = 0.0 # should be between 0 and 1, but 0 for now
            extra_step_kwargs["eta"] = eta

        step_seed = sd_run.seed + 10000 + self.t_to_i(t)*4242
        latents = self.scheduler.step(noise_pred, self.t_to_i(t), sd_run.latent , seed=step_seed , **extra_step_kwargs)["prev_sample"]
       

        if sd_run.do_masking:

            latent_proper = np.copy(sd_run.encoded_img_unmasked)

            noise = self.get_noise(sd_run.seed , latent_proper.shape )
            latent_proper = self.scheduler.add_noise(latent_proper, noise, np.array([self.t_to_i(sd_run.current_t)] * sd_run.batch_size, dtype=np.int64 ) )

            latents = (latent_proper  * sd_run.processed_mask_downscaled) + (latents * (1 - sd_run.processed_mask_downscaled))

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
        soft_seed=None,
        img_id=0,
        input_image=None,
        mask_image=None,
        negative_prompt="",
        input_image_strength=0.5,
        scheduler='k_euler',
        tdict_path=None, # if none then it will just use current one
        dtype='float16',
        mode="txt2img" # txt2img , img2img, inpaint_15
    ):

        self.scheduler = get_scheduler(scheduler)

        assert mode in ['txt2img' , 'img2img' , 'inpaint_15']

        if tdict_path is None:
            tdict_path = self.current_tdict_path

        sd_run = SDRun(
                prompt=prompt,
                img_height=img_height,
                img_width=img_width,
                batch_size=batch_size,
                num_steps=num_steps,
                guidance_scale=guidance_scale,
                seed=seed,
                soft_seed=soft_seed,
                img_id=img_id,
                input_image=input_image,
                mask_image=mask_image,
                negative_prompt=negative_prompt,
                input_image_strength=input_image_strength,
                tdict_path=tdict_path,
                mode=mode,
                dtype=dtype,
            )

        if mode == "img2img":
            assert input_image is not None and input_image != ""
            sd_run.starting_img_given = True

            if mask_image is not None and mask_image != "":
                sd_run.do_masking = True

        signal = self.callback(state="Starting" , progress=-1  )
        if signal == "stop":
            return

        self.prepare_model_interface(sd_run)

        signal = self.callback(state="Encoding" , progress=-1  )
        if signal == "stop":
            return

        self.prepare_seed(sd_run)
        self.prepare_timesteps(sd_run)
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
        return np.clip(decoded, 0, 255).astype("uint8")


    def timestep_embedding(self, timesteps, dim=320, max_period=10000):
        half = dim // 2
        freqs = np.exp(
            -math.log(max_period) * np.arange(0, half, dtype="float32") / half
        )
        args = np.array(timesteps) * freqs
        embedding = np.concatenate([np.cos(args), np.sin(args)])
        return np.reshape(embedding , (1 , -1 ))

 


