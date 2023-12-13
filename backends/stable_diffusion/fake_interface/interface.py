
import numpy as np
import time 

class ModelInterface:
    default_float_type = 'float32'
    avail_float_types = ['float32']
    avail_models = ["sd_1x" , "sd_2x" , "sd_1x_inpaint" ,  "sd_1x_controlnet"]

    def __init__(self, tdict,  dtype='float16', model_name="sd_1x", second_tdict=None ):
        pass

    def run_unet(self, time_emb, text_emb, unet_inp, control_inp=None,  control_weight=1):
        time.sleep(1.4)
        return np.copy(unet_inp)

    def run_controlnet(self, time_emb, text_emb, unet_inp, hint_img ):
        time.sleep(0.4)
        return np.array([42])

    def run_dec(self, unet_out):
        time.sleep(1.4)
        return np.zeros((unet_out.shape[0] , unet_out.shape[1]*8 , unet_out.shape[2]*8 , unet_out.shape[3])) 

    def run_text_enc(self, tokens, pos_ids):
        time.sleep(1.4)
        return np.zeros((tokens.shape[0] , 77 , 768)) 

    def run_enc(self, inp):
        time.sleep(1.4)
        return np.zeros((unet_out.shape[0] , unet_out.shape[1]//8 , unet_out.shape[2]//8 , unet_out.shape[3]))  

    def destroy(self):
        pass

    def load_from_tdict(self, tdict_path):
        pass
