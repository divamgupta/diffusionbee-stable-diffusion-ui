import argparse, os, sys, glob
import torch
import time
import numpy as np
from omegaconf import OmegaConf
from PIL import Image
from tqdm import tqdm, trange
from einops import repeat

from main import instantiate_from_config
from taming.modules.transformer.mingpt import sample_with_past


rescale = lambda x: (x + 1.) / 2.


def chw_to_pillow(x):
    return Image.fromarray((255*rescale(x.detach().cpu().numpy().transpose(1,2,0))).clip(0,255).astype(np.uint8))


@torch.no_grad()
def sample_classconditional(model, batch_size, class_label, steps=256, temperature=None, top_k=None, callback=None,
                            dim_z=256, h=16, w=16, verbose_time=False, top_p=None):
    log = dict()
    assert type(class_label) == int, f'expecting type int but type is {type(class_label)}'
    qzshape = [batch_size, dim_z, h, w]
    assert not model.be_unconditional, 'Expecting a class-conditional Net2NetTransformer.'
    c_indices = repeat(torch.tensor([class_label]), '1 -> b 1', b=batch_size).to(model.device)  # class token
    t1 = time.time()
    index_sample = sample_with_past(c_indices, model.transformer, steps=steps,
                                    sample_logits=True, top_k=top_k, callback=callback,
                                    temperature=temperature, top_p=top_p)
    if verbose_time:
        sampling_time = time.time() - t1
        print(f"Full sampling takes about {sampling_time:.2f} seconds.")
    x_sample = model.decode_to_img(index_sample, qzshape)
    log["samples"] = x_sample
    log["class_label"] = c_indices
    return log


@torch.no_grad()
def sample_unconditional(model, batch_size, steps=256, temperature=None, top_k=None, top_p=None, callback=None,
                         dim_z=256, h=16, w=16, verbose_time=False):
    log = dict()
    qzshape = [batch_size, dim_z, h, w]
    assert model.be_unconditional, 'Expecting an unconditional model.'
    c_indices = repeat(torch.tensor([model.sos_token]), '1 -> b 1', b=batch_size).to(model.device)  # sos token
    t1 = time.time()
    index_sample = sample_with_past(c_indices, model.transformer, steps=steps,
                                    sample_logits=True, top_k=top_k, callback=callback,
                                    temperature=temperature, top_p=top_p)
    if verbose_time:
        sampling_time = time.time() - t1
        print(f"Full sampling takes about {sampling_time:.2f} seconds.")
    x_sample = model.decode_to_img(index_sample, qzshape)
    log["samples"] = x_sample
    return log


