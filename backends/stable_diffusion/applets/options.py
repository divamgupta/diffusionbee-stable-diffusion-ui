options = """


[
    {
            "id" : "input_img",
            "component" : "ImageInput",
            "include_in" : ["img2img"] , 
            "get_img_size" : true,
            "draw_mask": true,
            "store_masked_image" : true

    },
    {
        "id" : "prompt",
        "component": "Textarea",
        "placeholder" : "Enter your prompt here",
        "default_value" : ""
    },
    {
        "id" : "negative_prompt",
        "component": "Textarea",
        "placeholder" : "Enter your negative prompt here",
        "is_small" : true,
        "include_in" : ["advanced"]
    },
    
    {
        "id": "is_adv_mode_desc",
        "component": "InputWithDesc",
        "title": "Advanced Options",
        "description": "",
        "children": [
            {
                "id": "is_adv_mode",
                "component": "Checkbox",
                "default_value" : false,
                "is_persistant" : true
            }
        ]
    },

    {
        "id": "selected_sd_model_desc",
        "component": "InputWithDesc",
        "title": "Model",
        "description": "The Stable Diffusion model used to generate images.",
        "children": [
            {
                "id": "selected_sd_model",
                "component": "Dropdown",
                "options": ["Default_SD1.5" ],
                "icon": "photo",
                "output_type" : "str",
                "default_value" : "Default_SD1.5",
                "is_persistant" : true
            }
        ]
    },

    {
        "id": "input_image_strength_desc",
        "component": "InputWithDesc",
        "title": "Input Strength",
        "full_width": true,
        "include_in" : ["img2img"],
        "description": "How  closely to stick to the input image.  (lower numbers makes the AI do more change)",
        "children": [
            {
                "id": "input_image_strength",
                "component": "Slider",
                "is_persistant" : true,
                "max_val" : 100,
                "min_val" : 2, 
                "output_type" : "float",
                "default_value" : 30
            }
        ]
    },
    {
        "id": "resolution_desc",
        "component": "InputWithDesc",
        "title": "Resolution",
        "exclude_in" : [ "outpainting" , "img2img" ],
        "description": "",
        "children": [
            {
                "id": "img_width",
                "component": "Dropdown",
                "options": [256, 320, 384, 448, 512, 576, 640, 704, 768],
                "icon": "img_width",
                "output_type" : "int",
                "default_value" : 512,
                "is_persistant" : true
            },
            {
                "id": "img_height",
                "component": "Dropdown",
                "options": [256, 320, 384, 448, 512, 576, 640, 704, 768],
                "default_value" : 512,
                "icon": "img_height",
                "output_type" : "int",
                "is_persistant" : true
            }
        ]
    },

    {
        "id": "num_imgs_desc",
        "component": "InputWithDesc",
        "title": "Number of images",
        "exclude_in" : [ "outpainting"],
        "description": "How many images are generated in total.",
        "children": [
            {
                "id": "num_imgs",
                "component": "Dropdown",
                "options": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 30, 50, 100 , 500 , 2000],
                "icon": "photo",
                "default_value" : 1,
                "output_type" : "int",
                "type" : "number",
                "is_persistant" : true
            }
        ]
    },

    {
        "id": "seed_desc",
        "component": "InputWithDesc",
        "title": "Seed",
        "description": "",
        "children": [
            {
                "id": "seed",
                "component": "Textbox",
                "icon": "seed",
                "placeholder" : "-1",
                "output_type" : "int",
                "type" : "number",
                "is_persistant" : false
            }
        ]
    },

    {
        "id": "num_steps_desc",
        "component": "InputWithDesc",
        "title": "Sampling Steps",
        "description": "",
        "children": [
            {
                "id": "num_steps",
                "component": "Dropdown",
                "options": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75],
                "icon": "steps",
                "type" : "number",
                "output_type" : "int",
                "default_value" : 25,
                "is_persistant" : true
            }
        ]
    },

    {
        "id": "diffusion_acc",
        "component": "Accordian",
        "title": "Diffusion",
        "include_in" : ["advanced"],
        "children": [
            {
                "id": "43545455",
                "component": "InputWithDesc",
                "title": "Sampler",
                "description": "The sampling algorithm used by DiffusionBee.",
                "children": [
                    {
                        "id": "scheduler",
                        "component": "Dropdown",
                        "options": ["ddim" , "lmsd" , "pndm" , "k_euler_ancestral", "k_euler"  ],
                        "icon": "photo",
                        "output_type" : "str",
                        "default_value" : "ddim",
                        "is_persistant" : true
                    }
                ]
            },
            {
                "id": "53454543",
                "component": "InputWithDesc",
                "title": "Steps",
                "description": "Iterations of the image (more steps means more detail & more processing time - best to start around 10)",
                "children": [
                    {
                        "id": "num_steps",
                        "component": "Dropdown",
                        "options": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75],
                        "icon": "steps",
                        "type" : "number",
                        "output_type" : "int",
                        "default_value" : 25,
                        "is_persistant" : true
                    }
                ]
            },
            {
                "id": "32e43434",
                "component": "InputWithDesc",
                "title": "Guidance Scale",
                "full_width": true,
                "description": "How closely to follow your prompt (lower numbers give the AI more creativity)",
                "children": [
                    {
                        "id": "guidance_scale",
                        "component": "Slider",
                        "is_persistant" : true,
                        "max_val" : 20,
                        "output_type" : "float",
                        "min_val" : 1, 
                        "default_value" : 7.5
                    }
                ]
            }
        ]
    },
    {
        "id": "seed_acc",
        "component": "Accordian",
        "title": "Seed",
        "include_in" : ["advanced"],
        "children": [
            {
                "id": "765655",
                "component": "InputWithDesc",
                "title": "Seed",
                "description": "Starting point for iterations (any random number will do; DB will pick one if left blank).",
                "children": [
                    {
                        "id": "seed",
                        "component": "Textbox",
                        "icon": "seed",
                        "placeholder" : "-1",
                        "type" : "number",
                        "output_type" : "int",
                        "is_persistant" : false
                    }
                ]
            } , 
            {
                "id": "76565345",
                "component": "InputWithDesc",
                "title": "Small Modification Seed",
                "description": "If you want to do small variations in the images.",
                "children": [
                    {
                        "id": "small_mod_seed",
                        "component": "Textbox",
                        "icon": "seed",
                        "placeholder" : "-1",
                        "type" : "number",
                        "output_type" : "int",
                        "is_persistant" : false
                    }
                ]
            } 
        ]
    }, 
    {
        "id": "controlnet_acc",
        "component": "Accordian",
        "title": "ControlNet",
        "include_in" : ["advanced"],
        "exclude_in" : [ "outpainting" ],
        "children": [
            
            {
                "id": "344345435",
                "component": "InputWithDesc",
                "title": "ControlNet Model",
                "description": "",
                "children": [
                    {
                        "id": "controlnet_model",
                        "component": "Dropdown",
                        "options": ["None" , "Depth" , "BodyPose" , "Scribble" ],
                        "default_value" : "None",
                        "icon": "photo",
                        "is_persistant" : false
                    }
                ]
            } , 
            {
                "id" : "controlnet_input_image_path",
                "component" : "ImageInput"
            } , 
            {
                "id": "678545",
                "component": "InputWithDesc",
                "title": "Automatically generate control?",
                "description": "If you select No, you have to input raw control image.",
                "children": [
                    {
                        "id": "do_controlnet_preprocess",
                        "component": "Dropdown",
                        "options": ["Yes" , "No"   ],
                        "output_type" : "bool",
                        "default_value" : "Yes",
                        "icon": "photo",
                        "is_persistant" : true
                    }
                ]
            } 

        ]
    } , 

    {
        "id": "misc_acc",
        "component": "Accordian",
        "title": "Misc",
        "include_in" : ["advanced"],
        "children": [
            {
                "id": "678545",
                "component": "InputWithDesc",
                "title": "V-Prediction",
                "description": "If it should use V-Prediction. Mostly used in SD2.X 768 models. ",
                "children": [
                    {
                        "id": "do_v_prediction",
                        "component": "Checkbox",
                        "output_type" : "bool",
                        "default_value" : false,
                        "is_persistant" : false
                    }
                ]
            } 
        ]
    } 


]



"""