

function inpaint_assets(self , mode ){
    let to_download = []
    if((!self.sd_options.selected_sd_model) || self.sd_options.selected_sd_model == "SD1.5_Inpainting"){
        to_download.push( { 
            id : "SD1.5_Inpainting", 
            filename: 'sd-v1-5-inpainting_fp16.tdict' ,   
            md5: '68303f49cca00968c39abddc20b622a6' , 
            is_stock_model : true,
            url : 'https://huggingface.co/divamgupta/stable_diffusion_mps/resolve/main/sd-v1-5-inpainting_fp16.tdict' , 
            title: "SD 1.5 Inpainting by RunwayML", 
            model_meta_data : {"type" : "sd_model_inpaint", "float_type" : "float16" ,  "sd_type" : "SD_1x_inpaint" }
        } )
    }

    // in generative fill, if a non inpaintgin model selected then it needs the contorlnet inpaint
    if(mode == "Generative Fill"){
        if((!self.sd_options.selected_sd_model) || self.sd_options.selected_sd_model == "Default_SD1.5" || 
            (self.app.assets_manager.all_avail_assets[self.sd_options.selected_sd_model] && (self.app.assets_manager.all_avail_assets[self.sd_options.selected_sd_model].model_meta_data||{}).type == "sd_model" )){

            to_download.push( {
                "id": "just_control_v11p_sd15_inpaint_fp16",
                "filename": "just_control_v11p_sd15_inpaint_fp16.tdict",
                "md5": "08a0a43ff75a4a4941fbb885c50d7874",
                is_stock_model : true,
                "url": "https://huggingface.co/divamgupta/controlnet_tensorflow/resolve/main/just_control_v11p_sd15_inpaint_fp16.tdict",
                "title": "ControlNet Inpaint",
                "description": "ControlNet Inpaint model.",
                model_meta_data : {"type" : "controlnet_model" , "sd_type" : "SD_1x", "float_type" : "float16" }
            })
        }
    }

    return to_download;
}

function prep_sd_optins(self , sd_options_object, mode , img_mask_url){
    if(!sd_options_object.num_imgs)
        sd_options_object.num_imgs = 1

    if( mode == "Text To Image") {
        sd_options_object.sd_mode_override = "txt2img"
    } else {

        if(mode == "Generative Fill"){
        
            let is_control_inpaint = false 
            
        
            if((self.app.assets_manager.all_avail_assets[self.sd_options.selected_sd_model].model_meta_data||{}).type == "sd_model" ){
                is_control_inpaint = true
                
            }   

            if(is_control_inpaint){
                sd_options_object.do_masking_diffusion = true
                sd_options_object.controlnet_model ="Inpaint"
                sd_options_object.controlnet_inp_img_preprocesser="Inpaint"
                sd_options_object.controlnet_input_image_path="NULL"
                sd_options_object.is_control_net=true
                sd_options_object.controlnet_guess_mode=true
                sd_options_object.guidance_scale = ( (sd_options_object.guidance_scale || 7.5) - 3.5 )
                if(sd_options_object.guidance_scale <= 1)
                    sd_options_object.guidance_scale = 1
                sd_options_object.sd_mode_override = "txt2img"
                sd_options_object.controlnet_tdict_path= self.app.assets_manager.get_downloaded_asset_path("just_control_v11p_sd15_inpaint_fp16")

            } else {
                // SD1.5 inpaint
                sd_options_object.is_sd15_inpaint = true
                sd_options_object.sd_mode_override = "txt2img"
            }
        } else {
            // Image to Image case
            sd_options_object.infill_alpha = true
        }

        sd_options_object.get_mask_from_image_alpha = true;

        if(self.sd_options.inp_only_update_masked){
            sd_options_object.blur_mask = true
            sd_options_object.do_masking_diffusion = true
            
        }
        sd_options_object.mask_image_path = img_mask_url
    }
}

export { prep_sd_optins ,  inpaint_assets }