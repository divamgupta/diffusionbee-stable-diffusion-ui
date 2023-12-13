from .applets import AppletBase
import json
from .form_utils import get_textbox , get_file_textbox , get_output_text , get_textarea, get_output_img
from stable_diffusion.stable_diffusion import StableDiffusion
from interface import ModelInterface
import copy
import numpy as np
import math
from stable_diffusion.plugins.base_plugin import BasePlugin
from stable_diffusion.utils.utils import get_sd_run_from_dict, sd_bee_stop_callback
import os 
from PIL import Image
from stable_diffusion.sd_run import SDRun 
from dataclasses import fields
import random
from .options import options

class InterpolatorHelperPlugin(BasePlugin):
    def hook_post_prepare_init_latent(self, sd_run):
        if self.parent.do_interpolate:
            sd_run.init_latent = self.parent.latent_a * self.parent.frac_a_latent + self.parent.latent_b * self.parent.frac_b_latent
            sd_run.latent = sd_run.init_latent
        elif self.parent.save_a:
            self.parent.latent_a = np.copy(sd_run.init_latent)
        elif self.parent.save_b:
            self.parent.latent_b = np.copy(sd_run.init_latent)
        else:
            raise ValueError("Err in hook_post_prepare_init_latent for interpolate")
    
    def hook_post_generate_text_emb(self, sd_run):
        if self.parent.do_interpolate:
            sd_run.context = self.parent.context_a *  self.parent.frac_a_context  +  self.parent.context_b * self.parent.frac_b_context
        elif self.parent.save_a:
            self.parent.context_a = np.copy(sd_run.context)
        elif self.parent.save_b:
            self.parent.context_b = np.copy(sd_run.context)



class FrameInterpolator(AppletBase):

    applet_name = "frame_interpolate"
    applet_title = "Interpolator"
    applet_description = "Generate videos by interpolating prompts and seeds"
    is_stop_avail = True
    applet_icon_fname = "interpolate.gif"

    def get_input_form(self):

        my_el = [
            get_textbox("num_frames", type="int" ,  default=40,  title="Number of frames" , description="The number of frames you want in the video."),

            get_textbox("seed1", type="int" ,    title="Start Seed" , description="The seed from which it will start the video."), 
            get_textarea("prompt1", title="Start Prompt" , description="The prompt from which it will start the video."),
            
            get_textbox("seed2", type="int" ,    title="End Seed" , description="The seed to which it will end the video. Keep it same as start seed if you dont want to change the seed in the video."), 
            get_textarea("prompt2", title="End Prompt" , description="The prompt to which it will end the video. Keep it same as start prompt if you dont want to change the prompt in the video."),

            get_output_text("The following options will remain constant in the whole video:")
        ]

        form =  json.loads(options)
        form = [f for f in form if not f['id'] in [ 'controlnet_acc' , 'seed_acc' , 'seed_desc' , 'prompt',  'num_imgs_desc']]
        return my_el +  form
    
    def update_progress(self , n_img_done, n_total, cur_img=None):
        oo = [get_output_text(f"Rendering... \n\n Rendered {n_img_done} out of {n_total} images.")] 
        if cur_img is not None:
            if type(cur_img) is not str:
                fn = "/tmp/" + str(random.randint(0,10000)) + ".jpg"
                cur_img = cur_img.resize( [ s//2 for s in cur_img.size] )
                cur_img = cur_img.save(fn)
            oo.append(get_output_text("Current frame:"))
            oo.append(get_output_img(fn))
        self.update_state("outputs" , oo )
    
    def stopped(self):
        oo = [get_output_text(f"Stopped")] 
        self.update_state("outputs" , oo )

    def run(self , params ):

        if "num_frames" not in params or params['num_frames'] < 3:
            raise ValueError("Enter a valid number of frames")
        n_total = int(params['num_frames'])
        
        if "seed1" not in params or params['seed1'] < 1:
            raise ValueError("Enter a valid start seed")
        seed1 = int(params['seed1'])
        
        if "seed2" not in params or params['seed2'] < 1:
            raise ValueError("Enter a valid end seed")
        seed2 = int(params['seed2'])
        
        if "prompt1" not in params or len(params['prompt1']) < 5:
            raise ValueError("Enter a valid start prompt")
        prompt1 = str(params['prompt1'])

        if "prompt2" not in params or len(params['prompt2']) < 5:
            raise ValueError("Enter a valid end prompt")
        prompt2 = str(params['prompt2'])
        

        # params = json.dumps(params)
        params = copy.deepcopy(params)

        generator = StableDiffusion( self.model_container , ModelInterface , None , model_name=None, callback=sd_bee_stop_callback )
        generator.add_plugin(InterpolatorHelperPlugin)

        rendered_imgs = []
        
        generator.do_interpolate = False
        generator.save_a = True
        generator.save_b = False
        params['seed'] = seed1
        params['prompt'] = prompt1
        sd_run = get_sd_run_from_dict(params)

        self.update_progress(0 , n_total)
        img = generator.generate(sd_run)
        if img is None:
            return self.stopped()
        img = Image.fromarray(img['img'][0]) 
        rendered_imgs.append(img)
        self.update_progress(1 , n_total, rendered_imgs[-1])

        generator.do_interpolate = False
        generator.save_b = True
        generator.save_a = False
        params['seed'] = seed2
        params['prompt'] = prompt2
        sd_run = get_sd_run_from_dict(params)
        
        img = generator.generate(sd_run)
        if img is None:
            return self.stopped()
        im_end = Image.fromarray(img['img'][0]) 
        self.update_progress(2 , n_total, rendered_imgs[-1])

        N = n_total - 1

        for i in range(1 , N):
            frac = float(i) / N
            generator.do_interpolate = True 
            generator.interpolate_frac = frac
            # generator.frac_a = np.cos( generator.interpolate_frac * np.pi / 2 )
            # generator.frac_b = np.sin( generator.interpolate_frac * np.pi / 2 )
            if seed1 != seed2:
                generator.frac_a_latent = np.sqrt(1 - frac )
                generator.frac_b_latent  = np.sqrt( frac )
            else:
                generator.frac_a_latent = 0.5
                generator.frac_b_latent = 0.5

            generator.frac_a_context = (1 - frac )
            generator.frac_b_context  =  ( frac )

            sd_run = get_sd_run_from_dict(params)
            img = generator.generate(sd_run)
            if img is None:
                return self.stopped()
            img = Image.fromarray(img['img'][0]) 
            rendered_imgs.append(img)
            self.update_progress(2+i , n_total, rendered_imgs[-1])

        rendered_imgs.append(im_end)    

        fn = "/tmp/" + str(random.randint(0,10000)) + ".gif"
        rendered_imgs[0].save(fn, format='GIF', append_images=rendered_imgs[1:] , save_all=True , loop=0)
        self.update_state("outputs" , [get_output_img(fn , save_ext='.gif' , is_save=True)] )

    
        

        




