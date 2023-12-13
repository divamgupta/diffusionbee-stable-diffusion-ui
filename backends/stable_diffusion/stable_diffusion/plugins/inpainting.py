from .base_plugin import BasePlugin
import numpy as np
from ..utils.image_preprocess import process_inp_img , post_process_mask
import cv2

class MaskInpainting(BasePlugin):


    def hook_pre_generate(self, sd_run):
        if sd_run.mode == "img2img"  :
            if sd_run.mask_image_path is not None and sd_run.mask_image_path != "" or sd_run.get_mask_from_image_alpha:
                sd_run.do_masking_diffusion = True


    def hook_post_process_inp_imgs(self, sd_run):
        if (sd_run.mask_image_path is not None and sd_run.mask_image_path != "") or (sd_run.get_mask_from_image_alpha):
            
            mask_image = None 

            if sd_run.mask_image_path is not None and sd_run.mask_image_path != "":
                h , w , mask_image , _ = process_inp_img(sd_run.mask_image_path ,  image_size=sd_run.inp_image_resize_mode , new_w=sd_run.img_width , new_h=sd_run.img_height  )

            if sd_run.get_mask_from_image_alpha:
                h , w , mask_image_alp , _ = process_inp_img(sd_run.input_image_path , only_read_alpha=True ,  image_size=sd_run.inp_image_resize_mode , new_w=sd_run.img_width , new_h=sd_run.img_height  )

                if mask_image is None:
                    mask_image = mask_image_alp
                else:
                    mask_image = np.maximum(mask_image , mask_image_alp)
                
            assert mask_image is not None
            assert h == sd_run.img_height , "Mask should be of the same size as inp image"
            assert w == sd_run.img_width , "Mask should be of the same size as inp image"
            mask_image = (mask_image + 1 )/2 

            if sd_run.get_mask_from_image_alpha:
                mask_image = cv2.dilate(mask_image, np.ones((20, 20), np.uint8))
            mask_image[mask_image < 0.5] = 0
            mask_image[mask_image >= 0.5] = 1
           
            
            if sd_run.blur_mask:
                oo = (mask_image*255).astype('uint8')
                oo = cv2.dilate(oo, np.ones((10, 10), np.uint8)) 
                oo = cv2.blur( oo  ,(10,10))
                mask_image = oo.astype('float32')/255
                                                   
            mask_image = 1 - mask_image # repaint white keep black
            mask_image = np.copy(mask_image[... , :1 ])
            
            if sd_run.do_masking_diffusion or True:
                mask_image_sm = cv2.resize(mask_image , (mask_image.shape[1]//8 , mask_image.shape[0]//8) )[: , : , None]
            else:
                mask_image_sm = np.copy(mask_image[::8 , ::8])

            mask_image = mask_image[None]
            mask_image_sm = mask_image_sm[None]

            if not sd_run.do_masking_diffusion:
                mask_image[mask_image < 0.5] = 0
                mask_image[mask_image >= 0.5] = 1

            mask_image_sm[mask_image_sm < 0.5] = 0
            mask_image_sm[mask_image_sm >= 0.5] = 1

            sd_run.processed_mask_downscaled = mask_image_sm
            sd_run.processed_mask = mask_image
    
    def hook_post_get_next_latent(self, sd_run):
        
        if sd_run.do_masking_diffusion:

            latent_proper = np.copy(sd_run.encoded_img_orig)

            noise = self.parent.get_modded_noise(sd_run.seed , latent_proper.shape , seed_type=sd_run.seed_type, small_mod_seed=sd_run.small_mod_seed  )
            latent_proper = self.parent.scheduler.add_noise(latent_proper, noise, np.array([self.parent.t_to_i(sd_run.current_t)] * sd_run.batch_size, dtype=np.int64 ) )

            sd_run.next_latents = (latent_proper  * sd_run.processed_mask_downscaled) + (sd_run.next_latents * (1 - sd_run.processed_mask_downscaled))
    
    def hook_mid_decode(self, sd_run):
        if sd_run.do_masking_diffusion:
            sd_run.decoded = (sd_run.input_image_processed  * sd_run.processed_mask) + (sd_run.decoded * (1 - sd_run.processed_mask ))

