

import os 
import sys
from PIL import Image

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path , "../model_converter"))
model_interface_path = os.environ.get('MODEL_INTERFACE_PATH')  or "../stable_diffusion_tf_models" 
sys.path.append( os.path.join(dir_path , model_interface_path) )

from interface import ModelInterface
from stable_diffusion import StableDiffusion

p_14 = "/Users/divamgupta/.diffusionbee/downloads/sd-v1-4_fp16.tdict"

p_21 = "/Users/divamgupta/Downloads/v2-1_768-nonema-pruned.tdict"


sd = StableDiffusion( ModelInterface , p_14 , model_name=None, callback=None)



def test_1():

    img = sd.generate(
            prompt="a tree" , 
            img_height=512, 
            img_width=512, 
            seed=1, 
            tdict_path=None,
            batch_size=1,
            dtype=ModelInterface.default_float_type,
            scheduler='ddim',
            mode="txt2img" )

    gt_p = "./test_assets/outputs/a_tree_1_ddim.png"

    Image.fromarray(img['img'][0]).show()


def test_1_pt_seed():

    img = sd.generate(
            prompt="a tree" , 
            img_height=512, 
            img_width=512, 
            seed=1417326105, 
            seed_type="pt",
            tdict_path=None,
            batch_size=1,
            dtype=ModelInterface.default_float_type,
            scheduler='ddim',
            mode="txt2img" )

    gt_p = "./test_assets/outputs/a_tree_pt_1417326105.jpg"

    Image.fromarray(img['img'][0]).show()





def test_2():

    img = sd.generate(
            prompt="a fantasy tiger rightening , Fangs and tusks , massive square jaw with underbite , cybernetic eye , smoking lit cigar , Heavy and crude industrial sci " , 
            img_height=512, 
            img_width=512, 
            seed=145, 
            tdict_path=None,
            batch_size=1,
            dtype=ModelInterface.default_float_type,
            scheduler='k_euler_ancestral',
            mode="txt2img" )
    gt_p = "./test_assets/outputs/tiger_k_euler_ancestral_145.png"

    Image.fromarray(img['img'][0]).show()





def test_3():

    img = sd.generate(
            prompt="a fantasy tiger rightening , Fangs and tusks , massive square jaw with underbite , cybernetic eye , smoking lit cigar , Heavy and crude industrial sci " , 
            img_height=512, 
            img_width=512, 
            seed=145, 
            tdict_path=None,
            batch_size=1,
            dtype=ModelInterface.default_float_type,
            scheduler='lmsd',
            mode="txt2img" )
    gt_p = "./test_assets/outputs/tiger_lmsd_145.png"

    Image.fromarray(img['img'][0]).show()


def test_4():

    img = sd.generate(
            prompt="a fantasy tiger rightening , Fangs and tusks , massive square jaw with underbite , cybernetic eye , smoking lit cigar , Heavy and crude industrial sci " , 
            img_height=512, 
            img_width=512, 
            seed=145, 
            tdict_path=None,
            batch_size=1,
            dtype=ModelInterface.default_float_type,
            scheduler='pndm',
            mode="txt2img" )

    gt_p = "./test_assets/outputs/tiger_pndm_145.png"

    Image.fromarray(img['img'][0]).show()



def test_5():

    inp = "./test_assets/mmm.png"
    mas = "./test_assets/ddd.png"

    img = sd.generate(
        prompt="Face of red cat, high resolution, sitting on a park bench" , 
        img_height=512, 
        img_width=512, 
        seed=443136, 
        input_image=inp, 
        mask_image=mas,  
        scheduler='ddim',
        tdict_path="/Users/divamgupta/.diffusionbee/downloads/sd-v1-5-inpainting_fp16.tdict",
        mode="inpaint_15" )

    gt_p = "./test_assets/outputs/inp_out_443136.png"
    Image.fromarray(img['img'][0]).show()


