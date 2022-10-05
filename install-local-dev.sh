#!/bin/bash

set -e

# Download stable diffusion info
cd backends/stable_diffusion_torch

echo ">> Downloading stable diffusion code"
# Download the m1-compatible Stable Diffusion sampling infrastructure
git clone https://github.com/magnusviri/stable-diffusion.git
cd stable-diffusion
git checkout apple-mps-support
cd ..

echo ">> Downloading text (CLIP) tokenizer"
# Download the CLIP tokenizer from huggingface hub
git clone https://huggingface.co/openai/clip-vit-base-patch32
mkdir -p HF_weights/
mv clip-vit-base-patch32 HF_weights/clip_tokenizer

echo ">> Downloading model weights (4gb, may take awhile)"
# Download v1.4 model weights (so you can run `python txt2img.py` locally when testing)
wget "https://me.cmdr2.org/stable-diffusion-ui/sd-v1-4.ckpt" -O sd-v1-4.ckpt
mkdir -p models/ldm/stable-diffusion-v1/
ln -s sd-v1-4.ckpt models/ldm/stable-diffusion-v1/model.ckpt


echo ">> Creating environment diffusion bee"
# Create fresh python environment
conda create --name diffusionbee

echo ">> Now run 'conda activate diffusionbee'"
echo ">> Followed by './install-local-dev-2.sh'" 

