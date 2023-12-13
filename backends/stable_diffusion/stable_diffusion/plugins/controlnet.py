import os
import functools

from ..control_processors.process_body_pose import process_image_body_pose
from ..control_processors.process_midas_depth import process_image_midas_depth
from ..control_processors.process_lineart import process_image_lineart


from ..utils.image_preprocess import process_inp_img
from ..utils.logging import log_object

from .base_plugin import BasePlugin

import numpy as np




def get_preprocess_function(preprocess_function_name , model_path ):
    if preprocess_function_name == "body_pose":
        return functools.partial(process_image_body_pose, model_path=model_path)
    elif preprocess_function_name == "midas_depth":
        return functools.partial(process_image_midas_depth, model_path=model_path)
    elif preprocess_function_name == "line_art":
        return functools.partial(process_image_lineart, model_path=model_path)

    else:
        raise ValueError("invalid function name")



class ControlNetPlugin(BasePlugin):
    
    def hook_pre_generate(self, sd_run):

        if sd_run.controlnet_model is not None and sd_run.controlnet_model != "" and  sd_run.controlnet_model != "None":
            if "sd_1x_controlnet" not in self.parent.ModelInterfaceClass.avail_models:
                raise ValueError("ControlNet is not supported in this version. Please upgrade.") 
            sd_run.is_control_net = True
            sd_run.second_tdict_path = sd_run.controlnet_tdict_path
            assert sd_run.controlnet_input_image_path is not None and sd_run.controlnet_input_image_path != ""

            if sd_run.do_controlnet_preprocess:
                if sd_run.controlnet_model == "Depth":                    
                    sd_run.controlnet_inp_img_preprocesser = "midas_depth"
                elif sd_run.controlnet_model == "BodyPose":
                    sd_run.controlnet_inp_img_preprocesser = "body_pose"
                elif sd_run.controlnet_model == "LineArt":
                    sd_run.controlnet_inp_img_preprocesser = "line_art"
                else:
                    raise ValueError("Generate control not supported for " +  sd_run.controlnet_model )

        if sd_run.is_control_net:
            assert ( sd_run.controlnet_input_image_path is not None and sd_run.controlnet_input_image_path != "" ) , "ControlNet Input Missing"

        if sd_run.controlnet_inp_img_preprocesser is not None and not sd_run.is_control_net:
            raise ValueError("Enexpected ControlNet Input preprocessor")
        
        if sd_run.do_controlnet_preprocess:
            sd_run.controlnet_inp_img_preprocesser

        
    def hook_post_generate(self, sd_run):
        if (sd_run.controlnet_inp_img_preprocesser is not None) and  (sd_run.controlnet_model != "Inpaint"):
            sd_run.ret['aux_img'] = sd_run.controlnet_input_image_path

    def hook_post_process_inp_imgs(self, sd_run):
        # process control net images 
        if (sd_run.controlnet_inp_img_preprocesser is not None) and (sd_run.controlnet_model != "Inpaint")  : #if you want to preprocess input image, but for inpaint no need to save the control file
            outfname = sd_run.controlnet_input_image_path + ".controlnet_processed_" + sd_run.controlnet_inp_img_preprocesser  + ".jpg"
            if not os.path.exists(outfname):
                preprocess_function = get_preprocess_function(sd_run.controlnet_inp_img_preprocesser, sd_run.controlnet_inp_img_preprocesser_model_path)
                preprocess_function(inp_fname=sd_run.controlnet_input_image_path , out_fname=outfname)
                assert os.path.exists(outfname)
            sd_run.controlnet_input_image_path = outfname

        if sd_run.controlnet_input_image_path is not None and sd_run.controlnet_input_image_path != "" and (sd_run.controlnet_model != "Inpaint"): 
            
            _, _, sd_run.controlnet_input_image_processed , _ = process_inp_img(sd_run.controlnet_input_image_path , image_size=None, new_w=sd_run.img_width , new_h=sd_run.img_height )
            sd_run.controlnet_input_image_processed = sd_run.controlnet_input_image_processed[None]

        # special case for inpaint preprocess
        if (sd_run.controlnet_inp_img_preprocesser is not None) and (sd_run.controlnet_model == "Inpaint"):
            # hhere mask is the control image, but we also need input image 

            sd_run.encoded_img_orig = np.copy(self.parent.get_encoded_img(sd_run , sd_run.input_image_processed ))
            mmm = (sd_run.processed_mask < 0.5 )[0]
            mmm = np.repeat(mmm , 3 , 2 )
            inpp = np.copy(sd_run.input_image_processed[0])
            inpp[mmm] = -3
            sd_run.controlnet_input_image_processed = inpp[None]



    def hook_mid_get_unet_out(self, sd_run):
        if sd_run.is_control_net:
            hint_img = (sd_run.controlnet_input_image_processed+1)/2

            if self.parent.debug_output_path is not None:
                log_object(hint_img , self.parent.debug_output_path  , "hint_img")

            if sd_run.combine_unet_run:
                hint_img = np.repeat(hint_img, sd_run.batch_size, axis=0)
            sd_run.controls = self.parent.model.run_controlnet(unet_inp=sd_run.latent_model_input, time_emb=sd_run.t_emb, text_emb=sd_run.context, hint_img=hint_img )
            iter_i = self.parent.t_to_i(sd_run.current_t)
            iter_frac = iter_i / sd_run.num_steps
            
            sd_run.control_weight_current_uncond = sd_run.control_weight
            sd_run.control_weight_current_cond = sd_run.control_weight

            if sd_run.controlnet_guess_mode:
                sd_run.control_weight_current_uncond = 0

            if self.parent.debug_output_path is not None:
                log_object(sd_run.controls  , self.parent.debug_output_path  , key="sd_run.controls")
        else:
            sd_run.controls = None