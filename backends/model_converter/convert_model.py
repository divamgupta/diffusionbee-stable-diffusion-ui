from fake_torch import fake_torch_load_zipped
import json
import numpy as np
from constants import SD_SHAPES, _ALPHAS_CUMPROD
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


torch_weights['state_dict']['temb_coefficients_fp32'] =  np.array([1.0, 0.94406086, 0.8912509, 0.84139514, 0.7943282, 0.7498942, 0.70794576, 0.6683439, 0.63095737, 0.5956621, 0.56234133, 0.53088444, 0.50118726, 0.47315124, 0.44668362, 0.42169648, 0.39810717, 0.3758374, 0.35481337, 0.33496544, 0.31622776, 0.29853827, 0.2818383, 0.2660725, 0.25118864, 0.23713735, 0.2238721, 0.21134889, 0.19952625, 0.18836491, 0.17782794, 0.16788039, 0.15848932, 0.14962357, 0.14125374, 0.13335215, 0.12589253, 0.11885023, 0.11220184, 0.10592538, 0.099999994, 0.094406076, 0.08912509, 0.0841395, 0.07943282, 0.074989416, 0.07079458, 0.06683439, 0.06309574, 0.05956621, 0.056234125, 0.05308844, 0.05011872, 0.047315124, 0.044668354, 0.04216965, 0.039810725, 0.037583742, 0.035481337, 0.033496536, 0.031622775, 0.029853828, 0.028183822, 0.026607247, 0.025118865, 0.02371374, 0.022387212, 0.021134889, 0.01995262, 0.018836489, 0.017782794, 0.01678804, 0.015848929, 0.014962353, 0.014125377, 0.013335214, 0.012589253, 0.01188502, 0.011220186, 0.010592538, 0.01, 0.009440607, 0.0089125065, 0.008413952, 0.007943282, 0.007498941, 0.007079456, 0.00668344, 0.0063095735, 0.005956621, 0.0056234123, 0.0053088428, 0.005011873, 0.0047315126, 0.0044668354, 0.004216964, 0.003981072, 0.0037583741, 0.0035481334, 0.0033496537, 0.0031622767, 0.0029853827, 0.0028183828, 0.0026607246, 0.0025118857, 0.0023713738, 0.0022387211, 0.0021134887, 0.0019952618, 0.0018836485, 0.0017782794, 0.0016788039, 0.0015848937, 0.001496236, 0.0014125376, 0.0013335207, 0.0012589252, 0.001188502, 0.0011220181, 0.0010592537, 0.0009999999, 0.00094406115, 0.0008912511, 0.0008413952, 0.0007943278, 0.00074989407, 0.0007079456, 0.0006683437, 0.00063095737, 0.0005956621, 0.0005623415, 0.00053088454, 0.0005011872, 0.000473151, 0.00044668352, 0.00042169637, 0.00039810702, 0.0003758374, 0.00035481335, 0.00033496553, 0.00031622782, 0.00029853827, 0.00028183826, 0.00026607246, 0.00025118855, 0.00023713727, 0.00022387199, 0.00021134898, 0.00019952627, 0.00018836492, 0.00017782794, 0.00016788038, 0.00015848929, 0.00014962352, 0.0001412537, 0.00013335208, 0.00012589258, 0.00011885024, 0.00011220186, 0.00010592537]).astype('float32')
torch_weights['state_dict']['causal_mask'] =   np.triu(np.ones((1,1,77,77), dtype=np.float16) * -65500.0, k=1).astype(np.float32)
torch_weights['state_dict']['aux_output_conv.weight'] =   np.array([0.14013671875, 0.0711669921875, -0.03271484375, -0.11407470703125, 0.126220703125, 0.10101318359375, 0.034515380859375, -0.1383056640625, 0.126220703125, 0.07733154296875, 0.042633056640625, -0.177978515625]).astype(np.float32) 
torch_weights['state_dict']['aux_output_conv.bias'] =   np.array([0.423828125, 0.471923828125, 0.473876953125]).astype(np.float32) 
torch_weights['state_dict']['alphas_cumprod'] = np.array(_ALPHAS_CUMPROD).astype(np.float32) 
extra_keys = ['temb_coefficients_fp32' , 'causal_mask' , 'aux_output_conv.weight' , 'aux_output_conv.bias', 'alphas_cumprod']

for k in torch_weights['state_dict']:
    if k not in SD_SHAPES and k not in extra_keys:
        continue
    if 'model_ema' in k:
        continue
    np_arr = torch_weights['state_dict'][k]
    key_bytes = np_arr.tobytes()
    shape = list(np_arr.shape)
    if k not in extra_keys:
        assert tuple(shape) == SD_SHAPES[k], ( "shape mismatch at" ,  k , shape , SD_SHAPES[k] )
    dtype = str(np_arr.dtype)
    if dtype == 'int64':
        np_arr = np_arr.astype('float32')
        dtype = 'float32'
    assert dtype in ['float16' , 'float32'] , (dtype, k)
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
