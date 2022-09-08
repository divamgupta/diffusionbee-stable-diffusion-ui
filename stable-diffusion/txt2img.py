import argparse, os, sys, glob
import cv2
import torch
import numpy as np
from omegaconf import OmegaConf
from PIL import Image
from tqdm import tqdm, trange
from imwatermark import WatermarkEncoder
from itertools import islice
from einops import rearrange
# from torchvision.utils import make_grid
import time
from pytorch_lightning import seed_everything
from torch import autocast
from contextlib import contextmanager, nullcontext
from collections import namedtuple
import copy
# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from ldm.util import instantiate_from_config
from ldm.models.diffusion.ddim import DDIMSampler
from ldm.models.diffusion.plms import PLMSSampler
from ldm.models.diffusion.ddpm import *
from ldm.modules.diffusionmodules.openaimodel import *
import multiprocessing

from ldm.models.autoencoder import *
from ldm.modules.encoders.modules import *
import json


import warnings
warnings.filterwarnings("ignore")


time.sleep(0.5)

class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, datas):
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


sys.stdout = Unbuffered(sys.stdout)



# so that it works with utf-8 files!
try:
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
except Exception as e:
    print("locale set failed")
    try:
        locale.setlocale(locale.LC_ALL, 'English_United States.1252')
    except Exception as e:
        print("locale set failed 2")

# PYTHONUTF8=1
os.environ["PYTHONUTF8"] = "1"






def get_device():
    if(torch.cuda.is_available()):
        return 'cuda'
    elif(torch.backends.mps.is_available()):
        return 'mps'
    else:
        return 'cpu'


from transformers import AutoFeatureExtractor


device = torch.device(get_device())

def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def numpy_to_pil(images):
    """
    Convert a numpy image or a batch of images to a PIL image.
    """
    if images.ndim == 3:
        images = images[None, ...]
    images = (images * 255).round().astype("uint8")
    pil_images = [Image.fromarray(image) for image in images]

    return pil_images


def load_model_from_config(config, ckpt, verbose=False):
    print(f"Loading model from {ckpt}")
    pl_sd = torch.load(ckpt, map_location="cpu")
    if "global_step" in pl_sd:
        print(f"Global Step: {pl_sd['global_step']}")
    sd = pl_sd["state_dict"]
    model = instantiate_from_config(config.model)
    m, u = model.load_state_dict(sd, strict=False)
    if len(m) > 0 and verbose:
        print("missing keys:")
        print(m)
    if len(u) > 0 and verbose:
        print("unexpected keys:")
        print(u)

    model.to(get_device())
    model.eval()
    return model


def put_watermark(img, wm_encoder=None):
    if wm_encoder is not None:
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img = wm_encoder.encode(img, 'dwtDct')
        img = Image.fromarray(img[:, :, ::-1])
    return img


class Opt:
    pass


