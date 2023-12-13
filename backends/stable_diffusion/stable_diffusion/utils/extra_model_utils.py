# utils for resolving weights of extra models like LoRA, TI etc
import numpy as np
from tdict import TDict
from tqdm import tqdm


def add_lora_w(weight ,up_weight ,  down_weight , scale , ratio):

    # for some reason numpy operatrions are slow with fp16
    weight = weight.astype('float32')
    up_weight = up_weight.astype('float32')
    down_weight = down_weight.astype('float32')
        
    if len(weight.shape) == 2:
        # linear
        weight = weight + ratio * (up_weight @ down_weight) * scale
    elif down_weight.shape[2:4] == (1, 1):
     
        # conv2d 1x1
        weight = (
            weight
            + ratio
            * (up_weight[: , : , 0 , 0 ] @ down_weight[: , : , 0 , 0 ])[: , : , None , None ] 
            * scale
        )
    else:
        raise ValueError("Unsupported LoRA W")
    
    weight = weight.astype( 'float16' )
    return weight

def add_lora_weights(src_tdict , state_dict , lora_tdict , ratio ):
    lora_tdict.init_read()
    root_keys = [ k.replace("_lora_up" , "").replace("_lora_down" , "").replace("_lora_scale" , "") for k in lora_tdict.keys() ]
    root_keys = list(set(root_keys))

    for k in tqdm(root_keys):
        if k not in state_dict:
            state_dict[k] = src_tdict.read_key(k).copy()
        up_weight = lora_tdict.read_key(k + "_lora_up")
        down_weight = lora_tdict.read_key(k + "_lora_down")
        scale = lora_tdict.read_key(k + "_lora_scale")

        state_dict[k] = add_lora_w( state_dict[k] , up_weight=up_weight , down_weight=down_weight ,  scale=scale , ratio=ratio  )


def add_lora_ti_weights(src_tdict , weight_additions_list):
    src_tdict.init_read()
    state_dict = {}
    for add_model_fn , tdict_path , power in weight_additions_list:
        if add_model_fn == "lora":
            m_tdict = TDict(tdict_path)
            add_lora_weights(src_tdict , state_dict, m_tdict ,  power )

    return state_dict

def clip_skip_2_patch_weights(src_tdict, weight_additions_list ,  current_weight_additions):
    is_skip = False
    for add_model_fn , _ , _ in weight_additions_list:
        if add_model_fn == "clip_skip_2":
            is_skip = True

    if is_skip:
        src_tdict.init_read()
        for k in src_tdict.keys():
            if k in [
                "cond_stage_model.transformer.text_model.encoder.layers.11.mlp.fc2.weight",
                "cond_stage_model.transformer.text_model.encoder.layers.11.mlp.fc2.bias",
                "cond_stage_model.transformer.text_model.encoder.layers.11.self_attn.out_proj.weight",
                "cond_stage_model.transformer.text_model.encoder.layers.11.self_attn.out_proj.bias"
            ]:
                current_weight_additions[k] = (src_tdict.read_key(k).copy() * 0).astype('float16')

    return current_weight_additions


