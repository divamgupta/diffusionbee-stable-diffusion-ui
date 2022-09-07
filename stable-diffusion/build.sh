pyinstaller txt2img.py   --collect-all  huggingface_hub --noconfirm --clean  --collect-all  tqdm --collect-all  regex --collect-all  requests --collect-all  packaging --collect-all  filelock --collect-all  numpy --collect-all  tokenizers --collect-all cv2

mkdir dist/txt2img/clip
cp src/clip/clip/bpe_simple_vocab_16e6.txt.gz dist/txt2img/clip/bpe_simple_vocab_16e6.txt.gz
cp -r configs dist/txt2img/configs
cp -r HF_weights dist/txt2img/HF_weights
mkdir dist/txt2img/models

echo "Right now you gotta copy the weights"