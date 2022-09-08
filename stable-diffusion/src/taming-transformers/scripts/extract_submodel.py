import torch
import sys

if __name__ == "__main__":
    inpath = sys.argv[1]
    outpath = sys.argv[2]
    submodel = "cond_stage_model"
    if len(sys.argv) > 3:
        submodel = sys.argv[3]

    print("Extracting {} from {} to {}.".format(submodel, inpath, outpath))

    sd = torch.load(inpath, map_location="cpu")
    new_sd = {"state_dict": dict((k.split(".", 1)[-1],v)
                                 for k,v in sd["state_dict"].items()
                                 if k.startswith("cond_stage_model"))}
    torch.save(new_sd, outpath)
