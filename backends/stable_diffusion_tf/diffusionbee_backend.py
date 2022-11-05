from stable_diffusion_tf.stable_diffusion import StableDiffusion
from stable_diffusion_tf.stdin_input import is_avail, get_input
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
            negative_prompt=d['negative_prompt'],
            input_image=d['input_image'],
            mask_image=d['mask_image'],
            input_image_strength=(1-float(d['img_strength'])),
        )
        if img is None:
            return
        
        for i in range(len(img)):
            s = ''.join(filter(str.isalnum, str(d['prompt'])[:30] ))
            fpath = os.path.join(defualt_data_root , "%s_%d.png"%(s ,  random.randint(0 ,100000000)) )

            Image.fromarray(img[i]).save(fpath)
            print("sdbk nwim %s"%(fpath) )


cur_model_id = -1
cur_model = None
def get_sd_model(model_id):
    global p1 , p2 , p3 , p4 , p1_15 , p2_15 , p3_15 , p4_15 
    global cur_model_id , cur_model
    if cur_model_id != model_id:
        
        if cur_model is not None:
            cur_model = None
            time.sleep(1)
        if model_id == 0:

            print("sdbk gnms  Loading SD Model"  )
            cur_model = StableDiffusion(img_height=512, img_width=512, jit_compile=False, download_weights=False, is_sd_15_inpaint=False)
            cur_model.text_encoder .load_weights(p2)
            cur_model.diffusion_model.load_weights(p1)  
            cur_model.decoder.load_weights(p3) 
            cur_model.encoder.load_weights(p4) 
            print("sdbk mdvr 1.4tf")
        elif model_id == 1:
            print("sdbk mdvr 1.5tf_inp")
            print("sdbk gnms  Loading SD Inpainting Model"  )
            cur_model = StableDiffusion(img_height=512, img_width=512, jit_compile=False, download_weights=False, is_sd_15_inpaint=True)
            cur_model.text_encoder .load_weights(p2_15)
            cur_model.diffusion_model.load_weights(p1_15)  
            cur_model.decoder.load_weights(p3_15) 
            cur_model.encoder.load_weights(p4_15) 
        else:
            assert False
        
        cur_model_id = model_id 
    
    return cur_model


def main():

    global p1 , p2 , p3 , p4 , p1_15 , p2_15 , p3_15 , p4_15 

    print("sdbk mltl Loading Model")

    is_downloaded = False
    for _ in range(10):
        try:
            p1 = ProgressBarDownloader(title="Downloading Model 1/8").download(
                        url="https://huggingface.co/fchollet/stable-diffusion/resolve/main/diffusion_model.h5",
                        md5_checksum="72db3d55b60691e1f8a6a68cd9f47ad0",
                        verify_ssl=False,
                        extract_zip=False,
                    )

            p2 = ProgressBarDownloader(title="Downloading Model 2/8").download(
                        url="https://huggingface.co/fchollet/stable-diffusion/resolve/main/text_encoder.h5",
                        md5_checksum="9ea30bed7728473b4270a76aabf1836b",
                        verify_ssl=False,
                        extract_zip=False,
                    )


            p3 = ProgressBarDownloader(title="Downloading Model 3/8").download(
                        url="https://huggingface.co/fchollet/stable-diffusion/resolve/main/decoder.h5",
                        md5_checksum="8c86dc2fadfb0da9712a7a06cfa7bf11",
                        verify_ssl=False,
                        extract_zip=False,
                    )
            
            p4 = ProgressBarDownloader(title="Downloading Model 4/8").download(
                        url="https://huggingface.co/divamgupta/stable-diffusion-tensorflow/resolve/main/encoder_newW.h5",
                        md5_checksum="bef951ed69aa5a7a3acae0ab0308b630",
                        verify_ssl=False,
                        extract_zip=False,
                    )

            p1_15 = ProgressBarDownloader(title="Downloading Model 5/8").download(
                        url="https://huggingface.co/divamgupta/stable-diffusion-tensorflow/resolve/main/diffusion_model_15_inpaint.h5",
                        md5_checksum="fd5868208a33dc4594559433bc493334",
                        verify_ssl=False,
                        extract_zip=False,
                    )

            p2_15 = ProgressBarDownloader(title="Downloading Model 6/8").download(
                        url="https://huggingface.co/divamgupta/stable-diffusion-tensorflow/resolve/main/text_encoder_15_inpaint.h5",
                        md5_checksum="859cc286026b9c1a510d87f85295b4a4",
                        verify_ssl=False,
                        extract_zip=False,
                    )


            p3_15 = ProgressBarDownloader(title="Downloading Model 7/8").download(
                        url="https://huggingface.co/divamgupta/stable-diffusion-tensorflow/resolve/main/decoder_15_inpaint.h5",
                        md5_checksum="aecfa5cbf18a06158e0dde99d6d2fadf",
                        verify_ssl=False,
                        extract_zip=False,
                    )
            
            p4_15 = ProgressBarDownloader(title="Downloading Model 8/8").download(
                        url="https://huggingface.co/divamgupta/stable-diffusion-tensorflow/resolve/main/encoder_15_inpaint.h5",
                        md5_checksum="f73e95b6d5e1ed32e9a15fe31b1ede70",
                        verify_ssl=False,
                        extract_zip=False,
                    )

            is_downloaded = True
            break
        except Exception as e:
            pass

        time.sleep(10)

    if not is_downloaded:
        raise ValueError("Unable to download the model weights. Please try again and make sure you have free space and a working internet connection.")

            

    print("sdbk mltl Loading Model")



    cur_size = (512 , 512)
    generator = get_sd_model(0)
    

    default_d = { "W" : 512 , "H" : 512, "num_imgs":1 , "ddim_steps" : 25 ,
     "scale" : 7.5, "batch_size":1 , "input_image" : None, "img_strength": 0.5
     , "negative_prompt" : "" ,  "mask_image" : None, "model_id": 0 }


    print("sdbk mdld")

    while True:
        print("sdbk inrd") # input ready

        inp_str = get_input()

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
            generator = None
            generator = get_sd_model(d['model_id'])
                
            process_opt(d, generator)
        except Exception as e:
            traceback.print_exc()
            print("sdbk errr %s"%(str(e)))
            print("py2b eror " + str(e))




if __name__ == "__main__":
    multiprocessing.freeze_support()  # for pyinstaller
    main()