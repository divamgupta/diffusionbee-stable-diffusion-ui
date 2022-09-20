import argparse, os, sys, glob, math, time
import torch
import numpy as np
from omegaconf import OmegaConf
import streamlit as st
from streamlit import caching
from PIL import Image
from main import instantiate_from_config, DataModuleFromConfig
from torch.utils.data import DataLoader
from torch.utils.data.dataloader import default_collate


rescale = lambda x: (x + 1.) / 2.


def bchw_to_st(x):
    return rescale(x.detach().cpu().numpy().transpose(0,2,3,1))

def save_img(xstart, fname):
    I = (xstart.clip(0,1)[0]*255).astype(np.uint8)
    Image.fromarray(I).save(fname)



def get_interactive_image(resize=False):
    image = st.file_uploader("Input", type=["jpg", "JPEG", "png"])
    if image is not None:
        image = Image.open(image)
        if not image.mode == "RGB":
            image = image.convert("RGB")
        image = np.array(image).astype(np.uint8)
        print("upload image shape: {}".format(image.shape))
        img = Image.fromarray(image)
        if resize:
            img = img.resize((256, 256))
        image = np.array(img)
        return image


def single_image_to_torch(x, permute=True):
    assert x is not None, "Please provide an image through the upload function"
    x = np.array(x)
    x = torch.FloatTensor(x/255.*2. - 1.)[None,...]
    if permute:
        x = x.permute(0, 3, 1, 2)
    return x


def pad_to_M(x, M):
    hp = math.ceil(x.shape[2]/M)*M-x.shape[2]
    wp = math.ceil(x.shape[3]/M)*M-x.shape[3]
    x = torch.nn.functional.pad(x, (0,wp,0,hp,0,0,0,0))
    return x

