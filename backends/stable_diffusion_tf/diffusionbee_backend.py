from stable_diffusion_tf.stable_diffusion import StableDiffusion
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



def process_opt(d, generator):

    batch_size = int(d['batch_size'])
    n_imgs = math.ceil(d['num_imgs'] / batch_size)

    
    for i in range(n_imgs):
        if 'seed' in d:
            seed = d['seed']
        else:
            seed = None
        img = generator.generate(
            d['prompt'],
            img_height=d["H"], img_width=d["W"],
            num_steps=d['ddim_steps'],
            unconditional_guidance_scale=d['scale'],
            temperature=1,
            batch_size=batch_size,
            seed=seed,
            img_id=i,
            input_image=d['input_image'],
            input_image_strength=(1-float(d['img_strength'])),
        )
        if img is None:
            return
        
        for i in range(len(img)):
            s = ''.join(filter(str.isalnum, str(d['prompt'])[:30] ))
            fpath = os.path.join(defualt_data_root , "%s_%d.png"%(s ,  random.randint(0 ,100000000)) )

            Image.fromarray(img[i]).save(fpath)
            print("sdbk nwim %s"%(fpath) )


def main():

    print("sdbk mltl Loading Model")

    for _ in range(5):
        try:
            p1 = ProgressBarDownloader(title="Downloading Model 1/4").download(
                        url="https://huggingface.co/fchollet/stable-diffusion/resolve/main/diffusion_model.h5",
                        md5_checksum="72db3d55b60691e1f8a6a68cd9f47ad0",
                        verify_ssl=False,
                        extract_zip=False,
                    )

            p2 = ProgressBarDownloader(title="Downloading Model 2/4").download(
                        url="https://huggingface.co/fchollet/stable-diffusion/resolve/main/text_encoder.h5",
                        md5_checksum="9ea30bed7728473b4270a76aabf1836b",
                        verify_ssl=False,
                        extract_zip=False,
                    )


            p3 = ProgressBarDownloader(title="Downloading Model 3/4").download(
                        url="https://huggingface.co/fchollet/stable-diffusion/resolve/main/decoder.h5",
                        md5_checksum="8c86dc2fadfb0da9712a7a06cfa7bf11",
                        verify_ssl=False,
                        extract_zip=False,
                    )
            
            p4 = ProgressBarDownloader(title="Downloading Model 4/4").download(
                        url="https://huggingface.co/divamgupta/stable-diffusion-tensorflow/resolve/main/encoder_newW.h5",
                        md5_checksum="bef951ed69aa5a7a3acae0ab0308b630",
                        verify_ssl=False,
                        extract_zip=False,
                    )
            break
        except Exception as e:
            pass

        time.sleep(4)

    

            

    print("sdbk mltl Loading Model")



    cur_size = (512 , 512)
    generator = StableDiffusion(img_height=512, img_width=512, jit_compile=False, download_weights=False)
    generator.text_encoder .load_weights(p2)
    generator.diffusion_model.load_weights(p1)  
    generator.decoder.load_weights(p3) 
    generator.encoder.load_weights(p4) 

    default_d = { "W" : 512 , "H" : 512, "num_imgs":1 , "ddim_steps" : 25 , "scale" : 7.5, "batch_size":1 , "input_image" : None, "img_strength": 0.5 }


    print("sdbk mdld")

    while True:
        print("sdbk inrd") # input ready

        inp_str = input()

        if inp_str.strip() == "":
            continue

        if not "b2py t2im" in inp_str:
            continue
        inp_str = inp_str.replace("b2py t2im" , "").strip()
        try:
            d_ = json.loads(inp_str)
            d = copy.deepcopy(default_d)
            d.update(d_)
            print("sdbk inwk") # working on the input

            # if cur_size != (d['W'] , d['H']):
            #     print("sdbk mltl Loading Model")
            #     generator = StableDiffusion(img_height= d['H'], img_width=d['W'], jit_compile=False, download_weights=False)
            #     generator.text_encoder .load_weights(p2)
            #     generator.diffusion_model.load_weights(p1)  
            #     generator.decoder.load_weights(p3)
            #     print("sdbk mdld")
            #     cur_size = (d['W'] , d['H'])
                
            process_opt(d, generator)
        except Exception as e:
            traceback.print_exc()
            print("sdbk errr %s"%(str(e)))
            print("py2b eror " + str(e))




if __name__ == "__main__":
    multiprocessing.freeze_support()  # for pyinstaller
    main()