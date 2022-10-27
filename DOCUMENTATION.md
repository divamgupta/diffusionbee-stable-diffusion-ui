## How to use DiffusionBee

This documentation is written for version 1.4.2. Parts of it may be unapplicable for other versions.

### Installation

On first launch, DiffusionBee will download and install additional data for image generation.

## Generating images

Depending on settings and available computing power it may take a few seconds to a few minutes to generate an image. Image generation may be aborted by pressing the stop button. Use the "save image" link to save the image to a location of your choice.

Clicking on an image opens a separate window displaying the image in full size.

### Text to image

The text to image function is used to create an image based on text input only.

To create an image, simply enter a prompt and press _generate_.

* The **Prompt ideas** button opens a web page where you can browse a gallery for finding useful prompts.
* The **Styles** button provides a palette of often-used terms to add to the prompt.
* The **Options** buttons gives the following options:
  * Num images: The number of images to generate.
  * Image height/width: Sets the dimensions of the image. Note that Stable Diffusion is trained on 512 x 512 (the default setting). Other dimensions may give less good result and take more time.
  * Steps: This corresponds to how many steps are used to build information about the image. Setting to a low number gives faster image generation, and may be useful while exploring different prompts.
  * Batch size: This tells DiffusionBee to generate multiple images at a time. New batches of images will be created until "num images" have been created. (Just increasing _num images_ is usually a better option.)
  * Guidance scale: This kind of corresponds to how closely Stable Diffusion should stick to the prompt. Higher value means more strict interpretation.
  * Seed: A number between 0 and 4,294,967,295 that is used as starting point for the image generation. If the same seed is used with the same prompt and the same settings (except *steps*, which may vary), the same image will be generated. If left empty, a random seed will be used.

#### Negative prompt

Enabling the negative prompt option allows adding descriptions of things to avoid including in the image, in combination with the standard prompt. As with the standard prompt the model's understanding of the negative prompt is not perfect, so things described in the negative prompt may still occur in the image.

### Image to image

The image to image function can be used to create an image based on a starting image (often a very rough sketch) combined with a text description.

Click on the left pane to upload a sketch starting image (only png supported). Add a prompt description of the desired output and press _generate_. The generated image will be 512 x 512 pixels.

* The **Options** buttons gives the following options:
  * Input strength: This tells DiffusionBee how closely to stick to the sketch input image. For rough sketches you normally want a low value.
  * Num images: The number of images to generate.
  * Steps: This corresponds to how many steps are used to build the image information. Setting to a low number gives faster image generation, and may be useful while exploring different prompts.
  * Seed: A number between 0 and 4,294,967,295 that is used as starting point for the image generation. If the same seed is used with the same image, the same prompt and the same settings (except *steps*, which may vary), the same image will be generated. If left empty, a random seed will be used.

### Inpainting

The inpainting function is used to replace/repaint parts of an image, for example to add a bow tie to a cat or removing a car from a photo of a street.

To use the inpainting functions, add an image and scribble in the image to mask the are you wish DiffusionBee to re-paint for you. You will usually get a better result if you maska significantly larger area than the part you actually want to change.

**Note that options in *image to image* also affect inpainting.** Using a low input strength (0.3 or below), use many steps (50 or more) may give better results.

### Outpainting

The outpainting function is used to expand an image a larger area.

To use the outpainting functions, add an image and move the 512×512 frame to a place where you want to expand the image, and provide a text prompt. The process may be repeated to expand the image several times and in different directions.

**Note that options in *image to image* also affect outpainting.** Using a high input strength (0.7 or above) may give better results.

## History

The **History** tab show previously generated images along with prompts and settings (including seed).

## Sharing images

Sharing images uploads images along with prompt and settings to arthub.ai. Before uploading you may select which of the images in a batch to upload. You are required to create an account to share images.

## Extra tips

* For prompt ideas and help, check out:
  - [lexica.art](https://lexica.art/)
  - [arthub.ai](https://arthub.ai/)
  - `Prompt Engineering` section at [AssemblyAI](https://www.assemblyai.com/blog/how-to-run-stable-diffusion-locally-to-generate-images/)
* Image generation requires a substantial amount of system memory. Close other applications for a faster generation.
* You can save time while tuning your prompts by lowering the *steps* setting, then turning it back up once you found a good prompt.
* When tuning prompts, make sure that you enter a seed to make it possible to recreate images. If you generate more than one image per seed (via either the Num Images or Batch setting) there will not be a way to tie any of the images generated after the first one to the same seed. For example, if I have Num Images set to 3 and Seed set to 1000, the first of my three generated images will correspond to the seed of 1000, but I won't know the seed for the other two images.
* When _num images_ is set to more than 1, `1234` is added to the seed for each image following the first one. This can be used to recreate number 4 in a string of images without having to recreate all the previous ones.
* All created images are stored at `~/.diffusionbee/images/` in your file system. There is no interface in DiffusionBee for deleting images, but they can be deleted manually from this hidden directory.
* The model is stored at `~/.diffusionbee/downloads`. If you already have the model available and don't want to re-download it, move, copy or symlink it to that directory.
* The _Show logs_ menu option shows logs that are mostly useful for developers or for tracking errors. You exit the log by clicking one of the tabs.

## Join the discussion

Join the DiffusionBee discord at https://discord.gg/t6rC5RaJQn