@torch.no_grad()
def run_conditional(model, dsets):
    if len(dsets.datasets) > 1:
        split = st.sidebar.radio("Split", sorted(dsets.datasets.keys()))
        dset = dsets.datasets[split]
    else:
        dset = next(iter(dsets.datasets.values()))
    batch_size = 1
    start_index = st.sidebar.number_input("Example Index (Size: {})".format(len(dset)), value=0,
                                          min_value=0,
                                          max_value=len(dset)-batch_size)
    indices = list(range(start_index, start_index+batch_size))

    example = default_collate([dset[i] for i in indices])

    x = model.get_input("image", example).to(model.device)

    cond_key = model.cond_stage_key
    c = model.get_input(cond_key, example).to(model.device)

    scale_factor = st.sidebar.slider("Scale Factor", min_value=0.5, max_value=4.0, step=0.25, value=1.00)
    if scale_factor != 1.0:
        x = torch.nn.functional.interpolate(x, scale_factor=scale_factor, mode="bicubic")
        c = torch.nn.functional.interpolate(c, scale_factor=scale_factor, mode="bicubic")

    quant_z, z_indices = model.encode_to_z(x)
    quant_c, c_indices = model.encode_to_c(c)

    cshape = quant_z.shape

    xrec = model.first_stage_model.decode(quant_z)
    st.write("image: {}".format(x.shape))
    st.image(bchw_to_st(x), clamp=True, output_format="PNG")
    st.write("image reconstruction: {}".format(xrec.shape))
    st.image(bchw_to_st(xrec), clamp=True, output_format="PNG")

    if cond_key == "segmentation":
        # get image from segmentation mask
        num_classes = c.shape[1]
        c = torch.argmax(c, dim=1, keepdim=True)
        c = torch.nn.functional.one_hot(c, num_classes=num_classes)
        c = c.squeeze(1).permute(0, 3, 1, 2).float()
        c = model.cond_stage_model.to_rgb(c)

    st.write(f"{cond_key}: {tuple(c.shape)}")
    st.image(bchw_to_st(c), clamp=True, output_format="PNG")

    idx = z_indices

    half_sample = st.sidebar.checkbox("Image Completion", value=False)
    if half_sample:
        start = idx.shape[1]//2
    else:
        start = 0

    idx[:,start:] = 0
    idx = idx.reshape(cshape[0],cshape[2],cshape[3])
    start_i = start//cshape[3]
    start_j = start %cshape[3]

    if not half_sample and quant_z.shape == quant_c.shape:
        st.info("Setting idx to c_indices")
        idx = c_indices.clone().reshape(cshape[0],cshape[2],cshape[3])

    cidx = c_indices
    cidx = cidx.reshape(quant_c.shape[0],quant_c.shape[2],quant_c.shape[3])

    xstart = model.decode_to_img(idx[:,:cshape[2],:cshape[3]], cshape)
    st.image(bchw_to_st(xstart), clamp=True, output_format="PNG")

    temperature = st.number_input("Temperature", value=1.0)
    top_k = st.number_input("Top k", value=100)
    sample = st.checkbox("Sample", value=True)
    update_every = st.number_input("Update every", value=75)

    st.text(f"Sampling shape ({cshape[2]},{cshape[3]})")

    animate = st.checkbox("animate")
    if animate:
        import imageio
        outvid = "sampling.mp4"
        writer = imageio.get_writer(outvid, fps=25)
    elapsed_t = st.empty()
    info = st.empty()
    st.text("Sampled")
    if st.button("Sample"):
        output = st.empty()
        start_t = time.time()
        for i in range(start_i,cshape[2]-0):
            if i <= 8:
                local_i = i
            elif cshape[2]-i < 8:
                local_i = 16-(cshape[2]-i)
            else:
                local_i = 8
            for j in range(start_j,cshape[3]-0):
                if j <= 8:
                    local_j = j
                elif cshape[3]-j < 8:
                    local_j = 16-(cshape[3]-j)
                else:
                    local_j = 8

                i_start = i-local_i
                i_end = i_start+16
                j_start = j-local_j
                j_end = j_start+16
                elapsed_t.text(f"Time: {time.time() - start_t} seconds")
                info.text(f"Step: ({i},{j}) | Local: ({local_i},{local_j}) | Crop: ({i_start}:{i_end},{j_start}:{j_end})")
                patch = idx[:,i_start:i_end,j_start:j_end]
                patch = patch.reshape(patch.shape[0],-1)
                cpatch = cidx[:, i_start:i_end, j_start:j_end]
                cpatch = cpatch.reshape(cpatch.shape[0], -1)
                patch = torch.cat((cpatch, patch), dim=1)
                logits,_ = model.transformer(patch[:,:-1])
                logits = logits[:, -256:, :]
                logits = logits.reshape(cshape[0],16,16,-1)
                logits = logits[:,local_i,local_j,:]

                logits = logits/temperature

                if top_k is not None:
                    logits = model.top_k_logits(logits, top_k)
                # apply softmax to convert to probabilities
                probs = torch.nn.functional.softmax(logits, dim=-1)
                # sample from the distribution or take the most likely
                if sample:
                    ix = torch.multinomial(probs, num_samples=1)
                else:
                    _, ix = torch.topk(probs, k=1, dim=-1)
                idx[:,i,j] = ix

                if (i*cshape[3]+j)%update_every==0:
                    xstart = model.decode_to_img(idx[:, :cshape[2], :cshape[3]], cshape,)

                    xstart = bchw_to_st(xstart)
                    output.image(xstart, clamp=True, output_format="PNG")

                    if animate:
                        writer.append_data((xstart[0]*255).clip(0, 255).astype(np.uint8))

        xstart = model.decode_to_img(idx[:,:cshape[2],:cshape[3]], cshape)
        xstart = bchw_to_st(xstart)
        output.image(xstart, clamp=True, output_format="PNG")
        #save_img(xstart, "full_res_sample.png")
        if animate:
            writer.close()
            st.video(outvid)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--resume",
        type=str,
        nargs="?",
        help="load from logdir or checkpoint in logdir",
    )
    parser.add_argument(
        "-b",
        "--base",
        nargs="*",
        metavar="base_config.yaml",
        help="paths to base configs. Loaded from left-to-right. "
        "Parameters can be overwritten or added with command-line options of the form `--key value`.",
        default=list(),
    )
    parser.add_argument(
        "-c",
        "--config",
        nargs="?",
        metavar="single_config.yaml",
        help="path to single config. If specified, base configs will be ignored "
        "(except for the last one if left unspecified).",
        const=True,
        default="",
    )
    parser.add_argument(
        "--ignore_base_data",
        action="store_true",
        help="Ignore data specification from base configs. Useful if you want "
        "to specify a custom datasets on the command line.",
    )
    return parser


