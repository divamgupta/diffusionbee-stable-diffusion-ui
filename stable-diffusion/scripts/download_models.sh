#!/bin/bash

# Exit on any error
set -e
datasets=(
  "celeba"
  "ffhq"
  "lsun_churches"
  "lsun_bedrooms"
)

mkdir -p ./models/ldm/
cd ./models/ldm

# Download datasets & unzip them
for dataset in "${datasets[@]}" ; do
  if [ ! -f "${dataset}/${dataset}-256.zip" ] ; then
    mkdir -p "${dataset}"
    wget "https://ommer-lab.com/files/latent-diffusion/${dataset}.zip" -O "${dataset}/${dataset}-256.zip"
    cd "${dataset}"
    unzip "${dataset}-256.zip"
    cd ..
  fi
done

# Hosted model name vs target directory for downloading
models=(
  "text2img::text2img256"
  "cin::cin256"
  "semantic_synthesis::semantic_synthesis512"
  "semantic_synthesis256::semantic_synthesis256"
  "sr_bsr::bsr_sr"
  "layout2img_model::layout2img-openimages256"
  "inpainting_big::inpainting_big"
)

# Download models & unzip them
for index in "${models[@]}" ; do
  KEY="${index%%::*}"
  VALUE="${index##*::}"

  echo "${KEY} -> ${VALUE}"
  if [ ! -f "${VALUE}/model.zip" ] ; then
    mkdir -p "${VALUE}"
    wget "https://ommer-lab.com/files/latent-diffusion/${KEY}.zip" -O "${VALUE}/model.zip"
    cd ${VALUE}
    unzip model.zip
    cd ..
  fi
done

