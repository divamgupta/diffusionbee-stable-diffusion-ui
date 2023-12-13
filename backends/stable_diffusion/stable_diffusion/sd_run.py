from dataclasses import dataclass


@dataclass
class SDRun():
    
    prompt: str

    is_sd2:bool = False

    mode:str="txt2img"
    tdict_path:str=None
    dtype:str= "float16"

    starting_img_given:bool = False 
    do_masking_diffusion:bool = False # if you wanna mask the latent at every sd step
    img_height: int = None
    img_width: int = None

    negative_prompt:str=""

    batch_size:int =1
    num_steps:int =25
    guidance_scale:float=7.5
    seed:int=None
    seed_type:str="np"
    small_mod_seed:int=None
    img_id:int = 0
    scheduler:str = "__default_for_model__"

    combine_unet_run:bool = False  # if it should do the cond + uncond in single batch

    input_image_path:str =None
    inp_image_resize_mode:str = "legacy_auto"

    mask_image_path:str =None
    get_mask_from_image_alpha:bool = False
    get_binary_mask_from_colored_mask:bool = True #if the mask_image_path is a colored mask, and this option will extract binary mask from it
    blur_mask:bool = False
    infill_alpha:bool = False #infill the image first
    infill_mask:bool = False #not used, infill the mask

    force_use_given_size:bool = False # this will set inp_image_resize_mode to none
    input_image_strength:float=0.5
    second_tdict_path:str = None
    lora_tdict_paths:tuple = ()

    controlnet_model:str = None
    do_controlnet_preprocess:bool = False
    controlnet_input_image_path:str = None
    controlnet_inp_img_preprocesser:str = None # name of the preprocess fn 
    is_control_net:bool = False
    controlnet_inp_img_preprocesser_model_path:str = None
    controlnet_tdict_path:str = None
    control_weight:float = 1.0
    control_weight_current_cond:float = 1.0
    control_weight_current_uncond:float = 1.0
    controlnet_guess_mode:bool = False
    
    is_sd15_inpaint:bool = False
    do_v_prediction:bool = False

    is_clip_skip_2:bool = False
