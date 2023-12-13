import numpy as np
from tqdm import tqdm
import math
from .clip_tokenizer import SimpleTokenizer , SimpleTokenizerV2, sdxl_text_projection_mat_path
import inspect

import time
import os 
import copy


MAX_TEXT_LEN = 77


dir_path = os.path.dirname(os.path.realpath(__file__))

from tdict import TDict

from .schedulers.get_scheduler import get_scheduler

from .utils.logging import log_object
from .utils.extra_model_utils import add_lora_ti_weights
from .utils.image_preprocess import process_inp_img 

from .plugins.plugin_system import StableDiffusionPluginMixin
from .utils.utils import get_tdict_model_version

from .plugins.controlnet import ControlNetPlugin
from .plugins.sd15_inpainting import Sd15Inpainting
from .plugins.inpainting import MaskInpainting

from .utils.model_interface import create_sd_model_with_weights

def dummy_callback(state="" , progress=-1):
    pass



class ModelContainer():

    def __init__(self):
        self.reset()

    def reset(self):
        try:
            self.model.destroy()
        except:
            pass
        
        self.model=None
        self.model_type=None
        self.model_config=None
        self.weights_config=None


class StableDiffusion(StableDiffusionPluginMixin):
    def __init__(self , model_container , ModelInterfaceClass ,  tdict_path , model_name="sd_1x",   callback=None , debug_output_path=None ):

        self.ModelInterfaceClass = ModelInterfaceClass
        self.model_container = model_container

        if callback is None:
            callback = dummy_callback

        self.plugin_system_init()
       
        self.tokenizer = SimpleTokenizer()
        self.tokenizerv2 = SimpleTokenizerV2()

        self.sd_base_version = 1

        self.current_mode = None
        self.callback = callback

        self.debug_output_path = debug_output_path

        assert model_name is None
        assert tdict_path is None # for now

      

        
        self.add_plugin(MaskInpainting)
        self.add_plugin(Sd15Inpainting)
        self.add_plugin(ControlNetPlugin)

        self.model = None

        self.sdxl_pooled_emb_text_proj_mat = np.load(sdxl_text_projection_mat_path())


    def prepare_model_interface(self , sd_run=None ):

        # self.run_plugin_hook('prepare_model_interface' , 'pre' , sd_run)

        dtype = sd_run.dtype
        tdict_path = sd_run.tdict_path
        second_tdict_path = sd_run.second_tdict_path

        tdict_model_version = get_tdict_model_version(tdict_path) % 1000

        if sd_run.is_control_net and sd_run.is_sd15_inpaint:
            raise ValueError("ControlNet with SD1.5 inpaint is not supported.")

        if sd_run.is_sd15_inpaint:
            model_name = "sd_1x_inpaint"
            if tdict_model_version != 13:
                raise ValueError("The model selected is not compatable with SD1.5 inpainting.")
        elif sd_run.is_control_net:
            model_name = "sd_1x_controlnet"
            if tdict_model_version != 12:
                raise ValueError("Only SD 1.x models are supported with controlnet")
        else:
            if tdict_model_version == 31 : 
                model_name = "sdxl_base"
            elif tdict_model_version == 12 :
                model_name = "sd_1x"
            elif tdict_model_version == 15 :
                if "sd_2x" in self.ModelInterfaceClass.avail_models:
                    model_name = "sd_2x"
                else:
                    raise ValueError("SD 2.x is not supported with this version")
            else:
                raise ValueError("This model is not compatable with this operation")
            
        # self.run_plugin_hook('prepare_model_interface' , 'mid' , sd_run)
        



        if self.model_container.model_type != "SD_normal":
            self.model_container.reset()

        model_config = ("SD_normal" , model_name, dtype)
        weights_config = (tdict_path, second_tdict_path, sd_run.weight_additions)

        create_sd_model_with_weights(self.ModelInterfaceClass, self.model_container, model_config, weights_config)
        self.model = self.model_container.model

        sd_run.model_name = model_name

        if "2x" in model_name:
            self.sd_base_version = 2
        if "xl" in model_name:
            self.sd_base_version = 3
        else :
            self.sd_base_version = 1



    def tokenize(self , prompt):
        
        if self.sd_base_version == 2:
            inputs = self.tokenizerv2.encode(prompt)
        else:
            inputs = self.tokenizer.encode(prompt)
            
        if len(inputs) >= 77:
            print("[SD] Prompt is too long, stripping it ")
            inputs = inputs[:77]
        if self.sd_base_version == 2:
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

        if self.sd_base_version == 3:
            context, penultimate_context = context
            unconditional_context, penultimate_uncond_context = unconditional_context

        sd_run.context = np.repeat(context, sd_run.batch_size, axis=0)
        sd_run.unconditional_context = np.repeat(unconditional_context, sd_run.batch_size, axis=0)
        if self.sd_base_version == 3:
            sd_run.penultimate_context = np.repeat(penultimate_context, sd_run.batch_size, axis=0)
            sd_run.penultimate_uncond_context = np.repeat(penultimate_uncond_context, sd_run.batch_size, axis=0)

        if self.debug_output_path  is not None:
            log_object(sd_run.unconditional_context   , self.debug_output_path  , key="unconditional_context")
            log_object(sd_run.context  , self.debug_output_path  , key="context")
        
        self.run_plugin_hook("generate_text_emb" , "post" , sd_run)

     
    def maybe_process_inp_imgs(self, sd_run):

        if sd_run.input_image_path is not None and sd_run.input_image_path != "": 

            sd_run.img_height, sd_run.img_width, sd_run.input_image_processed , sd_run.input_image_processed_downscaled = process_inp_img(sd_run.input_image_path, image_size=sd_run.inp_image_resize_mode , new_w=sd_run.img_width , new_h=sd_run.img_height  )
            sd_run.input_image_processed = sd_run.input_image_processed[None]
            sd_run.input_image_processed_downscaled = sd_run.input_image_processed_downscaled[None]

        self.run_plugin_hook("process_inp_imgs", "post", sd_run)


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
            assert shape == (1,64,64,4), "only implemnted for (1,64,64,4)"
            if len(shape) == 4:
                shape = (shape[0] , shape[3] , shape[1] , shape[2])
            a = torch.randn( (1,4,64,64) ).numpy().astype('float32')
            return np.rollaxis(a , 1 , 4 )
        else:
            raise ValueError("Invalid seed type")
        
    def get_modded_noise(self, seed, shape ,seed_type , small_mod_seed):
        noise = self.get_noise(seed, shape , seed_type)
        if small_mod_seed is not None and small_mod_seed >= 0:
            nmask = (np.random.RandomState(small_mod_seed).rand(*noise.shape ) > 0.99)
            noise = noise*(1-nmask) + nmask*self.get_noise(small_mod_seed, noise.shape , seed_type=seed_type )

        return noise


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
            latent_np = self.get_modded_noise(sd_run.seed ,(sd_run.batch_size, n_h, n_w, 4) ,  seed_type=sd_run.seed_type, small_mod_seed=sd_run.small_mod_seed  )

            if self.debug_output_path is not None:
                log_object(latent_np , self.debug_output_path  , key="latent_np")

            # latent_np = latent_np * np.float64(self.scheduler.init_noise_sigma)
            sd_run.latent = latent_np

            sd_run.latent  = sd_run.latent  * self.scheduler.initial_scale

        else:
            latent = self.get_encoded_img(sd_run , sd_run.input_image_processed )

            if self.debug_output_path is not None:
                log_object(latent  , self.debug_output_path  , key="encoded_img")

            sd_run.encoded_img_orig = np.copy(latent)

            start_timestep = np.array([self.t_to_i(sd_run.start_timestep)] * sd_run.batch_size, dtype=np.int64 )
           
            noise = self.get_modded_noise(sd_run.seed , latent.shape , seed_type=sd_run.seed_type, small_mod_seed=sd_run.small_mod_seed  )

            if self.debug_output_path is not None:
                log_object(noise , self.debug_output_path  , key="noise_e")

            latent = self.scheduler.add_noise(latent, noise, start_timestep )
            sd_run.latent = latent

        sd_run.init_latent = sd_run.latent

        if self.debug_output_path is not None:
            log_object(sd_run.init_latent  , self.debug_output_path  , key="sd_run_init_latent")

        self.run_plugin_hook("prepare_init_latent" , "post" , sd_run)



        

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

        if sd_run.small_mod_seed is not None and sd_run.small_mod_seed >= 0 :
            sd_run.small_mod_seed = sd_run.small_mod_seed + 1234*sd_run.img_id
        else:
            sd_run.seed = sd_run.seed  + 1234*sd_run.img_id

    def prepare_time_embed(self, sd_run):
        t = sd_run.current_t
        timestep_batch = np.array([t])
        t_emb = self.timestep_embedding(timestep_batch)
        sd_run.t_emb = np.repeat(t_emb, sd_run.batch_size, axis=0)

    def get_unet_out(self, sd_run):

        sd_run.controls = None

        self.prepare_time_embed(sd_run)

        sd_run.latent_model_input = sd_run.latent

        sd_run.latent_model_input =  sd_run.latent_model_input * self.scheduler.get_input_scale(self.t_to_i(sd_run.current_t))

        self.run_plugin_hook("get_unet_out" , "mid" , sd_run)

        if self.debug_output_path is not None:
            log_object(sd_run.latent_model_input  , self.debug_output_path  , key="sd_run.latent_model_input")
            log_object(sd_run.t_emb  , self.debug_output_path  , key="sd_run")

        if self.sd_base_version == 3:
            fixed_vector_cond = self.get_sdxl_fixed_vector(sd_run, is_cond=True) #np.zeros((1,2816)).astype(float)
            fixed_vector_uncond = self.get_sdxl_fixed_vector(sd_run, is_cond=False )
        else:
            fixed_vector_cond = None
            fixed_vector_uncond = None
            

        if sd_run.combine_unet_run:
            latent_combined = np.concatenate([sd_run.latent_model_input,sd_run.latent_model_input])
            temb_combined = np.concatenate([sd_run.t_emb,sd_run.t_emb])
            text_emb_combined = np.concatenate([sd_run.unconditional_context , sd_run.context ])
            assert sd_run.control_weight_current_cond == sd_run.control_weight_current_uncond, "not supported"
            o = self.model.run_unet(unet_inp=latent_combined, time_emb=temb_combined, text_emb=text_emb_combined , control_inp=sd_run.controls, control_weight=sd_run.control_weight_current_cond, fixed_vector=fixed_vector )
            sd_run.predicted_unconditional_latent = o[0: o.shape[0]//2 ]
            sd_run.predicted_latent = o[o.shape[0]//2 :]
        else:
            sd_run.predicted_unconditional_latent = self.model.run_unet(unet_inp=sd_run.latent_model_input, time_emb=sd_run.t_emb, text_emb=sd_run.unconditional_context , control_inp=sd_run.controls, control_weight=(sd_run.control_weight_current_uncond), fixed_vector=fixed_vector_uncond)
            sd_run.predicted_latent = self.model.run_unet(unet_inp=sd_run.latent_model_input, time_emb=sd_run.t_emb, text_emb=sd_run.context, control_inp=sd_run.controls, control_weight=(sd_run.control_weight_current_cond) , fixed_vector=fixed_vector_cond )

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
        sd_run.next_latents = self.scheduler.step(noise_pred, self.t_to_i(t), sd_run.latent , seed=step_seed , **extra_step_kwargs)["prev_sample"]

        if self.debug_output_path is not None:
            log_object(sd_run.next_latents  , self.debug_output_path  , key="latents_step")

        self.run_plugin_hook("get_next_latent" , "post" , sd_run)

        # sd_run.next_latents = self.scheduler.step(model_output=noise_pred, timestep=t , sample=sd_run.latent , **extra_step_kwargs)["prev_sample"]
        sd_run.latent = sd_run.next_latents



    def generate(
        self,
        sd_run_params
    ):
        
        sd_run = copy.deepcopy(sd_run_params)

        if sd_run.input_image_strength > 1:
            sd_run.input_image_strength = sd_run.input_image_strength/100.0
        
        if sd_run.do_v_prediction:
            if sd_run.scheduler not in ['ddim']:
                raise ValueError("V-prediction only works with DDIM")
            sd_run.scheduler = sd_run.scheduler + "_v"

        if sd_run.force_use_given_size:
            sd_run.inp_image_resize_mode = None

        
        
        
        assert sd_run.mode in ['txt2img' , 'img2img' ]
        
        if sd_run.dtype not in self.ModelInterfaceClass.avail_float_types:
            sd_run.dtype = self.ModelInterfaceClass.default_float_type
        
        sd_run.weight_additions = ()
        for tpath in sd_run.lora_tdict_paths:
            sd_run.weight_additions += (('lora' ,tpath , sd_run.lora_tdict_paths[tpath] ),)

        if sd_run.is_clip_skip_2 :
            assert self.sd_base_version == 1, "Clip skip is only supported with 1.x models"
            sd_run.weight_additions += (('clip_skip_2' , None , None),)

        
        self.run_plugin_hook("generate" , "pre", sd_run)

        if sd_run.mode == "img2img"  :
            assert sd_run.input_image_path is not None and sd_run.input_image_path != ""
            sd_run.starting_img_given = True


        if self.callback(state="Starting" , progress=-1  )  == "stop":
            return

        self.prepare_model_interface(sd_run)

        if sd_run.scheduler == "__default_for_model__":
            sd_run.scheduler = "karras"
            # if sd_run.model_name == "sdxl_base":
            #     sd_run.scheduler = "karras"
            # else:
            #     sd_run.scheduler = "ddim"

        self.scheduler = get_scheduler(sd_run.scheduler)


        if self.callback(state="Encoding" , progress=-1  ) == "stop":
            return

        self.prepare_seed(sd_run)
        self.prepare_timesteps(sd_run)

        if self.debug_output_path is not None:
            log_object(sd_run , self.debug_output_path  , key="sd_run")

        self.maybe_process_inp_imgs(sd_run)
                
        # Tokenize prompt (i.e. starting context)
        self.generate_text_emb(sd_run)
        self.prepare_init_latent(sd_run)

        if self.callback(state="Generating" , progress=-1  ) == "stop":
            return

        for i, t in tqdm(enumerate(sd_run.working_timesteps)):

            sd_run.current_t = t
            self.get_unet_out(sd_run)
            self.get_next_latent(sd_run)

            if self.callback(state="Generating" , progress=(100*(i+1)/len(sd_run.working_timesteps)) )  == "stop":
                return

        if self.callback(state="Decoding" , progress=-1 ) == "stop":
            return

        # Decoding stage
        sd_run.latent = sd_run.latent/0.18215
        sd_run.decoded = self.model.run_dec(sd_run.latent)

        self.run_plugin_hook("decode" , "mid" , sd_run)
        
        sd_run.decoded = ((sd_run.decoded + 1) / 2) * 255
        sd_run.ret = ({"img" : np.clip(sd_run.decoded, 0, 255).astype("uint8")})

        self.run_plugin_hook("generate" , "post" , sd_run)
        
        return sd_run.ret
    
    def get_sdxl_fixed_vector(self, sd_run, is_cond):
        height_emb = self.timestep_embedding(sd_run.img_height , dim=256 )
        width_emb = self.timestep_embedding(sd_run.img_width , dim=256 )
        zero_emb = self.timestep_embedding(0 , dim=256 )

        # used in refine:
        aesth_emb = self.timestep_embedding(6 , dim=256 )
        neg_aesth_emb = self.timestep_embedding(2.5 , dim=256 )

        if is_cond: 
            if 49407 in list(sd_run.tokens[0]) :
                last_tok_index = list(sd_run.tokens[0]).index( 49407 )
            else:
                last_tok_index = -1 
            pooled = sd_run.penultimate_context[: , last_tok_index ]
        else:
            if 49407 in list(sd_run.unconditional_tokens[0]) :
                last_tok_index = list(sd_run.unconditional_tokens[0]).index( 49407 )
            else:
                last_tok_index = -1 

            pooled = sd_run.penultimate_uncond_context[: , last_tok_index ]

        pooled = pooled @ self.sdxl_pooled_emb_text_proj_mat


        vec = np.concatenate([pooled, height_emb, width_emb, zero_emb, zero_emb, height_emb, width_emb ], axis=-1)
        assert vec.shape == (1, 2816)
        return vec



    def timestep_embedding(self, timesteps, dim=320, max_period=10000):
        half = dim // 2
        freqs = np.exp(
            -math.log(max_period) * np.arange(0, half, dtype="float32") / half
        )
        args = np.array(timesteps) * freqs
        embedding = np.concatenate([np.cos(args), np.sin(args)])
        return np.reshape(embedding , (1 , -1 ))
