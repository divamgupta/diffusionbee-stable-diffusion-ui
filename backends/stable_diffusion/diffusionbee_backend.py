print("backend")

from  stdin_input import is_avail, get_input
import argparse
from PIL import Image
import json
import random
import multiprocessing
from downloader import ProgressBarDownloader
import sys
import copy
import math
import time
import traceback
from stable_diffusion import StableDiffusion

# b2py t2im {"prompt": "sun glasses" , "W":640 , "H" : 640 , "num_imgs" : 10 , "input_image":"/Users/divamgupta/Downloads/inn.png" , "mask_image" : "/Users/divamgupta/Downloads/maa.png" , "is_inpaint":true  }



from pathlib import Path
import os

home_path = Path.home()

projects_root_path = os.path.join(home_path, ".diffusionbee")

if not os.path.isdir(projects_root_path):
    os.mkdir(projects_root_path)


defualt_data_root = os.path.join(projects_root_path, "images")


if not os.path.isdir(defualt_data_root):
    os.mkdir(defualt_data_root)



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


def download_weights():
    global p_14 , p_14_np

    print("sdbk mltl Loading Model")

    is_downloaded = False
    for _ in range(10):
        try:
            print("sdbk mltl Downloading Model 1/2")

            p_14 = "/Users/divamgupta/Downloads/sd-v1-4.tdict"

            print("sdbk mltl Downloading Model 2/2")

            p_14_np = "/Users/divamgupta/Downloads/sd-v1-5-inpainting.tdict"

            is_downloaded = True
            break
        except Exception as e:
            pass

        time.sleep(10)

    if not is_downloaded:
        raise ValueError("Unable to download the model weights. Please try again and make sure you have free space and a working internet connection.")

            



def process_opt(d, generator):

    batch_size = int(d['batch_size'])
    n_imgs = math.ceil(d['num_imgs'] / batch_size)

    if d['model_id'] == 1:
        model_mode = "inpaint_15"
        tdict_path = p_14_np
        print("sdbk mdvr 1.5_inp")
    else:
        tdict_path = p_14
        print("sdbk mdvr 1.4")
        if "input_image" in d and  d['input_image' ] is not None and d['input_image'] != "" :
            model_mode = "img2img"
        else:
            model_mode = "txt2img"

    if d['model_id'] == -1:
        cust_model_path = d['custom_model_path']
        tdict_path = cust_model_path
        print("sdbk mdvr custom_" + cust_model_path.split(os.sep)[-1].split(".")[0])

    for i in range(n_imgs):
        if 'seed' in d:
            seed = d['seed']
        else:
            seed = None
        if 'soft_seed' in d:
            soft_seed = d['soft_seed']
        else:
            soft_seed = None

        img = generator.generate(
            d['prompt'],
            img_height=d["H"], img_width=d["W"],
            num_steps=d['ddim_steps'],
            guidance_scale=d['scale'],
            temperature=1,
            batch_size=batch_size,
            seed=seed,
            soft_seed=soft_seed,
            img_id=i,
            negative_prompt=d['negative_prompt'],
            input_image=d['input_image'],
            tdict_path=tdict_path,
            mode=model_mode,
            mask_image=d['mask_image'],
            input_image_strength=(float(d['img_strength'])),
        )
        if img is None:
            return
        
        for i in range(len(img)):
            s = ''.join(filter(str.isalnum, str(d['prompt'])[:30] ))
            fpath = os.path.join(defualt_data_root , "%s_%d.png"%(s ,  random.randint(0 ,100000000)) )

            Image.fromarray(img[i]).save(fpath)
            print("sdbk nwim %s"%(fpath) )




def main():


    global p_14 , p_14_np
    download_weights()
    print("sdbk mltl Loading Model")

    def callback(state="" , progress=-1):
        print("sdbk dnpr "+str(progress) )
        if state != "Generating":
            print("sdbk gnms " + state)

        if is_avail():
            if "__stop__" in get_input():
                return "stop"

    generator = StableDiffusion( p_14 , model_name="sd_1x", callback=callback)
    

    default_d = { "W" : 512 , "H" : 512, "num_imgs":1 , "ddim_steps" : 25 ,
     "scale" : 7.5, "batch_size":1 , "input_image" : None, "img_strength": 0.5
     , "negative_prompt" : "" ,  "mask_image" : None, "model_id": 0 , "custom_model_path":None}


    print("sdbk mdld")

    while True:
        print("sdbk inrd") # input ready

        inp_str = get_input()

        if inp_str.strip() == "":
            continue

        if not "b2py t2im" in inp_str or "__stop__" in inp_str:
            continue
        inp_str = inp_str.replace("b2py t2im" , "").strip()
        try:
            d_ = json.loads(inp_str)
            d = copy.deepcopy(default_d)
            d.update(d_)
            print("sdbk inwk") # working on the input
     
            process_opt(d, generator)
            
        except Exception as e:
            traceback.print_exc()
            print("sdbk errr %s"%(str(e)))
            print("py2b eror " + str(e))




if __name__ == "__main__":
    multiprocessing.freeze_support()  # for pyinstaller
    main()