def load_model_from_config(config, sd, gpu=True, eval_mode=True):
    if "ckpt_path" in config.params:
        st.warning("Deleting the restore-ckpt path from the config...")
        config.params.ckpt_path = None
    if "downsample_cond_size" in config.params:
        st.warning("Deleting downsample-cond-size from the config and setting factor=0.5 instead...")
        config.params.downsample_cond_size = -1
        config.params["downsample_cond_factor"] = 0.5
    try:
        if "ckpt_path" in config.params.first_stage_config.params:
            config.params.first_stage_config.params.ckpt_path = None
            st.warning("Deleting the first-stage restore-ckpt path from the config...")
        if "ckpt_path" in config.params.cond_stage_config.params:
            config.params.cond_stage_config.params.ckpt_path = None
            st.warning("Deleting the cond-stage restore-ckpt path from the config...")
    except:
        pass

    model = instantiate_from_config(config)
    if sd is not None:
        missing, unexpected = model.load_state_dict(sd, strict=False)
        st.info(f"Missing Keys in State Dict: {missing}")
        st.info(f"Unexpected Keys in State Dict: {unexpected}")
    if gpu:
        model.cuda()
    if eval_mode:
        model.eval()
    return {"model": model}


def get_data(config):
    # get data
    data = instantiate_from_config(config.data)
    data.prepare_data()
    data.setup()
    return data


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def load_model_and_dset(config, ckpt, gpu, eval_mode):
    # get data
    dsets = get_data(config)   # calls data.config ...

    # now load the specified checkpoint
    if ckpt:
        pl_sd = torch.load(ckpt, map_location="cpu")
        global_step = pl_sd["global_step"]
    else:
        pl_sd = {"state_dict": None}
        global_step = None
    model = load_model_from_config(config.model,
                                   pl_sd["state_dict"],
                                   gpu=gpu,
                                   eval_mode=eval_mode)["model"]
    return dsets, model, global_step


if __name__ == "__main__":
    sys.path.append(os.getcwd())

    parser = get_parser()

    opt, unknown = parser.parse_known_args()

    ckpt = None
    if opt.resume:
        if not os.path.exists(opt.resume):
            raise ValueError("Cannot find {}".format(opt.resume))
        if os.path.isfile(opt.resume):
            paths = opt.resume.split("/")
            try:
                idx = len(paths)-paths[::-1].index("logs")+1
            except ValueError:
                idx = -2 # take a guess: path/to/logdir/checkpoints/model.ckpt
            logdir = "/".join(paths[:idx])
            ckpt = opt.resume
        else:
            assert os.path.isdir(opt.resume), opt.resume
            logdir = opt.resume.rstrip("/")
            ckpt = os.path.join(logdir, "checkpoints", "last.ckpt")
        print(f"logdir:{logdir}")
        base_configs = sorted(glob.glob(os.path.join(logdir, "configs/*-project.yaml")))
        opt.base = base_configs+opt.base

    if opt.config:
        if type(opt.config) == str:
            opt.base = [opt.config]
        else:
            opt.base = [opt.base[-1]]

    configs = [OmegaConf.load(cfg) for cfg in opt.base]
    cli = OmegaConf.from_dotlist(unknown)
    if opt.ignore_base_data:
        for config in configs:
            if hasattr(config, "data"): del config["data"]
    config = OmegaConf.merge(*configs, cli)

    st.sidebar.text(ckpt)
    gs = st.sidebar.empty()
    gs.text(f"Global step: ?")
    st.sidebar.text("Options")
    #gpu = st.sidebar.checkbox("GPU", value=True)
    gpu = True
    #eval_mode = st.sidebar.checkbox("Eval Mode", value=True)
    eval_mode = True
    #show_config = st.sidebar.checkbox("Show Config", value=False)
    show_config = False
    if show_config:
        st.info("Checkpoint: {}".format(ckpt))
        st.json(OmegaConf.to_container(config))

    dsets, model, global_step = load_model_and_dset(config, ckpt, gpu, eval_mode)
    gs.text(f"Global step: {global_step}")
    run_conditional(model, dsets)
