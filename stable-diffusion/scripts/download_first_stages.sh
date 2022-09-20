#!/bin/bash

# Exit on any error
set -e

mkdir -p models/first_stage_models
cd models/first_stage_models/

datasets=(
  "kl-f4"
  "kl-f8"
  "kl-f16"
  "kl-f32"
  "vq-f4"
  "vq-f4-noattn"
  "vq-f8"
  "vq-f8-n256"
  "vq-f16"
)

for dataset in "${datasets[@]}"
do
  mkdir -p "${dataset}"
  cd "${dataset}"
  if [ ! -f model.zip ] ; then
    wget "https://ommer-lab.com/files/latent-diffusion/${dataset}" -O model.zip
    unzip -o model.zip
  fi
  cd ..
done
