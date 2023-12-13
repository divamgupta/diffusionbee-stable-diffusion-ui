from PIL import Image, ImageOps, ImageFilter
import numpy as np

def process_inp_img(input_image, image_size="legacy_auto",new_w=None , new_h=None , only_read_alpha=False):
    input_image = Image.open(input_image)

    if only_read_alpha:
        input_image = input_image.split()[-1] #only keep the last channel
        input_image = ImageOps.invert(input_image)

    input_image = input_image.convert('RGB')

    if image_size == "legacy_auto":
        w , h = input_image.size
        if w > h:
            new_w = 512
            new_h  = round((h * new_w / w)/64)*64
        else:
            new_h = 512
            new_w  = round((w * new_h / h)/64)*64

    input_image_downscaled = ImageOps.fit(input_image, (new_w//8, new_h//8), method = Image.ANTIALIAS ,
                   bleed = 0.0, centering =(0.5, 0.5))

    input_image = ImageOps.fit(input_image, (new_w, new_h), method = Image.ANTIALIAS ,
                   bleed = 0.0, centering =(0.5, 0.5))
    input_image = np.array(input_image)[... , :3]
    input_image_downscaled = np.array(input_image_downscaled)[... , :3]
    input_image = (input_image.astype("float32") / 255.0)*2 - 1 
    input_image_downscaled = (input_image_downscaled.astype("float32") / 255.0)*2 - 1 
    return new_h , new_w  , input_image , input_image_downscaled

def post_process_mask(im , dilate=None, erode=None, blur=None):
    im = Image.fromarray((( im + 1 )*255/2).astype('uint8') )
    if dilate is not None:
        im = im.filter(ImageFilter.MaxFilter(dilate))
    if erode is not None:
        im = im.filter(ImageFilter.MinFilter(dilate))
    return (np.array(im).astype("float32")/ 255.0)*2 - 1 