def test_5_5():

    inp = "./test_assets/mmm.png"
    mas = "./test_assets/ddd.png"

    img = sd.generate(
        prompt="Face of yellow cat, high resolution, sitting on a park bench" , 
        img_height=512, 
        img_width=512, 
        seed=44136, 
        input_image=inp, 
        mask_image=mas,  
        num_steps=50,
        scheduler='ddim',
        tdict_path="/Users/divamgupta/.diffusionbee/downloads/sd-v1-5-inpainting_fp16.tdict",
        mode="inpaint_15" )

    gt_p = "./test_assets/outputs/inp_out_2_443136.png"
    Image.fromarray(img['img'][0]).show()




def test_6():

    inp = "./test_assets/mmm.png"
    mas = "./test_assets/ddd.png"

    img = sd.generate(
        prompt="yellow cat, high resolution, sitting on a park bench" , 
        img_height=512, 
        img_width=512, 
        seed=678, 
        input_image=inp, 
        mask_image=mas,  
        scheduler='ddim',
        tdict_path="/Users/divamgupta/.diffusionbee/downloads/sd-v1-5-inpainting_fp16.tdict",
        mode="inpaint_15" )
    gt_p = "./test_assets/outputs/inp_out_678.png"
    Image.fromarray(img['img'][0]).show()


def test_7():

    img = sd.generate(
            prompt="a tree" , 
            img_height=512, 
            img_width=512, 
            seed=1, 
            batch_size=2,
            tdict_path=None,
            dtype=ModelInterface.default_float_type,
            scheduler='ddim',
            mode="txt2img" )

    gt_p = "./test_assets/outputs/a_tree_1_ddim.png"
    gt_p2 = "./test_assets/outputs/a_tree_1_ddim_2.png"


    Image.fromarray(img['img'][0]).show()
    Image.fromarray(img['img'][1]).show()




def test_ctrl_1():
    inp = "./test_assets/scribble_turtle.png"

    img = sd.generate(
            prompt="a turtle" , 
            img_height=512, 
            img_width=512, 
            seed=6378, 
            tdict_path=None,
            second_tdict_path="/Users/divamgupta/.diffusionbee/downloads/just_control_sd15_scribble_fp16.tdict",
            batch_size=1,
            dtype="float16",
            scheduler='ddim',
            num_steps=10,
            input_image=inp,
            mode="controlnet" )

    Image.fromarray(img['img'][0]).show()



def test_sd2_1():

    img = sd.generate(
            prompt="a tree" , 
            img_height=512, 
            img_width=512, 
            seed=1, 
            num_steps=25,
            tdict_path="/Users/divamgupta/.diffusionbee/custom_models/v2-1_512-ema-pruned.tdict",
            batch_size=1,
            dtype=ModelInterface.default_float_type,
            scheduler='ddim',
            mode="txt2img" )

    # a_tree_1_sd2.png

    Image.fromarray(img['img'][0]).show()



def test_sd2_3():

    img = sd.generate(
            prompt="Face of yellow cat, high resolution, sitting on a park bench" , 
            img_height=512, 
            img_width=512, 
            seed=111, 
            num_steps=50,
            tdict_path="/Users/divamgupta/.diffusionbee/custom_models/v2-1_512-ema-pruned.tdict",
            batch_size=1,
            dtype=ModelInterface.default_float_type,
            scheduler='ddim',
            mode="txt2img" )

    # sd2_a_cat_111_test_sd2_3.png

    Image.fromarray(img['img'][0]).show()



def test_sd2_2():

    img = sd.generate(
            prompt="dog" , 
            img_height=512, 
            img_width=512, 
            seed=1, 
            num_steps=5,
            tdict_path="/Users/divamgupta/.diffusionbee/custom_models/djzJovianSkyshipV21_0.tdict",
            batch_size=1,
            dtype='float16',
            scheduler='ddim',
            mode="txt2img" )

    Image.fromarray(img['img'][0]).show()






def test_sd2_4():

    img = sd.generate(
            prompt="a tree" , 
            img_height=512, 
            img_width=512, 
            seed=13, 
            num_steps=30,
            tdict_path="/Volumes/ext_drive_1/sd_data_models/v2-1_768-nonema-pruned.tdict",
            dtype="float32",
            scheduler='ddim_v',
            mode="txt2img" )

    # sd2_a_cat_111_test_sd2_3.png

    Image.fromarray(img['img'][0]).show()




