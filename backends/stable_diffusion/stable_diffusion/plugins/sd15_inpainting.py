from .base_plugin import BasePlugin
import numpy as np
import cv2

class Sd15Inpainting(BasePlugin):

    def hook_pre_generate(self, sd_run):
        if sd_run.is_sd15_inpaint:
            assert (sd_run.input_image_path is not None and sd_run.input_image_path != "") , "No input image specified"
            # if sd_run.mode != "txt2img":
            #     raise ValueError("SD15 Inpaint can only run in txt2img mode")
            if (not sd_run.get_mask_from_image_alpha) and (sd_run.mask_image_path is None or sd_run.mask_image_path == ""):
                raise ValueError("With SD15, the mask should be present")
            
            
                
    
    def hook_post_prepare_init_latent(self, sd_run):
        if sd_run.is_sd15_inpaint:
            masked_img  = sd_run.input_image_processed * (sd_run.processed_mask > 0.5 )
            sd_run.encoded_masked_img = self.parent.get_encoded_img(sd_run , masked_img)

            assert sd_run.processed_mask_downscaled.shape[0] == 1, "batch_size > 1 not supported "

            if sd_run.do_masking_diffusion:
                sd_run.encoded_img_orig = np.copy(sd_run.encoded_masked_img)
            
         

    def hook_mid_get_unet_out(self, sd_run):
        if sd_run.is_sd15_inpaint:
            sd_run.latent_model_input = np.concatenate([
                sd_run.latent_model_input , 
                np.repeat( (1 - sd_run.processed_mask_downscaled ), sd_run.batch_size , axis=0) , 
                sd_run.encoded_masked_img 
            ], axis=-1) #TODO verify if we have to concat before or after prescale