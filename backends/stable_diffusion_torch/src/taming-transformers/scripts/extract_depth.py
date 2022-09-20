import os
import torch
import numpy as np
from tqdm import trange
from PIL import Image


def get_state(gpu):
    import torch
    midas = torch.hub.load("intel-isl/MiDaS", "MiDaS")
    if gpu:
        midas.cuda()
    midas.eval()

    midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
    transform = midas_transforms.default_transform

    state = {"model": midas,
             "transform": transform}
    return state


def depth_to_rgba(x):
    assert x.dtype == np.float32
    assert len(x.shape) == 2
    y = x.copy()
    y.dtype = np.uint8
    y = y.reshape(x.shape+(4,))
    return np.ascontiguousarray(y)


def rgba_to_depth(x):
    assert x.dtype == np.uint8
    assert len(x.shape) == 3 and x.shape[2] == 4
    y = x.copy()
    y.dtype = np.float32
    y = y.reshape(x.shape[:2])
    return np.ascontiguousarray(y)


def run(x, state):
    model = state["model"]
    transform = state["transform"]
    hw = x.shape[:2]
    with torch.no_grad():
        prediction = model(transform((x + 1.0) * 127.5).cuda())
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=hw,
            mode="bicubic",
            align_corners=False,
        ).squeeze()
        output = prediction.cpu().numpy()
    return output


def get_filename(relpath, level=-2):
    # save class folder structure and filename:
    fn = relpath.split(os.sep)[level:]
    folder = fn[-2]
    file   = fn[-1].split('.')[0]
    return folder, file


def save_depth(dataset, path, debug=False):
    os.makedirs(path)
    N = len(dset)
    if debug:
        N = 10
    state = get_state(gpu=True)
    for idx in trange(N, desc="Data"):
        ex = dataset[idx]
        image, relpath = ex["image"], ex["relpath"]
        folder, filename = get_filename(relpath)
        # prepare
        folderabspath = os.path.join(path, folder)
        os.makedirs(folderabspath, exist_ok=True)
        savepath = os.path.join(folderabspath, filename)
        # run model
        xout = run(image, state)
        I = depth_to_rgba(xout)
        Image.fromarray(I).save("{}.png".format(savepath))


if __name__ == "__main__":
    from taming.data.imagenet import ImageNetTrain, ImageNetValidation
    out = "data/imagenet_depth"
    if not os.path.exists(out):
        print("Please create a folder or symlink '{}' to extract depth data ".format(out) +
              "(be prepared that the output size will be larger than ImageNet itself).")
        exit(1)

    # go
    dset = ImageNetValidation()
    abspath = os.path.join(out, "val")
    if os.path.exists(abspath):
        print("{} exists - not doing anything.".format(abspath))
    else:
        print("preparing {}".format(abspath))
        save_depth(dset, abspath)
        print("done with validation split")

    dset = ImageNetTrain()
    abspath = os.path.join(out, "train")
    if os.path.exists(abspath):
        print("{} exists - not doing anything.".format(abspath))
    else:
        print("preparing {}".format(abspath))
        save_depth(dset, abspath)
        print("done with train split")

    print("done done.")