@torch.no_grad()
def run(logdir, model, batch_size, temperature, top_k, unconditional=True, num_samples=50000,
        given_classes=None, top_p=None):
    batches = [batch_size for _ in range(num_samples//batch_size)] + [num_samples % batch_size]
    if not unconditional:
        assert given_classes is not None
        print("Running in pure class-conditional sampling mode. I will produce "
              f"{num_samples} samples for each of the {len(given_classes)} classes, "
              f"i.e. {num_samples*len(given_classes)} in total.")
        for class_label in tqdm(given_classes, desc="Classes"):
            for n, bs in tqdm(enumerate(batches), desc="Sampling Class"):
                if bs == 0: break
                logs = sample_classconditional(model, batch_size=bs, class_label=class_label,
                                               temperature=temperature, top_k=top_k, top_p=top_p)
                save_from_logs(logs, logdir, base_count=n * batch_size, cond_key=logs["class_label"])
    else:
        print(f"Running in unconditional sampling mode, producing {num_samples} samples.")
        for n, bs in tqdm(enumerate(batches), desc="Sampling"):
            if bs == 0: break
            logs = sample_unconditional(model, batch_size=bs, temperature=temperature, top_k=top_k, top_p=top_p)
            save_from_logs(logs, logdir, base_count=n * batch_size)


def save_from_logs(logs, logdir, base_count, key="samples", cond_key=None):
    xx = logs[key]
    for i, x in enumerate(xx):
        x = chw_to_pillow(x)
        count = base_count + i
        if cond_key is None:
            x.save(os.path.join(logdir, f"{count:06}.png"))
        else:
            condlabel = cond_key[i]
            if type(condlabel) == torch.Tensor: condlabel = condlabel.item()
            os.makedirs(os.path.join(logdir, str(condlabel)), exist_ok=True)
            x.save(os.path.join(logdir, str(condlabel), f"{count:06}.png"))


def get_parser():
    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif v.lower() in ("no", "false", "f", "n", "0"):
            return False
        else:
            raise argparse.ArgumentTypeError("Boolean value expected.")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--resume",
        type=str,
        nargs="?",
        help="load from logdir or checkpoint in logdir",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        type=str,
        nargs="?",
        help="path where the samples will be logged to.",
        default=""
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
        "-n",
        "--num_samples",
        type=int,
        nargs="?",
        help="num_samples to draw",
        default=50000
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        nargs="?",
        help="the batch size",
        default=25
    )
    parser.add_argument(
        "-k",
        "--top_k",
        type=int,
        nargs="?",
        help="top-k value to sample with",
        default=250,
    )
    parser.add_argument(
        "-t",
        "--temperature",
        type=float,
        nargs="?",
        help="temperature value to sample with",
        default=1.0
    )
    parser.add_argument(
        "-p",
        "--top_p",
        type=float,
        nargs="?",
        help="top-p value to sample with",
        default=1.0
    )
    parser.add_argument(
        "--classes",
        type=str,
        nargs="?",
        help="specify comma-separated classes to sample from. Uses 1000 classes per default.",
        default="imagenet"
    )
    return parser


def load_model_from_config(config, sd, gpu=True, eval_mode=True):
    model = instantiate_from_config(config)
    if sd is not None:
        model.load_state_dict(sd)
    if gpu:
        model.cuda()
    if eval_mode:
        model.eval()
    return {"model": model}


def load_model(config, ckpt, gpu, eval_mode):
    # load the specified checkpoint
    if ckpt:
        pl_sd = torch.load(ckpt, map_location="cpu")
        global_step = pl_sd["global_step"]
        print(f"loaded model from global step {global_step}.")
    else:
        pl_sd = {"state_dict": None}
        global_step = None
    model = load_model_from_config(config.model, pl_sd["state_dict"], gpu=gpu, eval_mode=eval_mode)["model"]
    return model, global_step


if __name__ == "__main__":
    sys.path.append(os.getcwd())
    parser = get_parser()

    opt, unknown = parser.parse_known_args()
    assert opt.resume

    ckpt = None

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

    base_configs = sorted(glob.glob(os.path.join(logdir, "configs/*-project.yaml")))
    opt.base = base_configs+opt.base

    configs = [OmegaConf.load(cfg) for cfg in opt.base]
    cli = OmegaConf.from_dotlist(unknown)
    config = OmegaConf.merge(*configs, cli)

    model, global_step = load_model(config, ckpt, gpu=True, eval_mode=True)

    if opt.outdir:
        print(f"Switching logdir from '{logdir}' to '{opt.outdir}'")
        logdir = opt.outdir

    if opt.classes == "imagenet":
        given_classes = [i for i in range(1000)]
    else:
        cls_str = opt.classes
        assert not cls_str.endswith(","), 'class string should not end with a ","'
        given_classes = [int(c) for c in cls_str.split(",")]

    logdir = os.path.join(logdir, "samples", f"top_k_{opt.top_k}_temp_{opt.temperature:.2f}_top_p_{opt.top_p}",
                          f"{global_step}")

    print(f"Logging to {logdir}")
    os.makedirs(logdir, exist_ok=True)

    run(logdir, model, opt.batch_size, opt.temperature, opt.top_k, unconditional=model.be_unconditional,
        given_classes=given_classes, num_samples=opt.num_samples, top_p=opt.top_p)

    print("done.")
