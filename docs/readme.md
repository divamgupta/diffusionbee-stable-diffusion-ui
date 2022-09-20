# How to use DiffusionBee

## Installation

* Download the application and add to your applications directory, then eject the installation drive.
* Start the DiffusionBee application. The first time DiffusionBee will download additional data, which takes some extra time. Following application starts will be quicker.

## Generating images

To create an image using DiffusionBee, simply enter a prompt and press "generate". Depending on settings and available computing power it may take a few seconds to a few minutes to generate an image. Use the "save image" link to save the image to a location of your choice.

Some options are available:

* Image height/width: Sets the dimensions of the image. Note that Stable Diffusion is trained on 512 x 512 (the default setting). Other dimensions may give less good result and take more time.
* Steps: This corresponds to how many steps are used to improve the image quality. Setting to a low number gives faster image generation, and may be useful while exploring different prompts.
* Guidance scale: This kind of corresponds to how closely Stable Diffusion should stick to the prompt. Higher value means more strict interpretation.

## Extra tips

* For some tips for writing prompts, see for example [lexica.art](https://lexica.art/), [arthub.ai](https://arthub.ai) or ["prompt engineering" section on this page](https://www.assemblyai.com/blog/how-to-run-stable-diffusion-locally-to-generate-images/).
* As stated in the DiffusionBee window, the application requires quite a bit of CPU power and will run faster if other applications are turned off.
* All created images are stored at `/tmp/samples` in your file system, which can be useful for retrieving old images. The directory is wiped every time you reboot your computer.
* The model file is stored at `~/.diffusionbee/downloads`. If you already have the model available and don't want to re-download it, move, copy or symlink it to that directory.
* The tab _Image to Image_ is currently not used. The _Logs_ tab contains logs that are mostly useful for developers or for tracking errors.

## Join the discussion

Join the DiffusionBee discord at https://discord.gg/t6rC5RaJQn
