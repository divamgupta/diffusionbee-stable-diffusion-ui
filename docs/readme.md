## How to use DiffusionBee

This documentation is written for version 0.3.0. Parts of it may be unapplicable for other versions.

### Installation

* Download the application and add to your applications directory, then eject the installation drive.
* Start the DiffusionBee application. The first time DiffusionBee will download additional data, which takes some extra time. Following application starts will be quicker.

## Generating images

To create an image using DiffusionBee, simply enter a prompt and press "generate". Depending on settings and available computing power it may take a few seconds to a few minutes to generate an image. Image generation may be aborted by pressing the stop button. Use the "save image" link to save the image to a location of your choice.

### Options and extras

The **Prompt ideas** button opens a web page where you can browse a gallery for finding useful prompts.

The **Styles** button provides a palette of often-used terms to add to the prompt.

The **Advanced options** buttons gives the following options:

* Num images: The number of images to generate.
* Image height/width: Sets the dimensions of the image. Note that Stable Diffusion is trained on 512 x 512 (the default setting). Other dimensions may give less good result and take more time.
* Steps: This corresponds to how many steps are used to improve the image quality. Setting to a low number gives faster image generation, and may be useful while exploring different prompts.
* Batch size: This tells DiffusionBee to generate multiple images at a time. New batches of images will be created until "num images" have been created.
* Guidance scale: This kind of corresponds to how closely Stable Diffusion should stick to the prompt. Higher value means more strict interpretation.
* Seed: A number between 0 and 2^32 - 1 that is used as starting point for the image generation. If the same seed is used with the same prompt, the same image will be generated. If left empty, a random seed will be used.

The **History** tab show previously generated images and the prompts used. If a seed was provided, it too will be available. (If the seed setting was left empty, the random seed will _not_ be visible in the logs for version 0.3.0.)

## Extra tips

* For some tips for writing prompts, see for example [lexica.art](https://lexica.art/), [arthub.ai](https://arthub.ai) or ["prompt engineering" section on this page](https://www.assemblyai.com/blog/how-to-run-stable-diffusion-locally-to-generate-images/).
* As stated in the DiffusionBee window, the application requires quite a bit of CPU power and will run faster if other applications are turned off.
* All created images are stored at `/tmp` in your file system. The directory is wiped every time you reboot your computer.
* The model file is stored at `~/.diffusionbee/downloads`. If you already have the model available and don't want to re-download it, move, copy or symlink it to that directory.
* The tab _Image to Image_ is currently not used.
* The _Show logs_ menu option shows logs that are mostly useful for developers or for tracking errors. You exit the log by clicking **Text to image**.

## Join the discussion

Join the DiffusionBee discord at https://discord.gg/t6rC5RaJQn
