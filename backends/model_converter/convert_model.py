import json
import numpy as np
from constants import _ALPHAS_CUMPROD
import sys, getopt 

# python convert_model.py "/Users/divamgupta/Downloads/hollie-mengert.ckpt"  "/Users/divamgupta/Downloads/hollie-mengert.tdict"

# pyinstaller  convert_model.py  --onefile  --noconfirm --clean # build using intel machine so that its cross platform lol

 
from safetensor_wrapper import SafetensorWrapper
from fake_torch import extract_weights_from_checkpoint
from sd_shapes import get_model_type , possible_model_shapes , ctdict_ids
from tdict import TDict



def convert_model(checkpoint_filename=None, out_filename=None,  torch_weights=None):

    if torch_weights is None:
        if checkpoint_filename.lower().endswith(".ckpt"):
            torch_weights = extract_weights_from_checkpoint(open(checkpoint_filename, "rb"))
        elif checkpoint_filename.lower().endswith(".safetensors"):
            torch_weights = SafetensorWrapper(checkpoint_filename)
        else:
            raise ValueError("Invalid import format")

    if 'state_dict' in torch_weights:
        state_dict = torch_weights['state_dict']
    else:
        state_dict = torch_weights

    state_dict['temb_coefficients_fp32'] =  np.array([1.0, 0.94406086, 0.8912509, 0.84139514, 0.7943282, 0.7498942, 0.70794576, 0.6683439, 0.63095737, 0.5956621, 0.56234133, 0.53088444, 0.50118726, 0.47315124, 0.44668362, 0.42169648, 0.39810717, 0.3758374, 0.35481337, 0.33496544, 0.31622776, 0.29853827, 0.2818383, 0.2660725, 0.25118864, 0.23713735, 0.2238721, 0.21134889, 0.19952625, 0.18836491, 0.17782794, 0.16788039, 0.15848932, 0.14962357, 0.14125374, 0.13335215, 0.12589253, 0.11885023, 0.11220184, 0.10592538, 0.099999994, 0.094406076, 0.08912509, 0.0841395, 0.07943282, 0.074989416, 0.07079458, 0.06683439, 0.06309574, 0.05956621, 0.056234125, 0.05308844, 0.05011872, 0.047315124, 0.044668354, 0.04216965, 0.039810725, 0.037583742, 0.035481337, 0.033496536, 0.031622775, 0.029853828, 0.028183822, 0.026607247, 0.025118865, 0.02371374, 0.022387212, 0.021134889, 0.01995262, 0.018836489, 0.017782794, 0.01678804, 0.015848929, 0.014962353, 0.014125377, 0.013335214, 0.012589253, 0.01188502, 0.011220186, 0.010592538, 0.01, 0.009440607, 0.0089125065, 0.008413952, 0.007943282, 0.007498941, 0.007079456, 0.00668344, 0.0063095735, 0.005956621, 0.0056234123, 0.0053088428, 0.005011873, 0.0047315126, 0.0044668354, 0.004216964, 0.003981072, 0.0037583741, 0.0035481334, 0.0033496537, 0.0031622767, 0.0029853827, 0.0028183828, 0.0026607246, 0.0025118857, 0.0023713738, 0.0022387211, 0.0021134887, 0.0019952618, 0.0018836485, 0.0017782794, 0.0016788039, 0.0015848937, 0.001496236, 0.0014125376, 0.0013335207, 0.0012589252, 0.001188502, 0.0011220181, 0.0010592537, 0.0009999999, 0.00094406115, 0.0008912511, 0.0008413952, 0.0007943278, 0.00074989407, 0.0007079456, 0.0006683437, 0.00063095737, 0.0005956621, 0.0005623415, 0.00053088454, 0.0005011872, 0.000473151, 0.00044668352, 0.00042169637, 0.00039810702, 0.0003758374, 0.00035481335, 0.00033496553, 0.00031622782, 0.00029853827, 0.00028183826, 0.00026607246, 0.00025118855, 0.00023713727, 0.00022387199, 0.00021134898, 0.00019952627, 0.00018836492, 0.00017782794, 0.00016788038, 0.00015848929, 0.00014962352, 0.0001412537, 0.00013335208, 0.00012589258, 0.00011885024, 0.00011220186, 0.00010592537]).astype('float32')
    state_dict['causal_mask'] =   np.triu(np.ones((1,1,77,77), dtype=np.float16) * -65500.0, k=1).astype(np.float32)
    state_dict['aux_output_conv.weight'] =   np.array([0.14013671875, 0.0711669921875, -0.03271484375, -0.11407470703125, 0.126220703125, 0.10101318359375, 0.034515380859375, -0.1383056640625, 0.126220703125, 0.07733154296875, 0.042633056640625, -0.177978515625]).astype(np.float32) 
    state_dict['aux_output_conv.bias'] =   np.array([0.423828125, 0.471923828125, 0.473876953125]).astype(np.float32) 
    state_dict['alphas_cumprod'] = np.array(_ALPHAS_CUMPROD).astype(np.float32) 
    state_dict['temb_coefficients_fp16'] =  np.array( [1.0, 0.944, 0.891, 0.8413, 0.7944, 0.75, 0.708, 0.6685, 0.631, 0.5957, 0.5625, 0.531, 0.501, 0.4731, 0.4468, 0.4216, 0.3982, 0.3757, 0.3547, 0.335, 0.3162, 0.2986, 0.2817, 0.266, 0.2512, 0.2372, 0.2239, 0.2113, 0.1996, 0.1884, 0.1779, 0.1678, 0.1584, 0.1497, 0.1412, 0.1333, 0.1259, 0.11884, 0.1122, 0.1059, 0.1, 0.0944, 0.0891, 0.08417, 0.0794, 0.075, 0.0708, 0.06683, 0.0631, 0.05957, 0.05624, 0.0531, 0.0501, 0.0473, 0.04468, 0.04218, 0.03983, 0.0376, 0.0355, 0.0335, 0.03162, 0.02986, 0.02818, 0.02661, 0.02512, 0.02371, 0.02238, 0.02113, 0.01996, 0.01883, 0.01778, 0.01678, 0.01585, 0.01496, 0.01412, 0.013336, 0.01259, 0.01189, 0.01122, 0.01059, 0.01, 0.00944, 0.00891, 0.008415, 0.00794, 0.0075, 0.00708, 0.006683, 0.00631, 0.005955, 0.005623, 0.00531, 0.005013, 0.00473, 0.004467, 0.004215, 0.003983, 0.003757, 0.003548, 0.00335, 0.003162, 0.002985, 0.00282, 0.00266, 0.002512, 0.00237, 0.00224, 0.002113, 0.001995, 0.0018835, 0.001779, 0.001678, 0.001585, 0.001496, 0.001412, 0.001333, 0.001259, 0.001188, 0.001122, 0.00106, 0.001, 0.000944, 0.000891, 0.0008416, 0.0007944, 0.00075, 0.000708, 0.0006685, 0.000631, 0.0005956, 0.000562, 0.0005307, 0.000501, 0.0004733, 0.0004468, 0.0004218, 0.0003982, 0.0003757, 0.0003548, 0.000335, 0.0003161, 0.0002985, 0.0002818, 0.000266, 0.0002513, 0.0002371, 0.0002239, 0.0002114, 0.0001996, 0.0001884, 0.0001779, 0.0001678, 0.0001585, 0.0001496, 0.0001413, 0.0001334, 0.0001259, 0.00011885, 0.0001122, 0.0001059]).astype('float16')

    extra_keys = ['temb_coefficients_fp32', 'temb_coefficients_fp16' , 'causal_mask' , 'aux_output_conv.weight' , 'aux_output_conv.bias', 'alphas_cumprod']



    for k in (list(state_dict.keys())):

        if ".encoder." in k or ".decoder." in k:
            for v , s  in [('q' , 'to_q') , ('v' , 'to_v' ) , ('k' , 'to_k') , ('proj_out' , 'to_out.0')]:
                if f'.{s}.' in k:
                    state_dict[ k.replace(f'.{s}.' , f'.{v}.') ] = state_dict[k]

        if '.norm' in k and '.bias' in k:
            k2 = k.replace(".bias" , ".weight")
            k3 = k.replace(".bias" , ".bias_by_weight")
            state_dict[k3] = state_dict[k]/state_dict[k2]

        if ".ff." in k:
            pp = state_dict[k]
            state_dict[k + "._split_1"] = pp[:pp.shape[0]//2].copy() 
            state_dict[k + "._split_2"] = pp[pp.shape[0]//2:].copy() 

        elif "attn.in_proj" in k and  state_dict[k].shape[0] == 3072 :
            pp = state_dict[k]
            state_dict[k + "._split_1"] = pp[:pp.shape[0]//3].copy()
            state_dict[k + "._split_2"] = pp[pp.shape[0]//3:2*pp.shape[0]//3].copy()
            state_dict[k + "._split_3"] = pp[2*pp.shape[0]//3: ].copy()


    keys_list = list(state_dict.keys())
    mid_key = keys_list[len(keys_list)//2]

    for i in range(1,21):
        nn = 320*i
        dtype = state_dict[mid_key].dtype
        state_dict["zeros_"+str(nn)] = np.zeros(nn).astype(dtype)
        state_dict["ones_"+str(nn)] = np.ones(nn).astype(dtype)

        nn = 128*i
        dtype = state_dict[mid_key].dtype
        state_dict["zeros_"+str(nn)] = np.zeros(nn).astype(dtype)
        state_dict["ones_"+str(nn)] = np.ones(nn).astype(dtype)


    model_type = get_model_type(state_dict)

    if model_type is None:
        raise ValueError("The model is not supported. Please make sure it is a valid SD 1.4/1.5/2.1 .ckpt/safetensor file")

    if "float16" in model_type:
        cur_dtype = "float16"
    elif "float32" in model_type:
        cur_dtype = "float32"
    else:
        assert False

    print("model type " , model_type)

    model_shapes = possible_model_shapes[model_type]
    ctdict_id = ctdict_ids[model_type]

    outfile = TDict(fpath=out_filename)

    outfile.init_write(ctdict_version=ctdict_id )

    for k in model_shapes:
        np_arr = np.copy(state_dict[k])
        np_arr = np.reshape(np_arr , model_shapes[k] )

        if "float" in str(np_arr.dtype):
            np_arr = np_arr.astype(cur_dtype)
        shape = list(np_arr.shape)
        assert tuple(shape) == tuple(model_shapes[k]), ( "shape mismatch at" ,  k , shape , SD_SHAPES[k] )
        outfile.write_key(key=k , tensor=np_arr)

    outfile.finish_write()
    sd_version = model_type.replace("_float16" , "").replace("_float32" , "") 
    if sd_version in ["SD_1x" , "SD_2x"]:
        sd_type = "sd_model"
    elif sd_version in ["SD_1x_inpaint" , "SD_2x_inpaint"]:
        sd_type = "sd_model_inpaint"
    else:
        raise ValueError("Invalid sd_version "+ sd_version)
    model_metadata = {"float_type" : cur_dtype , "sd_type" :sd_version, "type" : sd_type }
    print("__converted_model_data__" , json.dumps(model_metadata))


def usage():
        print("\nConverts .cpkt model files into .tdict model files for Diffusion Bee")
        print("\npython3 convert_py   input.ckpt output.tdict")
        print("\tNormal use.")
        print("\n\tPlease report any errors on the Diffusion Bee GitHub project or the official Discord server.")
        print("\npython3 convert_py --help")
        print("\tDisplays this message")


if __name__ == "__main__":
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "hu", ["help" ])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)
    for o, a in optlist:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"

    if len(args) != 2:
        print("Incorrect number of arguments")
        usage()
        sys.exit(2)

    checkpoint_filename = args[0]
    out_filename = args[1]

    convert_model(checkpoint_filename , out_filename )


