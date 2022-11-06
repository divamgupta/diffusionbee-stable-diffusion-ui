from fake_torch import fake_torch_load_zipped
import json
import numpy as np
from constants import SD_SHAPES
import sys 

# python convert_model.py "/Users/divamgupta/Downloads/hollie-mengert.ckpt"  "/Users/divamgupta/Downloads/hollie-mengert.tdict"

# pyinstaller  convert_model.py  --onefile  --noconfirm --clean # build using intel machine so that its cross platform lol

checkpoint_filename = sys.argv[1]
out_filename = sys.argv[2]

#TODO add MD5s

_HEADER_BYTES  = [42, 10 , 8, 42] + [0]*20


s  = 24

torch_weights = fake_torch_load_zipped(open(checkpoint_filename, "rb"))
keys_info = {}
out_file = open( out_filename , "wb")

out_file.write(bytes(_HEADER_BYTES))

for k in torch_weights['state_dict']:
    assert k in SD_SHAPES , k 
    np_arr = torch_weights['state_dict'][k]
    key_bytes = np_arr.tobytes()
    shape = list(np_arr.shape)
    assert tuple(shape) == SD_SHAPES[k], (k , shape , SD_SHAPES[k] )
    dtype = str(np_arr.dtype)
    e = s + len(key_bytes)
    out_file.write(key_bytes)
    keys_info[k] = {"start": s , "end" : e , "shape": shape , "dtype" : dtype }
    s = e

for k in SD_SHAPES:
    if 'model_ema' in k or 'betas' in k or 'alphas' in k or 'posterior_' in k:
        continue
    assert k in keys_info , k

json_start = s
info_json = bytes( json.dumps(keys_info)  , 'ascii') 
json_end = s + len(info_json)

out_file.write(info_json)

out_file.seek(5)
out_file.write(np.array(json_start).astype('long').tobytes())

out_file.seek(14)
out_file.write(np.array(json_end).astype('long').tobytes())
