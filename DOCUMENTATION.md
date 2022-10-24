## How to use DiffusionBee

This documentation is written for version 1.1.0. Parts of it may be unapplicable for other versions.

### Installation

On first launch, DiffusionBee will download and install additional data for image generation.

## Generating images

Depending on settings and available computing power it may take a few seconds to a few minutes to generate an image. Image generation may be aborted by pressing the stop button. Use the "save image" link to save the image to a location of your choice.

Clicking on an image opens a separate window displaying the image in full size.

### Text to image

To create an image, simply enter a prompt and press _generate_.

* The **Prompt ideas** button opens a web page where you can browse a gallery for finding useful prompts.
* The **Styles** button provides a palette of often-used terms to add to the prompt.
* The **Advanced options** buttons gives the following options:
  * Num images: The number of images to generate.
  * Image height/width: Sets the dimensions of the image. Note that Stable Diffusion is trained on 512 x 512 (the default setting). Other dimensions may give less good result and take more time.
  * Steps: This corresponds to how many steps are used to improve the image quality. Setting to a low number gives faster image generation, and may be useful while exploring different prompts.
  * Batch size: This tells DiffusionBee to generate multiple images at a time. New batches of images will be created until "num images" have been created. (Just increasing _num images_ is usually a better option.)
  * Guidance scale: This kind of corresponds to how closely Stable Diffusion should stick to the prompt. Higher value means more strict interpretation.
  * Seed: A number between 0 and 4,294,967,295 that is used as starting point for the image generation. If the same seed is used with the same prompt and the same settings (except *steps*, which may vary), the same image will be generated. If left empty, a random seed will be used.

### Image to image

Click on the left pane to upload a sketch starting image (only png supported). Add a prompt description of the desired output and press _generate_. The generated image will be 512 x 512 pixels.

* The **Options** buttons gives the following options:
  * Input strength: This tells DiffusionBee how closely to stick to the sketch input image. For rough sketches you normally want a low value.
  * Num images: The number of images to generate.
  * Steps: This corresponds to how many steps are used to build the image. Setting to a low number gives faster image generation, and may be useful while exploring different prompts.
  * Seed: A number between 0 and 4,294,967,295 that is used as starting point for the image generation. If the same seed is used with the same image, the same prompt and the same settings (except *steps*, which may vary), the same image will be generated. If left empty, a random seed will be used.

#### Inpainting

To use the inpainting functions, select *image to image*, add an image and select *inpainting* below the image. Then scribble in the image to mask the are you wish DiffusionBee to re-paint for you.

You may have better chances of getting inpainting to work well if you use low input strength in the options (0.3 or below), use many steps (50 or more) and mask a larger area than you actually want to replace.

## History

The **History** tab show previously generated images along with prompts and settings (including seed).

## Extra tips

* For prompt ideas and help, check out:
  - [lexica.art](https://lexica.art/)
  - [arthub.ai](https://arthub.ai/)
  - `Prompt Engineering` section at [AssemblyAI](https://www.assemblyai.com/blog/how-to-run-stable-diffusion-locally-to-generate-images/)
* Image generation requires a substantial amount of system memory. Close other applications for a faster generation.
* You can save time while tuning your prompts by lowering the *steps* setting, then turning it back up once you found a good prompt.
* When tuning prompts, make sure that you enter a seed to make it possible to recreate images. If you generate more than one image per seed (via either the Num Images or Batch setting) there will not be a way to tie any of the images generated after the first one to the same seed. For example, if I have Num Images set to 3 and Seed set to 1000, the first of my three generated images will correspond to the seed of 1000, but I won't know the seed for the other two images.
* When _num images_ is set to more than 1, `1234` is added to the seed for each image following the first one. (This can be used to recreate number 4 in a string of images without having to recreate all the previous ones.)
* All created images are stored at `~/.diffusionbee/images/` in your file system. There is no interface in DiffusionBee for deleting images, but they can be deleted manually from this hidden directory.
* The model is stored at `~/.diffusionbee/downloads`. If you already have the model available and don't want to re-download it, move, copy or symlink it to that directory.
* The _Show logs_ menu option shows logs that are mostly useful for developers or for tracking errors. You exit the log by clicking one of the tabs.

## Join the discussion

Join the DiffusionBee discord at https://discord.gg/t6rC5RaJQn
