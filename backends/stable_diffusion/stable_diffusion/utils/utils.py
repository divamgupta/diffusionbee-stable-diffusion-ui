from tdict import TDict
from ..sd_run import SDRun 
import math
from dataclasses import fields
from .stdin_input import is_avail, get_input


tdict_model_versions = {}
def get_tdict_model_version(tdict_path):
    if tdict_path in tdict_model_versions:
        return tdict_model_versions[tdict_path]
    f = TDict(tdict_path, mode='r')
    tdict_model_versions[ tdict_path] = f.ctdict_version
    return tdict_model_versions[ tdict_path] 


def get_sd_run_from_dict(d):

    if 'input_img' in d:
        d['input_image_path'] = d['input_img']
    if 'mask_image' in d:
        d['mask_image_path'] = d['mask_image']
    if 'model_tdict_path' in d:
        d['tdict_path'] = d['model_tdict_path']

    if 'batch_size' not in d:
        d['batch_size'] = 1
    if 'num_imgs' not in d:
        d['num_imgs'] = 1

    d2 = {}
    SD_keys = [ff.name for ff in fields(SDRun) ]
    for k in d:
        if k in SD_keys:
            d2[k] = d[k]
            print(k, "k")

    sd_run = SDRun(**d2)

    if sd_run.input_image_path is not None and  sd_run.input_image_path != ""  and ( not sd_run.is_sd15_inpaint):
        sd_run.mode = "img2img"
    else:
        sd_run.mode  = "txt2img"

    
    if "sd_mode_override" in d:
        sd_run.mode = d["sd_mode_override"]

    return sd_run


def sd_bee_stop_callback(state="" , progress=-1):
    if is_avail():
        if "__stop__" in get_input():
            return "stop"