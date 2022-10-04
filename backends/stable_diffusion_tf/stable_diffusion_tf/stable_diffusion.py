import numpy as np
from tqdm import tqdm
import math
import time
import tensorflow as tf

from .autoencoder_kl import Decoder, Encoder
from .diffusion_model import UNetModel
from .clip_encoder import CLIPTextTransformer
from .clip_tokenizer import SimpleTokenizer
from .constants import _UNCONDITIONAL_TOKENS, _ALPHAS_CUMPROD
from .stdin_input import is_avail, get_input
from PIL import Image, ImageOps
MAX_TEXT_LEN = 77

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

    input_image = ImageOps.fit(input_image, (new_w, new_h), method = Image.BILINEAR ,
                   bleed = 0.0, centering =(0.5, 0.5))
    input_image = np.array(input_image)[... , :3]
    input_image = (input_image.astype("float") / 255.0)*2 - 1 
    return new_h , new_w  , input_image


class StableDiffusion:
    def __init__(self, img_height=1000, img_width=1000, jit_compile=False, download_weights=True):
        self.img_height = img_height
        self.img_width = img_width
        self.tokenizer = SimpleTokenizer()

        text_encoder, diffusion_model, decoder, encoder , text_encoder_f , diffusion_model_f , decoder_f , encoder_f = get_models(img_height, img_width, download_weights=download_weights)
        self.text_encoder = text_encoder
        self.diffusion_model = diffusion_model
        self.decoder = decoder
        self.encoder = encoder
        self.text_encoder_f = text_encoder_f
        self.diffusion_model_f = diffusion_model_f 
        self.decoder_f = decoder_f
        self.encoder_f = encoder_f
        if jit_compile:
            assert False
            self.text_encoder.compile(jit_compile=True)
            self.diffusion_model.compile(jit_compile=True)
            self.decoder.compile(jit_compile=True)

    def generate(
        self,
        prompt, 
        img_height, img_width,
        batch_size=1,
        num_steps=25,
        unconditional_guidance_scale=7.5,
        temperature=1,
        seed=None,
        img_id=0,
        input_image=None,
        input_image_strength=0.5,
    ):

        if type(input_image) is str:
            img_height, img_width, input_image = process_inp_img(input_image)
        
        if self.img_height == img_height and self.img_width == img_width:
            self.use_eager = False
        else:
            self.use_eager = True

        try:
            seed = int(seed)
            if seed < 1:
                seed = int(time.time()*100)%1002487 
        except:
            pass

        if seed is None:
            seed = int(time.time()*100)%1002487
        
        seed = seed + 1234*img_id
        # Tokenize prompt (i.e. starting context)
        inputs = self.tokenizer.encode(prompt)
        assert len(inputs) < 77, "Prompt is too long!"
        phrase = inputs + [49407] * (77 - len(inputs))
        phrase = np.array(phrase)[None].astype("int32")
        phrase = np.repeat(phrase, batch_size, axis=0)

        # Encode prompt tokens (and their positions) into a "context vector"
        pos_ids = np.array(list(range(77)))[None].astype("int32")
        pos_ids = np.repeat(pos_ids, batch_size, axis=0)

        if self.use_eager:
            context = self.text_encoder_f([phrase, pos_ids])
        else:
            context = self.text_encoder.predict_on_batch([phrase, pos_ids])

        

        # Encode unconditional tokens (and their positions into an
        # "unconditional context vector"
        unconditional_tokens = np.array(_UNCONDITIONAL_TOKENS)[None].astype("int32")
        unconditional_tokens = np.repeat(unconditional_tokens, batch_size, axis=0)
        self.unconditional_tokens = tf.convert_to_tensor(unconditional_tokens)

        if self.use_eager:
            unconditional_context = self.text_encoder_f(
                [self.unconditional_tokens, pos_ids]
            )
        else:
            unconditional_context = self.text_encoder.predict_on_batch(
                [self.unconditional_tokens, pos_ids]
            )
        timesteps = np.arange(1, 1000, 1000 // num_steps)
        input_img_noise_t = timesteps[ int(len(timesteps)*input_image_strength) ]
        latent, alphas, alphas_prev = self.get_starting_parameters(
            img_height, img_width , timesteps, batch_size, seed , input_image=input_image, input_img_noise_t=input_img_noise_t
        )

        if input_image is not None:
            timesteps = timesteps[: int(len(timesteps)*input_image_strength)]

        # Diffusion stage
        ii = 0
        progbar = tqdm(list(enumerate(timesteps))[::-1])
        for index, timestep in progbar:

            if is_avail():
                if "__stop__" in get_input():
                    return None

            progbar.set_description(f"{index:3d} {timestep:3d}")
            percentage = 100*ii/len(timesteps)
            ii += 1
            print("sdbk dnpr "+str(percentage) ) # done percentage 
            e_t = self.get_model_output(
                latent,
                timestep,
                context,
                unconditional_context,
                unconditional_guidance_scale,
                batch_size,
            )
            a_t, a_prev = alphas[index], alphas_prev[index]
            latent, pred_x0 = self.get_x_prev_and_pred_x0(
                latent, e_t, index, a_t, a_prev, temperature, seed + index
            )

        # Decoding stage
        if self.use_eager:
            decoded = self.decoder_f(latent)
        else:
            decoded = self.decoder.predict_on_batch(latent)
        decoded = ((decoded + 1) / 2) * 255
        return np.clip(decoded, 0, 255).astype("uint8")

    def add_noise(self, x , t , seed ):
        batch_size,w,h = x.shape[0] , x.shape[1] , x.shape[2]
        noise = np.random.RandomState(seed).normal(size=(batch_size, w, h, 4)).astype('float32')
        sqrt_alpha_prod = _ALPHAS_CUMPROD[t] ** 0.5
        sqrt_one_minus_alpha_prod = (1 - _ALPHAS_CUMPROD[t]) ** 0.5

        return  sqrt_alpha_prod * x + sqrt_one_minus_alpha_prod * noise

    def timestep_embedding(self, timesteps, dim=320, max_period=10000):
        half = dim // 2
        freqs = np.exp(
            -math.log(max_period) * np.arange(0, half, dtype="float32") / half
        )
        args = np.array(timesteps) * freqs
        embedding = np.concatenate([np.cos(args), np.sin(args)])
        return tf.convert_to_tensor(embedding.reshape(1, -1))

    def get_model_output(
        self,
        latent,
        t,
        context,
        unconditional_context,
        unconditional_guidance_scale,
        batch_size,
    ):
        timesteps = np.array([t])
        t_emb = self.timestep_embedding(timesteps)
        t_emb = np.repeat(t_emb, batch_size, axis=0)

        if self.use_eager:
            unconditional_latent = self.diffusion_model_f(
                [latent, t_emb, unconditional_context]
            )
            latent = self.diffusion_model_f([latent, t_emb, context])
        else:
            unconditional_latent = self.diffusion_model.predict_on_batch(
                [latent, t_emb, unconditional_context]
            )
            latent = self.diffusion_model.predict_on_batch([latent, t_emb, context])
        return unconditional_latent + unconditional_guidance_scale * (
            latent - unconditional_latent
        )

    def get_x_prev_and_pred_x0(self, x, e_t, index, a_t, a_prev, temperature, seed):
        sigma_t = 0
        sqrt_one_minus_at = math.sqrt(1 - a_t)
        pred_x0 = (x - sqrt_one_minus_at * e_t) / math.sqrt(a_t)

        # Direction pointing to x_t
        dir_xt = math.sqrt(1.0 - a_prev - sigma_t**2) * e_t

        ll_np = np.random.RandomState(seed).normal(size=x.shape).astype('float32')
        ll = tf.convert_to_tensor(ll_np)

        noise = sigma_t * ll * temperature
        x_prev = math.sqrt(a_prev) * pred_x0 + dir_xt
        return x_prev, pred_x0

    def get_starting_parameters(self, img_height, img_width , timesteps, batch_size, seed, input_image=None, input_img_noise_t=None):
        n_h = img_height // 8
        n_w = img_width // 8
        alphas = [_ALPHAS_CUMPROD[t] for t in timesteps]
        alphas_prev = [1.0] + alphas[:-1]

        if input_image is None:
            latent_np = np.random.RandomState(seed).normal(size=(batch_size, n_h, n_w, 4)).astype('float32')
            latent = tf.convert_to_tensor(latent_np)
        else:
            latent = self.encoder_f(input_image[None])
            latent = self.add_noise(latent, input_img_noise_t, seed)
            latent = tf.repeat(latent , batch_size , axis=0)

        
        # latent = tf.random.normal((batch_size, n_h, n_w, 4), seed=seed)
        return latent, alphas, alphas_prev


def get_models(img_height, img_width, download_weights=True):
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
    latent = tf.keras.layers.Input((n_h, n_w, 4))
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

    
    if download_weights:
        assert False
        text_encoder_weights_fpath = tf.keras.utils.get_file(
            origin="https://huggingface.co/fchollet/stable-diffusion/resolve/main/text_encoder.h5",
            file_hash="d7805118aeb156fc1d39e38a9a082b05501e2af8c8fbdc1753c9cb85212d6619",
        )
        diffusion_model_weights_fpath = tf.keras.utils.get_file(
            origin="https://huggingface.co/fchollet/stable-diffusion/resolve/main/diffusion_model.h5",
            file_hash="a5b2eea58365b18b40caee689a2e5d00f4c31dbcb4e1d58a9cf1071f55bbbd3a",
        )
        decoder_weights_fpath = tf.keras.utils.get_file(
            origin="https://huggingface.co/fchollet/stable-diffusion/resolve/main/decoder.h5",
            file_hash="6d3c5ba91d5cc2b134da881aaa157b2d2adc648e5625560e3ed199561d0e39d5",
        )



        text_encoder.load_weights(text_encoder_weights_fpath)
        diffusion_model.load_weights(diffusion_model_weights_fpath)
        decoder.load_weights(decoder_weights_fpath)
    return text_encoder, diffusion_model, decoder, encoder , text_encoder_f , diffusion_model_f , decoder_f , encoder_f
