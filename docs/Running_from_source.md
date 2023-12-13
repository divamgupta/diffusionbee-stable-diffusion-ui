## How to run DiffusionBee from source 

Install the following
- Miniforge 
- Nodejs v16


Clone the repo: 

```
git clone https://github.com/divamgupta/diffusionbee-stable-diffusion-ui

```




Create the conda environment and activate it:

```
conda create -n diffusion_bee_env  python=3.9.10
conda activate diffusion_bee_env

```

Install the python packages :

```
cd diffusionbee-stable-diffusion-ui/backends/stable_diffusion
pip install -r requirements.txt

```

Install the npm packages 

```
cd diffusionbee-stable-diffusion-ui/electron_app
npm install
```


Run the app

```
npm run electron:serve 

```