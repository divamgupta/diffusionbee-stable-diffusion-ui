#!/bin/bash
set -e

cd backends/stable_diffusion_torch/

echo ">> Installing pytorch"
conda install pytorch torchvision torchaudio -c pytorch-nightly

echo ">> Downloading custom python dependencies, might have to pass (i) to ignore existing packages"
pip install -r requirements.txt

cd ../..

echo ">> Setting up electron app"
cd electron_app
npm i

echo ">> Starting electron app"
npm run electron:serve