def process_opt(opt, model):

    seed_everything(opt.seed)

    if opt.plms:
        sampler = PLMSSampler(model)
    else:
        sampler = DDIMSampler(model)

    os.makedirs(opt.outdir, exist_ok=True)
    outpath = opt.outdir

    wm = "stable_diffusion_gui"
    wm_encoder = WatermarkEncoder()
    wm_encoder.set_watermark('bytes', wm.encode('utf-8'))

    batch_size = opt.n_samples
    n_rows = opt.n_rows if opt.n_rows > 0 else batch_size
        
    prompt = opt.prompt
    assert prompt is not None
    data = [batch_size * [prompt]]

    sample_path = os.path.join(outpath, "samples")
    os.makedirs(sample_path, exist_ok=True)
    base_count = len(os.listdir(sample_path))
    grid_count = len(os.listdir(outpath)) - 1

    start_code = None
    if opt.fixed_code:
        start_code = torch.randn(
            [opt.n_samples, opt.C, opt.H // opt.f, opt.W // opt.f], device="cpu"
        ).to(torch.device(device))

    precision_scope = autocast if opt.precision=="autocast" else nullcontext
    if device.type == 'mps':
        precision_scope = nullcontext # have to use f32 on mps
    with torch.no_grad():
        with precision_scope(device.type):
            with model.ema_scope():
                tic = time.time()
                for n in trange(opt.n_iter, desc="Sampling"):
                    for prompts in tqdm(data, desc="data"):

                        uc = None
                        if opt.scale != 1.0:
                            uc = model.get_learned_conditioning(batch_size * [""])
                        if isinstance(prompts, tuple):
                            prompts = list(prompts)
                        c = model.get_learned_conditioning(prompts)
                        shape = [opt.C, opt.H // opt.f, opt.W // opt.f]
                        samples_ddim, qqq = sampler.sample(S=opt.ddim_steps,
                                                         conditioning=c,
                                                         batch_size=opt.n_samples,
                                                         shape=shape,
                                                         verbose=False,
                                                         unconditional_guidance_scale=opt.scale,
                                                         unconditional_conditioning=uc,
                                                         eta=opt.ddim_eta,
                                                         x_T=start_code)

                        if qqq is None and samples_ddim is None: #bad code to detect stop within the module
                            return 

                        x_samples_ddim = model.decode_first_stage(samples_ddim)
                        x_samples_ddim = torch.clamp((x_samples_ddim + 1.0) / 2.0, min=0.0, max=1.0)
                        x_samples_ddim = x_samples_ddim.cpu().permute(0, 2, 3, 1).numpy()

                        x_checked_image = x_samples_ddim

                        x_checked_image_torch = torch.from_numpy(x_checked_image).permute(0, 3, 1, 2)

                        if not opt.skip_save:
                            for x_sample in x_checked_image_torch:
                                x_sample = 255. * rearrange(x_sample.cpu().numpy(), 'c h w -> h w c')
                                img = Image.fromarray(x_sample.astype(np.uint8))
                                img = put_watermark(img, wm_encoder)
                                impath = os.path.join(sample_path, f"{base_count:05}.png")
                                img.save(impath)
                                print("utds generated_image___U_P_D_A_T_E___\"%s\""%(impath) ) 
                                base_count += 1

                         
                toc = time.time()

    print(f"Your samples are ready and waiting for you here: \n{outpath} \n"
          f" \nEnjoy.")


def main():
    opt = Opt()
    opt.prompt = None # "apple"
    opt.outdir = "/tmp/"
    opt.skip_save = False
    opt.ddim_steps = 40
    opt.plms = False
    opt.fixed_code = False
    opt.ddim_eta = 0.0
    opt.n_iter = 1
    opt.H = 256
    opt.W = 256
    opt.C = 4
    opt.f = 8
    opt.n_samples = 1
    opt.n_rows = 1
    opt.scale = 7.5

    opt.config = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "configs",
                "stable-diffusion",
                "v1-inference.yaml"))

    opt.ckpt = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "models",
                "stable_diffusion_model.ckpt"))

    opt.seed = 42
    opt.precision = "autocast"

    #TODO downlaod model if not downlaoded

    print("utds loading_msg___U_P_D_A_T_E___\" Loading model \"" ) 
    print("utds loading_percentage___U_P_D_A_T_E___-1" ) 

    
   
    config = OmegaConf.load(f"{opt.config}")
    model = load_model_from_config(config, f"{opt.ckpt}")

    model = model.to(device)

    print("utds is_model_loaded___U_P_D_A_T_E___true") # model loaded
    print("utds loading_msg___U_P_D_A_T_E___\"\"" ) 


    while True:
        print("utds is_textbox_avail___U_P_D_A_T_E___true") # model loaded # disable input
        print("utds loading_msg___U_P_D_A_T_E___\"\"") 

        inp_str = input()

        if inp_str.strip() == "":
            continue

        if not "b2py t2im" in inp_str:
            continue
        inp_str = inp_str.replace("b2py t2im" , "").strip()
        try:
            d = json.loads(inp_str)

            print("utds is_textbox_avail___U_P_D_A_T_E___false") # model loaded # disable input
            print("utds loading_msg___U_P_D_A_T_E___\"Generating Image\"") 
            print("utds generated_image___U_P_D_A_T_E___\"\"") 
            print("utds backedn_error___U_P_D_A_T_E___\"\"") 

            new_opt = copy.deepcopy(opt)
            for key,value in d.items():
                setattr(new_opt,key,value)
            print("utds is_textbox_avail___U_P_D_A_T_E___false") # model loaded # disable input
            print("utds loading_msg___U_P_D_A_T_E___\"Generating Image\"") 
            print("utds generated_image___U_P_D_A_T_E___\"\"") 
            print("utds backedn_error___U_P_D_A_T_E___\"\"") 
            print("utds loading_percentage___U_P_D_A_T_E___"+str(0) ) 
            process_opt(new_opt, model)
        except Exception as e:
            print("utds backedn_error___U_P_D_A_T_E___\"%s\""%(str(e))) 
            print("py2b eror " + str(e))

        

    

if __name__ == "__main__":
    multiprocessing.freeze_support()  # for pyinstaller
    main()
