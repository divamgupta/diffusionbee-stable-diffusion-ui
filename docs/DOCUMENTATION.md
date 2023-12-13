## How to use DiffusionBee

This documentation is written for version 1.5.1. Parts of it may be unapplicable for other versions.

### Installation

On first launch, DiffusionBee will download and install additional data for image generation.

### Updates

DiffusionBee occasionally receives updates to add new features and improve performance. When prompted on startup, re-download the application from the site, and replace the new file in the location of the old one. Your history and models will be saved.

## Generating images

Depending on settings and available computing power it may take a few seconds to a few minutes to generate an image. Image generation may be aborted by pressing the stop button. Use the "save image" link to save the image to a location of your choice.

Clicking on an image opens a separate window displaying the image in full size.

### Text to image
<img width="500" alt="Image of text to image" src="https://user-images.githubusercontent.com/105890749/198898577-1852a780-47b6-4d82-98b7-715b0386e44d.png">

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
<img width="300" alt="Image of Negative Prompt" src="https://user-images.githubusercontent.com/105890749/198899943-35b66e59-4a89-4770-b939-fb1d8de541ef.png">

Enabling the negative prompt option allows adding descriptions of things to avoid including in the image, in combination with the standard prompt. As with the standard prompt the model's understanding of the negative prompt is not perfect, so things described in the negative prompt may still occur in the image.

### Image to image
<img width="500" alt="Image of Image to image" src="https://user-images.githubusercontent.com/105890749/198898970-64efd0e5-4e10-433a-928c-7a6cd95d1a4f.png">

The image to image function can be used to create an image based on a starting image (often a very rough sketch) combined with a text description.

Click on the left pane to upload a sketch starting image (only png supported). Add a prompt description of the desired output and press _generate_. The generated image will be 512 x 512 pixels.

* The **Options** buttons gives the following options:
  * Input strength: This tells DiffusionBee how closely to stick to the sketch input image. For rough sketches you normally want a low value.
  * Num images: The number of images to generate.
  * Steps: This corresponds to how many steps are used to build the image information. Setting to a low number gives faster image generation, and may be useful while exploring different prompts.
  * Seed: A number between 0 and 4,294,967,295 that is used as starting point for the image generation. If the same seed is used with the same image, the same prompt and the same settings (except *steps*, which may vary), the same image will be generated. If left empty, a random seed will be used.

### Inpainting
<img width="500" alt="Image of Inpainting" src="https://user-images.githubusercontent.com/105890749/198899315-3c905257-192f-44f2-9bdf-02e454c276de.png">

The inpainting function is used to replace/repaint parts of an image, for example to add a bow tie to a cat or removing a car from a photo of a street.

To use the inpainting functions, add an image and scribble on it to mask the area you wish DiffusionBee to re-paint for you. You will usually get a better result if you mask a significantly larger area than the part you actually want to change. Right now, the inpainting model works with a max height of 512 pixels, so any images bigger than that will be scaled down proportionally to fit the model.


### Outpainting
<img width="500" alt="Picture of Outpainting" src="https://user-images.githubusercontent.com/105890749/198899711-05bca2fb-04ca-4bc4-9d7c-e276bf5db9d2.png">

The outpainting function is used to expand an image to a larger area.

To use the outpainting functions, add an image and move the 512×512 frame to a place where you want to expand the image, and provide a text prompt. The process may be repeated to expand the image several times and in different directions.


## History
<img width="500" alt="Image of History" src="https://user-images.githubusercontent.com/105890749/198899465-8d85d26d-5f28-4965-accc-e3fbba80c6dd.png">

The **History** tab show previously generated images along with prompts and settings (including seed).

## Sharing images
<img width="500" alt="Image of sharing images" src="https://user-images.githubusercontent.com/105890749/198900052-25632642-c46c-4163-9dee-9758ec6fa06a.png">

Sharing images uploads images along with prompt and settings to arthub.ai. Before uploading you may select which of the images in a batch to upload. You are required to create an account to share images.

## Custom models