def test_lr_1():

    img = sd.generate(
            prompt="masterpiece,best quality,toon,3D,simple design, Pixar style,house, sandbox ,Peach and Mint,tree ,Florist, Arial view" , 
            negative_prompt="lowres, bad anatomy, bad hands,text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry,tree on the roof,",
            img_height=512, 
            img_width=512, 
            seed=1456, 
            batch_size=1,
            # tdict_path="/Users/divamgupta/Downloads/merge.tdict",
            tdict_path="/Volumes/ext_drive_1/sd_data_models/sd-v1-5_fp16.tdict",
            dtype=ModelInterface.default_float_type,
            scheduler='ddim',
            mode="txt2img" )

    gt_p = "./test_assets/outputs/a_tree_1_ddim.png"

    Image.fromarray(img['img'][0]).show()




def test_1_torchseed():

    img = sd.generate(
            prompt="a tree" , 
            img_height=512, 
            img_width=512, 
            seed=1417326105, 
            tdict_path="/Volumes/ext_drive_1/sd_data_models/sd-v1-5_fp16.tdict",
            batch_size=1,
            dtype=ModelInterface.default_float_type,
            scheduler='ddim',
            mode="txt2img" )

    Image.fromarray(img['img'][0]).show()





def test_lr_2():

    img = sd.generate(
            prompt="masterpiece,best quality,toon,3D,simple design, Pixar style,house, sandbox ,Peach and Mint,tree ,Florist, Arial view" , 
            negative_prompt="lowres, bad anatomy, bad hands,text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry,tree on the roof,",
            img_height=512, 
            img_width=512, 
            seed=1456, 
            batch_size=1,
            tdict_path="/Users/divamgupta/Downloads/merge.tdict",
            # tdict_path="/Volumes/ext_drive_1/sd_data_models/sd-v1-5_fp16.tdict",
            dtype=ModelInterface.default_float_type,
            scheduler='ddim',
            mode="txt2img" )

    gt_p = "./test_assets/outputs/a_tree_1_ddim.png"

    Image.fromarray(img['img'][0]).show()




def test_lr_3():

    img = sd.generate(
            prompt="masterpiece,best quality,toon,3D,simple design, Pixar style,house, sandbox ,Peach and Mint,tree ,Florist, Arial view" , 
            negative_prompt="lowres, bad anatomy, bad hands,text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry,tree on the roof,",
            img_height=512, 
            img_width=512, 
            seed=1456, 
            batch_size=1,
            tdict_path="/Volumes/ext_drive_1/sd_data_models/sd-v1-5_fp16.tdict",
            dtype=ModelInterface.default_float_type,
            scheduler='ddim',   
            num_steps=25,
            lora_tdict_paths={"/Users/divamgupta/Downloads/lora.tdict" : 1.0 },
            mode="txt2img" )

    gt_p = "./test_assets/outputs/a_tree_1_ddim.png"

    Image.fromarray(img['img'][0]).show()


def test_lr_31():

    img = sd.generate(
            prompt="masterpiece,best quality,toon,3D,simple design, Pixar style,house, sandbox ,Peach and Mint,tree ,Florist, Arial view" , 
            negative_prompt="lowres, bad anatomy, bad hands,text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry,tree on the roof,",
            img_height=512-128, 
            img_width=512+128, 
            seed=1456, 
            batch_size=1,
            tdict_path="/Volumes/ext_drive_1/sd_data_models/sd-v1-5_fp16.tdict",
            dtype=ModelInterface.default_float_type,
            num_steps=25,
            scheduler='ddim',   
            lora_tdict_paths={"/Users/divamgupta/Downloads/lora.tdict" : 1.0 },
            mode="txt2img" )

    gt_p = "./test_assets/outputs/a_tree_1_ddim.png"

    Image.fromarray(img['img'][0]).show()


