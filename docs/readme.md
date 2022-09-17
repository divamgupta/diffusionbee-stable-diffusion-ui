# How to use DiffusionBee

## Installation

See documentation on main page.

## Using DiffusionBee

To create an image using DiffusionBee, simply enter a prompt and press "generate". For some tips for writing prompts, see for example ["prompt engineering" section on this page](https://www.assemblyai.com/blog/how-to-run-stable-diffusion-locally-to-generate-images/).

Some advanced options are available:

* Image height/width: Sets the dimensions of the image. Note that Stable Diffusion is trained on 512 x 512 (the default setting). Other dimensions may give poorer result and take more time.
* Steps: This corresponds to how many steps are used to improve the image quality. Setting to a low number gives faster image generation, and may be useful while exploring different prompts.
* Guidance scale: This kind of corresponds to how closely Stable Diffusion should stick to the prompt. Higher value means more strict interpretation.

The tab _Image to Image_ is currently not used. The _Logs_ tab contains logs that are mostly useful for developers or for tracking errors.

As stated in the DiffusionBee window, the application requires quite a bit of CPU power and will run faster if other applications are turned off.

## More advanced tips

All created images are stored at /tmp/samples in your file system, which can be useful for retrieving old images. The directory is wiped every time you reboot your computer.

## Discord

Join the DiffusionBee discord at https://discord.gg/t6rC5RaJQn
