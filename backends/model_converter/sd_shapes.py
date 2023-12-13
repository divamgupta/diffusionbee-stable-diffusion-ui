
from sd_shapes_consts import shapes_unet , shapes_encoder, shapes_decoder , shapes_text_encoder, shapes_params , shapes_unet_v2 , text_encoder_open_clip
import copy
from collections import Counter

def add_aux_shapes(d):
    for k in list(d.keys()):
        if '.norm' in k and '.bias' in k:
            d[k.replace(".bias" , ".bias_by_weight")] = d[k]

        if ".ff." in k:
            sh = list(d[k])
            sh[0] = sh[0] // 2
            sh = tuple(sh)
            d[k + "._split_1"] = sh
            d[k + "._split_2"] = sh

        elif "attn.in_proj" in k and d[k][0]  == 3072  :
            sh = list(d[k])
            sh[0] = sh[0] // 3
            sh = tuple(sh)
            d[k + "._split_1"] = sh
            d[k + "._split_2"] = sh
            d[k + "._split_3"] = sh

        for i in range(1,21):
            nn = 320*i
            d["zeros_"+str(nn)] = (nn,)
            d["ones_"+str(nn)] = (nn,)

            nn = 128*i
            d["zeros_"+str(nn)] = (nn,)
            d["ones_"+str(nn)] = (nn,)




sd_1x_shapes = {}
sd_1x_shapes.update(shapes_unet)
sd_1x_shapes.update(shapes_encoder)
sd_1x_shapes.update(shapes_decoder)
sd_1x_shapes.update(shapes_text_encoder)
sd_1x_shapes.update(shapes_params)

sd_1x_inpaint_shapes = copy.deepcopy(sd_1x_shapes)
sd_1x_inpaint_shapes['model.diffusion_model.input_blocks.0.0.weight'] = [320, 9, 3, 3]

add_aux_shapes(sd_1x_shapes)
add_aux_shapes(sd_1x_inpaint_shapes)




sd_2x_shapes = {}
sd_2x_shapes.update(shapes_unet_v2)
sd_2x_shapes.update(shapes_encoder)
sd_2x_shapes.update(shapes_decoder)
sd_2x_shapes.update(text_encoder_open_clip)
sd_2x_shapes.update(shapes_params)


add_aux_shapes(sd_2x_shapes)


possible_model_shapes = {"SD_1x_float32": sd_1x_shapes , 
    "SD_1x_inpaint_float32": sd_1x_inpaint_shapes, 
    "SD_1x_float16": sd_1x_shapes , 

    "SD_2x_float16": sd_2x_shapes , 
    "SD_2x_float32": sd_2x_shapes , 

    "SD_1x_inpaint_float16": sd_1x_inpaint_shapes}

ctdict_ids = {"SD_1x_float32": 12 , 
    "SD_1x_inpaint_float32": 13, 
    "SD_2x_float32": 15 ,
    "SD_1x_float16": 1012 , 
    "SD_1x_inpaint_float16": 1013 , 
    "SD_1x_just_controlnet_16" : 1014,
    "SD_2x_float16": 1015 ,
    "sdxl_base_unet_f8_rest_f16" : 3031,
    }



extra_keys = ['temb_coefficients_fp32' , 'temb_coefficients_fp16' , 'causal_mask' , 'aux_output_conv.weight' , 'aux_output_conv.bias', 'alphas_cumprod']



def are_shapes_matching(state_dict , template_shapes , name=None):
    for k in template_shapes:
        if k not in state_dict:
            print("key", k , "not found in state_dict" , state_dict.keys())
            return False
        if tuple(template_shapes[k]) != tuple(state_dict[k].shape):
            if tuple(template_shapes[k]) != tuple(state_dict[k].shape) + (1,1):
                print("shape mismatch", k , tuple(template_shapes[k]) ,tuple(state_dict[k].shape) )
                return False 

    return True


def get_dtype(state_dict, template_shapes ):
    c = Counter()

    for k in state_dict:
        if k in extra_keys:
            continue
        if k not in template_shapes:
            continue

        if 'float' in str(state_dict[k].dtype):
            c[ str(state_dict[k].dtype)] += 1 
    print(c.most_common())
    return c.most_common(1)[0][0]



def check_shapes_float(state_dict, template_shapes ):
    for k in state_dict:
        if k in extra_keys:
            continue
        if k not in template_shapes:
            continue
        
        assert 'float' in str(state_dict[k].dtype )



def get_model_type(state_dict):

    if are_shapes_matching(state_dict , sd_1x_shapes) :
        shapes = sd_1x_shapes
        mname = "SD_1x"
    elif are_shapes_matching(state_dict , sd_2x_shapes) :
        shapes = sd_2x_shapes
        mname = "SD_2x"
    elif are_shapes_matching(state_dict , sd_1x_inpaint_shapes) :
        shapes = sd_1x_inpaint_shapes
        mname = "SD_1x_inpaint"
    else:
        return None

    check_shapes_float(state_dict , shapes)
    c_dtype = get_dtype(state_dict , shapes)
    if c_dtype not in ["float32" , "float16"]:
        raise ValueError("The weights should either be float32 or float16, but these are " + c_dtype)

    return mname + "_" + c_dtype


