import glob
import os
import sys
from itertools import product
from pathlib import Path
from typing import Literal, List, Optional, Tuple

import numpy as np
import torch
from omegaconf import OmegaConf
from pytorch_lightning import seed_everything
from torch import Tensor
from torchvision.utils import save_image
from tqdm import tqdm

from scripts.make_samples import get_parser, load_model_and_dset
from taming.data.conditional_builder.objects_center_points import ObjectsCenterPointsConditionalBuilder
from taming.data.helper_types import BoundingBox, Annotation
from taming.data.annotated_objects_dataset import AnnotatedObjectsDataset
from taming.models.cond_transformer import Net2NetTransformer

seed_everything(42424242)
device: Literal['cuda', 'cpu'] = 'cuda'
first_stage_factor = 16
trained_on_res = 256


def _helper(coord: int, coord_max: int, coord_window: int) -> (int, int):
    assert 0 <= coord < coord_max
    coord_desired_center = (coord_window - 1) // 2
    return np.clip(coord - coord_desired_center, 0, coord_max - coord_window)


def get_crop_coordinates(x: int, y: int) -> BoundingBox:
    WIDTH, HEIGHT = desired_z_shape[1], desired_z_shape[0]
    x0 = _helper(x, WIDTH, first_stage_factor) / WIDTH
    y0 = _helper(y, HEIGHT, first_stage_factor) / HEIGHT
    w = first_stage_factor / WIDTH
    h = first_stage_factor / HEIGHT
    return x0, y0, w, h


def get_z_indices_crop_out(z_indices: Tensor, predict_x: int, predict_y: int) -> Tensor:
    WIDTH, HEIGHT = desired_z_shape[1], desired_z_shape[0]
    x0 = _helper(predict_x, WIDTH, first_stage_factor)
    y0 = _helper(predict_y, HEIGHT, first_stage_factor)
    no_images = z_indices.shape[0]
    cut_out_1 = z_indices[:, y0:predict_y, x0:x0+first_stage_factor].reshape((no_images, -1))
    cut_out_2 = z_indices[:, predict_y, x0:predict_x]
    return torch.cat((cut_out_1, cut_out_2), dim=1)


@torch.no_grad()
def sample(model: Net2NetTransformer, annotations: List[Annotation], dataset: AnnotatedObjectsDataset,
           conditional_builder: ObjectsCenterPointsConditionalBuilder, no_samples: int,
           temperature: float, top_k: int) -> Tensor:
    x_max, y_max = desired_z_shape[1], desired_z_shape[0]

    annotations = [a._replace(category_no=dataset.get_category_number(a.category_id)) for a in annotations]

    recompute_conditional = any((desired_resolution[0] > trained_on_res, desired_resolution[1] > trained_on_res))
    if not recompute_conditional:
        crop_coordinates = get_crop_coordinates(0, 0)
        conditional_indices = conditional_builder.build(annotations, crop_coordinates)
        c_indices = conditional_indices.to(device).repeat(no_samples, 1)
        z_indices = torch.zeros((no_samples, 0), device=device).long()
        output_indices = model.sample(z_indices, c_indices, steps=x_max*y_max, temperature=temperature,
                                      sample=True, top_k=top_k)
    else:
        output_indices = torch.zeros((no_samples, y_max, x_max), device=device).long()
        for predict_y, predict_x in tqdm(product(range(y_max), range(x_max)), desc='sampling_image', total=x_max*y_max):
            crop_coordinates = get_crop_coordinates(predict_x, predict_y)
            z_indices = get_z_indices_crop_out(output_indices, predict_x, predict_y)
            conditional_indices = conditional_builder.build(annotations, crop_coordinates)
            c_indices = conditional_indices.to(device).repeat(no_samples, 1)
            new_index = model.sample(z_indices, c_indices, steps=1, temperature=temperature, sample=True, top_k=top_k)
            output_indices[:, predict_y, predict_x] = new_index[:, -1]
    z_shape = (
        no_samples,
        model.first_stage_model.quantize.e_dim,  # codebook embed_dim
        desired_z_shape[0],  # z_height
        desired_z_shape[1]  # z_width
    )
    x_sample = model.decode_to_img(output_indices, z_shape) * 0.5 + 0.5
    x_sample = x_sample.to('cpu')

    plotter = conditional_builder.plot
    figure_size = (x_sample.shape[2], x_sample.shape[3])
    scene_graph = conditional_builder.build(annotations, (0., 0., 1., 1.))
    plot = plotter(scene_graph, dataset.get_textual_label_for_category_no, figure_size)
    return torch.cat((x_sample, plot.unsqueeze(0)))


def get_resolution(resolution_str: str) -> (Tuple[int, int], Tuple[int, int]):
    if not resolution_str.count(',') == 1:
        raise ValueError("Give resolution as in 'height,width'")
    res_h, res_w = resolution_str.split(',')
    res_h = max(int(res_h), trained_on_res)
    res_w = max(int(res_w), trained_on_res)
    z_h = int(round(res_h/first_stage_factor))
    z_w = int(round(res_w/first_stage_factor))
    return (z_h, z_w), (z_h*first_stage_factor, z_w*first_stage_factor)


def add_arg_to_parser(parser):
    parser.add_argument(
        "-R",
        "--resolution",
        type=str,
        default='256,256',
        help=f"give resolution in multiples of {first_stage_factor}, default is '256,256'",
    )
    parser.add_argument(
        "-C",
        "--conditional",
        type=str,
        default='objects_bbox',
        help=f"objects_bbox or objects_center_points",
    )
    parser.add_argument(
        "-N",
        "--n_samples_per_layout",
        type=int,
        default=4,
        help=f"how many samples to generate per layout",
    )
    return parser


if __name__ == "__main__":
    sys.path.append(os.getcwd())

    parser = get_parser()
    parser = add_arg_to_parser(parser)

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
                idx = -2  # take a guess: path/to/logdir/checkpoints/model.ckpt
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
            if hasattr(config, "data"):
                del config["data"]
    config = OmegaConf.merge(*configs, cli)
    desired_z_shape, desired_resolution = get_resolution(opt.resolution)
    conditional = opt.conditional

    print(ckpt)
    gpu = True
    eval_mode = True
    show_config = False
    if show_config:
        print(OmegaConf.to_container(config))

    dsets, model, global_step = load_model_and_dset(config, ckpt, gpu, eval_mode)
    print(f"Global step: {global_step}")

    data_loader = dsets.val_dataloader()
    print(dsets.datasets["validation"].conditional_builders)
    conditional_builder = dsets.datasets["validation"].conditional_builders[conditional]

    outdir = Path(opt.outdir).joinpath(f"{global_step:06}_{opt.top_k}_{opt.temperature}")
    outdir.mkdir(exist_ok=True, parents=True)
    print("Writing samples to ", outdir)

    p_bar_1 = tqdm(enumerate(iter(data_loader)), desc='batch', total=len(data_loader))
    for batch_no, batch in p_bar_1:
        save_img: Optional[Tensor] = None
        for i, annotations in tqdm(enumerate(batch['annotations']), desc='within_batch', total=data_loader.batch_size):
            imgs = sample(model, annotations, dsets.datasets["validation"], conditional_builder,
                          opt.n_samples_per_layout, opt.temperature, opt.top_k)
            save_image(imgs, outdir.joinpath(f'{batch_no:04}_{i:02}.png'), n_row=opt.n_samples_per_layout+1)
