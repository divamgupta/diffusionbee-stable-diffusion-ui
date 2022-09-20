from tensorflow import keras
from stable_diffusion_tf.stable_diffusion import Text2Image
import argparse
from PIL import Image
import json
import random
import multiprocessing
from downloader import ProgressBarDownloader
import sys


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
    for _ in range(d['num_imgs']):
        img = generator.generate(
            d['prompt'],
            num_steps=d['ddim_steps'],
            unconditional_guidance_scale=d['scale'],
            temperature=1,
            batch_size=1,
        )
        if img is None:
            return
        fpath = "/tmp/%d.png"%(random.randint(0 ,100000000))
        Image.fromarray(img[0]).save(fpath)
        print("sdbk nwim %s"%(fpath) )


def main():

    print("sdbk mltl Loading Model")

    p1 = ProgressBarDownloader(title="Downloading Model 1/3").download(
                url="https://huggingface.co/fchollet/stable-diffusion/resolve/main/diffusion_model.h5",
                md5_checksum="72db3d55b60691e1f8a6a68cd9f47ad0",
                verify_ssl=False,
                extract_zip=False,
            )

    p2 = ProgressBarDownloader(title="Downloading Model 2/3").download(
                url="https://huggingface.co/fchollet/stable-diffusion/resolve/main/text_encoder.h5",
                md5_checksum="9ea30bed7728473b4270a76aabf1836b",
                verify_ssl=False,
                extract_zip=False,
            )


    p3 = ProgressBarDownloader(title="Downloading Model 2/3").download(
                url="https://huggingface.co/fchollet/stable-diffusion/resolve/main/decoder.h5",
                md5_checksum="8c86dc2fadfb0da9712a7a06cfa7bf11",
                verify_ssl=False,
                extract_zip=False,
            )

    print("sdbk mltl Loading Model")



    cur_size = (512 , 512)
    generator = Text2Image(img_height=512, img_width=512, jit_compile=False, download_weights=False)
    generator.text_encoder .load_weights(p2)
    generator.diffusion_model.load_weights(p1)  
    generator.decoder.load_weights(p3) 


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
            d = json.loads(inp_str)
            print("sdbk inwk") # working on the input

            if cur_size != (d['W'] , d['H']):
                print("sdbk mltl Loading Model")
                generator = Text2Image(img_height= d['H'], img_width=d['W'], jit_compile=False, download_weights=False)
                generator.text_encoder .load_weights(p2)
                generator.diffusion_model.load_weights(p1)  
                generator.decoder.load_weights(p3)
                print("sdbk mdld")
                cur_size = (d['W'] , d['H'])
                
            process_opt(d, generator)
        except Exception as e:
            print("sbdk errr %s"%(str(e)))
            print("py2b eror " + str(e))




if __name__ == "__main__":
    multiprocessing.freeze_support()  # for pyinstaller
    main()