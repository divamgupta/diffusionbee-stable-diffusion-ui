import sys, os
import numpy as np
import scipy
import torch
import torch.nn as nn
from scipy import ndimage
from tqdm import tqdm, trange
from PIL import Image
import torch.hub
import torchvision
import torch.nn.functional as F

# download deeplabv2_resnet101_msc-cocostuff164k-100000.pth from
# https://github.com/kazuto1011/deeplab-pytorch/releases/download/v1.0/deeplabv2_resnet101_msc-cocostuff164k-100000.pth
# and put the path here
CKPT_PATH = "TODO"

rescale = lambda x: (x + 1.) / 2.

def rescale_bgr(x):
    x = (x+1)*127.5
    x = torch.flip(x, dims=[0])
    return x


class COCOStuffSegmenter(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.n_labels = 182
        model = torch.hub.load("kazuto1011/deeplab-pytorch", "deeplabv2_resnet101", n_classes=self.n_labels)
        ckpt_path = CKPT_PATH
        model.load_state_dict(torch.load(ckpt_path))
        self.model = model

        normalize = torchvision.transforms.Normalize(mean=self.mean, std=self.std)
        self.image_transform = torchvision.transforms.Compose([
            torchvision.transforms.Lambda(lambda image: torch.stack(
                [normalize(rescale_bgr(x)) for x in image]))
        ])

    def forward(self, x, upsample=None):
        x = self._pre_process(x)
        x = self.model(x)
        if upsample is not None:
            x = torch.nn.functional.upsample_bilinear(x, size=upsample)
        return x

    def _pre_process(self, x):
        x = self.image_transform(x)
        return x

    @property
    def mean(self):
        # bgr
        return [104.008, 116.669, 122.675]

    @property
    def std(self):
        return [1.0, 1.0, 1.0]

    @property
    def input_size(self):
        return [3, 224, 224]


def run_model(img, model):
    model = model.eval()
    with torch.no_grad():
        segmentation = model(img, upsample=(img.shape[2], img.shape[3]))
        segmentation = torch.argmax(segmentation, dim=1, keepdim=True)
    return segmentation.detach().cpu()


def get_input(batch, k):
    x = batch[k]
    if len(x.shape) == 3:
        x = x[..., None]
    x = x.permute(0, 3, 1, 2).to(memory_format=torch.contiguous_format)
    return x.float()


def save_segmentation(segmentation, path):
    # --> class label to uint8, save as png
    os.makedirs(os.path.dirname(path), exist_ok=True)
    assert len(segmentation.shape)==4
    assert segmentation.shape[0]==1
    for seg in segmentation:
        seg = seg.permute(1,2,0).numpy().squeeze().astype(np.uint8)
        seg = Image.fromarray(seg)
        seg.save(path)


def iterate_dataset(dataloader, destpath, model):
    os.makedirs(destpath, exist_ok=True)
    num_processed = 0
    for i, batch in tqdm(enumerate(dataloader), desc="Data"):
        try:
            img = get_input(batch, "image")
            img = img.cuda()
            seg = run_model(img, model)

            path = batch["relative_file_path_"][0]
            path = os.path.splitext(path)[0]

            path = os.path.join(destpath, path + ".png")
            save_segmentation(seg, path)
            num_processed += 1
        except Exception as e:
            print(e)
            print("but anyhow..")

    print("Processed {} files. Bye.".format(num_processed))


from taming.data.sflckr import Examples
from torch.utils.data import DataLoader

if __name__ == "__main__":
    dest = sys.argv[1]
    batchsize = 1
    print("Running with batch-size {}, saving to {}...".format(batchsize, dest))

    model = COCOStuffSegmenter({}).cuda()
    print("Instantiated model.")

    dataset = Examples()
    dloader = DataLoader(dataset, batch_size=batchsize)
    iterate_dataset(dataloader=dloader, destpath=dest, model=model)
    print("done.")