Diffusion Bee supports the ability to add and use custom models. Custom models are trained with specific images in order to create a certain style or type of image output. The best place to find custom models for DiffusionBee is [Hugging Face](https://huggingface.co/models?other=stable-diffusion). If using a model from Hugging Face, visit the model page and click the 'files and versions' tab. Then find and download the relevant .ckpt file.

<img width="500" alt="Image of Hugging Face model page" src="https://user-images.githubusercontent.com/105890749/201486549-1bc6d01c-c39f-4dc2-b216-3e42903315b8.png">


### Importing custom models
Once you have found and downloaded the .ckpt file of the model you wish to use, you need to import it into DiffusionBee. To do so, open DiffusionBee and click on the menu icon located on the top right. Click settings from the dropdown list, and click 'add new model'. Navigate to the model file, click on it, and click open. 

<img width="500" alt="Image of importing custom model" src="https://user-images.githubusercontent.com/105890749/201486009-1e63899a-e471-4f4d-aed5-31945bed6088.png">

### Using custom models
Once you have imported a custom model, you will be able to use it when generating images. First, click options and scroll down to the custom model section. Clicking on the icon will display a dropdown of all the available models. Choose the model you wish to use.

<img width="500" alt="Image of selcting custom model" src="https://user-images.githubusercontent.com/105890749/201485348-f746ae01-2ced-4dbd-9eff-2db28fc13d82.png">

When generating images with a custom model, make sure to use the custom token in order to get the desired result. The required prompt/ other important information is most likely disclosed on the info page of the model.

<img width="500" alt="Image of using custom model" src="https://user-images.githubusercontent.com/105890749/201485626-b2d4112a-91ba-431c-94c1-4bcc01c936de.png">


## Removing DiffusionBee

#### Removing the application itself
Drag and drop the DiffusionBee.app application to the Trash.

#### Removing leftover files
DiffusionBee saves your generated images and some information related to the custom models you might have imported in your home folder, in the .diffusionbee/ folder. If you want to fully uninstall the application, you can safely remove the whole folder. There are two ways to do it:

##### From the Terminal
Open the Terminal.app application (located in /Applications/Utilities/), and enter the command:

```
rm -r ~/.diffusionbee/
```

This will remove all traces of the DiffusionBee application (cache, generated images, imported models...).

##### From the Finder
Open your Home folder, and press the cmd + shift + . (command + shift + period) keys. This will show the hidden files and directories. You can safely drag and drop the .diffusionbee folder in the Trash.


## Extra tips

* For prompt ideas and help, check out:
  - [lexica.art](https://lexica.art/)
  - [arthub.ai](https://arthub.ai/)
  - `Prompt Engineering` section at [AssemblyAI](https://www.assemblyai.com/blog/how-to-run-stable-diffusion-locally-to-generate-images/)
* Image generation requires a substantial amount of system memory. Close other applications for a faster generation.
* You can save time while tuning your prompts by lowering the *steps* setting, then turning it back up once you found a good prompt.
* When tuning prompts, make sure that you enter a seed to make it possible to recreate images. If you generate more than one image per seed (via either the Num Images or Batch setting) there will not be a way to tie any of the images generated after the first one to the same seed. For example, if I have Num Images set to 3 and Seed set to 1000, the first of my three generated images will correspond to the seed of 1000, but I won't know the seed for the other two images.
* When _num images_ is set to more than 1, `1234` is added to the seed for each image following the first one. Therefore, the formula to calculate the seed of the $n^{th}$ image in a batch is the following: $seed(n) = seed + (n\times{1234})$. This can be used to recreate any number in a string of images without having to recreate all the previous ones.
* All created images are stored at `~/.diffusionbee/images/` in your file system. There is no interface in DiffusionBee for deleting images, but they can be deleted manually from this hidden directory.
* The model is stored at `~/.diffusionbee/downloads`. If you already have the model available and don't want to re-download it, move, copy or symlink it to that directory.
* The _Show logs_ menu option shows logs that are mostly useful for developers or for tracking errors. You exit the log by clicking one of the tabs.



## Join the discussion

Join the [DiffusionBee Discord Server](https://discord.gg/t6rC5RaJQn) to chat with the community.