def test_lr_32():

    img = sd.generate(
            prompt="masterpiece,best quality,toon,3D,simple design, Pixar style,house, sandbox ,Peach and Mint,tree ,Florist, Arial view" , 
            negative_prompt="lowres, bad anatomy, bad hands,text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry,tree on the roof,",
            img_height=512-128, 
            img_width=512+128, 
            seed=1456, 
            batch_size=1,
            tdict_path=p_14,
            dtype=ModelInterface.default_float_type,
            num_steps=25,
            scheduler='ddim',   
            lora_tdict_paths={"/Users/divamgupta/Downloads/lora.tdict" : 1.0 },
            mode="txt2img" )

    gt_p = "./test_assets/outputs/a_tree_1_ddim.png"

    Image.fromarray(img['img'][0]).show()




# test_lr_1()

def test_11():

    img = sd.generate(
            prompt="a tree" , 
            img_height=512, 
            img_width=512, 
            seed=1, 
            tdict_path=None,
            batch_size=1,
            num_steps=5,
            dtype=ModelInterface.default_float_type,
            scheduler='ddim',
            mode="txt2img" )

    gt_p = "./test_assets/outputs/a_tree_1_ddim.png"

    Image.fromarray(img['img'][0]).show()



test_11()

exit()



# inp = "./test_assets/yoga1.jpg"


# img = sd.generate(
#         prompt="a man doing yoga, Underwater series /// High detail RAW color photo professional, highly detail face: 1.4, a detailed portrait of a woman floating underwater wearing long flowing dress, nymph style, amazing underwater, detailed skin, wet clothes, wet hair, see-through clothes, lens flare, shade, tindal effect, lens flare, backlighting, bokeh " , 
#         img_height=512, 
#         img_width=512, 
#         seed=6378, 
#         tdict_path=None,
#         second_tdict_path="/Users/divamgupta/Downloads/just_control_sd15_openpose_fp16.tdict",
#         batch_size=1,
#         dtype=ModelInterface.default_float_type,
#         scheduler='ddim',
#         num_steps=25,
#         input_image=inp,
#         inp_img_preprocesser="body_pose",
#         mode="controlnet" )


# Image.fromarray(img[0]).show()





# Image.fromarray(img['img'][0]).show()


# img = sd.generate(
#         prompt="a tortoise" , 
#         img_height=512, 
#         img_width=512, 
#         seed=678, 
#         tdict_path=None,
#         batch_size=1,
#         dtype=ModelInterface.default_float_type,
#         scheduler='ddim',
#         input_image=inp,
#         mode="txt2img" )


# Image.fromarray(img[0]).show()


inp = "./test_assets/mmm.png"
mas = "./test_assets/ddd.png"




for cur_run_id in range(2):
    img = sd.generate(
        prompt="a haloween bedroom" , 
        img_height=512+64, 
        img_width=512-64, 
        seed=678, 
        tdict_path=None,
        batch_size=1,
        dtype=ModelInterface.default_float_type,
        scheduler='ddim',
        input_image_strength=0.4,
        input_image="bedroom2.jpg",
        mode="img2img" )
    Image.fromarray(img[0]).show()

for cur_run_id in range(2):
    img = sd.generate(
        prompt="modern disney a blue colored baby lion with lots of fur" , 
        img_height=512-64, 
        img_width=512, 
        seed=34, 
        num_steps=25,
        batch_size=1,
        tdict_path="/Users/divamgupta/.diffusionbee/custom_models/moDi-v1-pruned.tdict",
        dtype=ModelInterface.default_float_type,
        scheduler='ddim',
        mode="txt2img" )
    Image.fromarray(img[0]).show()

img = sd.generate(
    prompt="modern disney a blue colored baby lion with lots of fur" , 
    img_height=512, 
    img_width=512, 
    seed=34, 
    tdict_path=None,
    mode="txt2img" )
Image.fromarray(img[0]).show()


img = sd.generate(
    prompt="Face of red cat, high resolution, sitting on a park bench" , 
    img_height=512, 
    img_width=512, 
    seed=443136, 
    input_image=inp, 
    mask_image=mas,  
    tdict_path="/Users/divamgupta/Downloads/sd-v1-5-inpainting.tdict",
    mode="inpaint_15" )
Image.fromarray(img[0]).show()



