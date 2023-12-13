


import tensorflow as tf
from autoencoder_kl import Decoder, Encoder
from diffusion_model import UNetModel , UNetModelV2
from clip_encoder import CLIPTextTransformer
from clip_encoder_v2 import CLIPTextTransformerV2
from controlnet import ControlNet, HintNet

from mapping_constants import PYTORCH_CKPT_MAPPING , PYTORCH_CKPT_MAPPING_SD2

import json

MAX_TEXT_LEN = 77
import numpy as np

def get_models(n_unet_ch=4 , is_sd2=False ):

    img_height=512
    img_width=512

    n_h = img_height // 8
    n_w = img_width // 8

    # Create text encoder
    input_word_ids = tf.keras.layers.Input(shape=(MAX_TEXT_LEN,), dtype="int32")
    input_pos_ids = tf.keras.layers.Input(shape=(MAX_TEXT_LEN,), dtype="int32")
    if is_sd2:
        text_encoder_f = CLIPTextTransformerV2()
    else:
        text_encoder_f = CLIPTextTransformer()
    embeds = text_encoder_f([input_word_ids, input_pos_ids])
    text_encoder = tf.keras.models.Model([input_word_ids, input_pos_ids], embeds)

    # Creation diffusion UNet
    if is_sd2:
        context = tf.keras.layers.Input((MAX_TEXT_LEN, 1024))
    else:
        context = tf.keras.layers.Input((MAX_TEXT_LEN, 768))
    t_emb = tf.keras.layers.Input((320,))
  
    latent = tf.keras.layers.Input((n_h, n_w, n_unet_ch))

    if is_sd2:
        unet = UNetModelV2()
    else:
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


def get_controlnet_models():
    context = tf.keras.layers.Input((MAX_TEXT_LEN, 768))
    t_emb = tf.keras.layers.Input((320,))
    latent = tf.keras.layers.Input((64, 64, 4))
    hint_x = tf.keras.layers.Input((64, 64, 320))


    hint_img = tf.keras.layers.Input((512, 512, 3))

    controlnet_f = ControlNet()
    hintnet_f = HintNet()

    inps = [latent, t_emb, context, hint_x]
    controlnet_model = tf.keras.models.Model(
        inps, controlnet_f(inps)
    )

    hintnet_model = tf.keras.models.Model(
        hint_img, hintnet_f(hint_img)
    )

    return hintnet_model , controlnet_model , hintnet_f , controlnet_f


def load_from_tdict(inp_file , models , is_sd2=False ):
    inp_file.init_read()

    if is_sd2:
        mappings_to_use = PYTORCH_CKPT_MAPPING_SD2
    else:
        mappings_to_use = PYTORCH_CKPT_MAPPING

    for module_name in models.keys():
        module_weights = []
        for i , (key , perm ) in enumerate(mappings_to_use[module_name]):
            w = inp_file.read_key(key)

            if perm is not None:
                w = np.transpose(w , perm )
            module_weights.append(w)
        models[module_name].set_weights(module_weights)
        print("Loaded %d weights for %s"%(len(module_weights) , module_name))
    inp_file.finish_read()



class ModelInterface:

    default_float_type = 'float32'
    avail_float_types = ['float32']
    avail_models = ["sd_1x" , "sd_2x" , "sd_1x_inpaint" ,  "sd_1x_controlnet"]

    def __init__(self, tdict,  dtype='float16', model_name="sd_1x", second_tdict=None ):

        print("initing " , model_name)

        self.is_control_net = False 
        self.is_sd2 = False

        if model_name == "sd_1x":
            n_unet_ch = 4
        elif model_name == "sd_2x":
            n_unet_ch = 4
            self.is_sd2 = True
        elif model_name == "sd_1x_inpaint":
            n_unet_ch = 9
        elif model_name == "sd_1x_controlnet":
            assert second_tdict is not None
            n_unet_ch = 4
            self.is_control_net = True
        else:
            raise ValueError("invalid model name")

        text_encoder, diffusion_model, decoder, encoder , text_encoder_f , diffusion_model_f , decoder_f , encoder_f = get_models( n_unet_ch=n_unet_ch , is_sd2=self.is_sd2  )
        self.text_encoder = text_encoder
        self.diffusion_model = diffusion_model
        self.decoder = decoder
        self.encoder = encoder
        self.text_encoder_f = text_encoder_f
        self.diffusion_model_f = diffusion_model_f 
        self.decoder_f = decoder_f
        self.encoder_f = encoder_f

        if self.is_control_net:
            hintnet_model , controlnet_model , hintnet_f , controlnet_f = get_controlnet_models()
            self.hintnet_f = hintnet_f
            self.controlnet_f = controlnet_f
            self.controlnet = controlnet_model
            self.hintnet = hintnet_model

        self.load_from_tdict(tdict, second_tdict=second_tdict)


    def run_unet(self, time_emb, text_emb, unet_inp, control_inp=None,  control_weight=1, fixed_vector=None  ):
        time_emb = np.array(time_emb).astype('float32')
        text_emb = np.array(text_emb).astype('float32')
        unet_inp = np.array(unet_inp).astype('float32')
        inps = [unet_inp, time_emb, text_emb]
        assert fixed_vector is None, "Fixed vector not supported"
        assert control_weight == 1 or control_weight == 1.0 , "Control weight not supported"
        if control_inp is not None:
            inps = inps + [ np.array(c).astype('float32') for c in control_inp ]
        return np.array(self.diffusion_model_f(inps ))

    def run_controlnet(self, time_emb, text_emb, unet_inp, hint_img ):
        time_emb = np.array(time_emb).astype('float32')
        text_emb = np.array(text_emb).astype('float32')
        unet_inp = np.array(unet_inp).astype('float32')
        hint_img = np.array(hint_img).astype('float32')

        hint_x = self.hintnet_f(hint_img)
        controls = self.controlnet_f([unet_inp, time_emb, text_emb, hint_x])

        return [ np.array(c) for c in controls]

        
    def run_dec(self, unet_out):
        unet_out = np.array(unet_out).astype('float32')
        return np.array(self.decoder_f(unet_out))

    def run_text_enc(self, tokens, pos_ids):
        o =  np.array(self.text_encoder_f([tokens , pos_ids]))
        return o

    def run_enc(self, inp):
        inp = np.array(inp).astype('float32')
        return np.array(self.encoder_f(inp))

    def destroy(self):
        del self.text_encoder
        del self.diffusion_model
        del self.decoder
        del self.encoder
        del self.text_encoder_f 
        del self.diffusion_model_f 
        del self.decoder_f
        del self.encoder_f

        if self.is_control_net:
            del self.hintnet_f 
            del self.controlnet_f 
            del self.controlnet
            del self.hintnet 


    def load_from_tdict(self, tdict, second_tdict=None):

        if self.is_control_net:
            assert second_tdict is not None
            load_from_tdict(second_tdict , {
                'controlnet' : self.controlnet, 
                'hintnet' : self.hintnet
            }  , is_sd2=self.is_sd2 )

        load_from_tdict(tdict , {
            'text_encoder' : self.text_encoder, 
            'diffusion_model' : self.diffusion_model , 
            'decoder' : self.decoder , 
            'encoder' : self.encoder 
        } , is_sd2=self.is_sd2)


