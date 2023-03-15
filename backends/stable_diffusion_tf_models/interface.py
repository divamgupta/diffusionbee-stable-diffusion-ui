


import tensorflow as tf
from autoencoder_kl import Decoder, Encoder
from diffusion_model import UNetModel
from clip_encoder import CLIPTextTransformer

from mapping_constants import PYTORCH_CKPT_MAPPING

import json

MAX_TEXT_LEN = 77
import numpy as np

def get_models(n_unet_ch=4 ):

    img_height=512
    img_width=512

    n_h = img_height // 8
    n_w = img_width // 8

    # Create text encoder
    input_word_ids = tf.keras.layers.Input(shape=(MAX_TEXT_LEN,), dtype="int32")
    input_pos_ids = tf.keras.layers.Input(shape=(MAX_TEXT_LEN,), dtype="int32")
    text_encoder_f = CLIPTextTransformer()
    embeds = text_encoder_f([input_word_ids, input_pos_ids])
    text_encoder = tf.keras.models.Model([input_word_ids, input_pos_ids], embeds)

    # Creation diffusion UNet
    context = tf.keras.layers.Input((MAX_TEXT_LEN, 768))
    t_emb = tf.keras.layers.Input((320,))
  
    latent = tf.keras.layers.Input((n_h, n_w, n_unet_ch))
    unet = UNetModel()
    diffusion_model_f = unet
    diffusion_model = tf.keras.models.Model(
        [latent, t_emb, context], unet([latent, t_emb, context])
    )

    # Create decoder
    latent = tf.keras.layers.Input((n_h, n_w, 4))
    decoder = Decoder()
    decoder_f = decoder
    decoder = tf.keras.models.Model(latent, decoder(latent))

    inp_img = tf.keras.layers.Input((img_height, img_width, 3))
    encoder_f = Encoder()
    encoder = tf.keras.models.Model(inp_img, encoder_f(inp_img))

    
    return text_encoder, diffusion_model, decoder, encoder , text_encoder_f , diffusion_model_f , decoder_f , encoder_f




class ModelInterface:

    default_float_type = 'float32'

    def __init__(self, tdict,  dtype='float16', model_name="sd_1x"):

        if model_name == "sd_1x":
            n_unet_ch = 4
        elif model_name == "sd_1x_inpaint":
            n_unet_ch = 9
        else:
            raise ValueError("invalid model name")



        text_encoder, diffusion_model, decoder, encoder , text_encoder_f , diffusion_model_f , decoder_f , encoder_f = get_models( n_unet_ch=n_unet_ch )
        self.text_encoder = text_encoder
        self.diffusion_model = diffusion_model
        self.decoder = decoder
        self.encoder = encoder
        self.text_encoder_f = text_encoder_f
        self.diffusion_model_f = diffusion_model_f 
        self.decoder_f = decoder_f
        self.encoder_f = encoder_f

        self.load_from_tdict(tdict)


    def run_unet(self, time_emb, text_emb, unet_inp):
        time_emb = np.array(time_emb).astype('float32')
        text_emb = np.array(text_emb).astype('float32')
        unet_inp = np.array(unet_inp).astype('float32')
        return np.array(self.diffusion_model_f([unet_inp, time_emb, text_emb]))
        
    def run_dec(self, unet_out):
        unet_out = np.array(unet_out).astype('float32')
        return np.array(self.decoder_f(unet_out))

    def run_text_enc(self, tokens, pos_ids):
        return np.array(self.text_encoder_f([tokens , pos_ids]))

    def run_enc(self, inp):
        inp = np.array(inp).astype('float32')
        return np.array(self.encoder_f(inp))

    def destroy(self):
        pass

    def load_from_tdict(self, tdict):
        inp_file = tdict
        inp_file.init_read()


        for module_name in ['text_encoder', 'diffusion_model', 'decoder', 'encoder' ]:
            module_weights = []
            for i , (key , perm ) in enumerate(PYTORCH_CKPT_MAPPING[module_name]):
                
                w = inp_file.read_key(key)

                if perm is not None:
                    w = np.transpose(w , perm )
                module_weights.append(w)
            getattr(self, module_name).set_weights(module_weights)
            print("Loaded %d weights for %s"%(len(module_weights) , module_name))
        inp_file.finish_read()