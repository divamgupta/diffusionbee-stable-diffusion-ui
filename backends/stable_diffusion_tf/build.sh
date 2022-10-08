pyinstaller   diffusionbee_backend.py  --collect-all tensorflow --collect-all tensorflow-plugins  --noconfirm --clean
cp stable_diffusion_tf/clip_tokenizer/bpe_simple_vocab_16e6.txt.gz ./dist/diffusionbee_backend

cp -r ../realesrgan_ncnn/models  ./dist/diffusionbee_backend/models 
cp  ../realesrgan_ncnn/realesrgan_ncnn_macos  ./dist/diffusionbee_backend/realesrgan_ncnn_macos 

