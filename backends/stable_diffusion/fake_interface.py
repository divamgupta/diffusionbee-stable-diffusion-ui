
import numpy as np
import time 

class ModelInterface:
    default_float_type = 'float16'

    def __init__(self , *args , **k ):
        pass

    def run_unet(self, time_emb, text_emb, unet_inp):
        time.sleep(1.4)
        return np.copy(unet_inp)

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
