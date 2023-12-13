

function controlnet_required_assets(self , to_download){
    if( self.sd_options.controlnet_model && self.sd_options.controlnet_model == "Depth" ){
        to_download.push( {
            "id": "just_control_sd15_depth_fp16",
            "filename": "just_control_sd15_depth_fp16.tdict",
            "md5": "652bb2d467e37ba8253b7361973c82b6",
            "url": "https://huggingface.co/divamgupta/controlnet_tensorflow/resolve/main/just_control_sd15_depth_fp16.tdict",
            "title": "ControlNet Depth",
            is_stock_model : true,
            "description": "ControlNet Depth. Works with MiDaS depth.",
            model_meta_data : {"type" : "controlnet_model" , "sd_type" : "SD_1x", "float_type" : "float16" }
        })

        if( self.sd_options.do_controlnet_preprocess == true || self.sd_options.do_controlnet_preprocess == "Yes" ){
            to_download.push( {
                "id": "midas_monodepth",
                "filename": "midas_monodepth.onnx",
                "md5": "3ad9d8a9d820214d2bfe65c0d37683a7",
                is_stock_model : true,
                "url": "https://huggingface.co/divamgupta/controlnet_tensorflow/resolve/main/midas_monodepth.onnx",
                "title": "MiDaS Depth Extractor",
                "description": "MiDaS Depth Extractor, for processing ControlNet input.",
                model_meta_data : {"type" : "controlnet_preprocess_model"   }
            })
        }
    }

    if( self.sd_options.controlnet_model && self.sd_options.controlnet_model == "BodyPose" ){
        to_download.push( {
            "id": "just_control_sd15_openpose_fp16",
            "filename": "just_control_sd15_openpose_fp16.tdict",
            "md5": "81077e9fe3472ed2242a7a3d8035b6eb",
            "url": "https://huggingface.co/divamgupta/controlnet_tensorflow/resolve/main/just_control_sd15_openpose_fp16.tdict",
            "title": "ControlNet Body",
            is_stock_model : true,
            "description": "ControlNet Body model. Works with OpenPose poses.",
            model_meta_data : {"type" : "controlnet_model" , "sd_type" : "SD_1x", "float_type" : "float16" }
        })

        if(  self.sd_options.do_controlnet_preprocess == true || self.sd_options.do_controlnet_preprocess == "Yes" ){
            to_download.push( {
                "id": "body_pose_model",
                "filename": "body_pose_model.onnx",
                "md5": "51499a50aff296971a99605f32c7e8e7",
                is_stock_model : true,
                "url": "https://huggingface.co/divamgupta/controlnet_tensorflow/resolve/main/body_pose_model.onnx",
                "title": "OpenPose Extractor",
                "description": "OpenPose Extractor, for processing ControlNet input.",
                model_meta_data : {"type" : "controlnet_preprocess_model"   }
            })
        }

        
    }

    if( self.sd_options.controlnet_model && self.sd_options.controlnet_model == "LineArt" ){
        to_download.push( {
            "id": "just_control_v11p_sd15_lineart",
            "filename": "just_control_v11p_sd15_lineart.tdict",
            "md5": "5917957e792a5b4399714bf44240034d",
            "url": "https://huggingface.co/divamgupta/controlnet_tensorflow/resolve/main/just_control_v11p_sd15_lineart.tdict",
            "title": "ControlNet LineArt",
            is_stock_model : true,
            "description": "ControlNet LineArt model. ",
            model_meta_data : {"type" : "controlnet_model" , "sd_type" : "SD_1x", "float_type" : "float16" }
        })

        if(  self.sd_options.do_controlnet_preprocess == true || self.sd_options.do_controlnet_preprocess == "Yes" ){
            to_download.push( {
                "id": "lineart_model",
                "filename": "lineart_model.onnx",
                "md5": "667d0d7cad9449f3a6db135b526f2279",
                is_stock_model : true,
                "url": "https://huggingface.co/divamgupta/controlnet_tensorflow/resolve/main/linart.onnx",
                "title": "LineArt Extractor",
                "description": "LineArt Extractor, for processing ControlNet input.",
                model_meta_data : {"type" : "controlnet_preprocess_model"   }
            })
        }
    }


    if( self.sd_options.controlnet_model && self.sd_options.controlnet_model == "Scribble" ){
        to_download.push( {
            "id": "just_control_sd15_scribble_fp16",
            "filename": "just_control_sd15_scribble_fp16.tdict",
            "md5": "2d29e2d006035919180e2f8b6decc40a",
            is_stock_model : true,
            "url": "https://huggingface.co/divamgupta/controlnet_tensorflow/resolve/main/just_control_sd15_scribble_fp16.tdict",
            "title": "ControlNet Scribble",
            "description": "ControlNet Scribble model.",
            model_meta_data : {"type" : "controlnet_model" , "sd_type" : "SD_1x", "float_type" : "float16" }
        })
    }

    

    if( self.sd_options.controlnet_model && self.sd_options.controlnet_model == "Tile" ){
        to_download.push( {
            "id": "just_control_v11f1e_sd15_tile_fp16",
            "filename": "just_control_v11f1e_sd15_tile_fp16.tdict",
            "md5": "7f3eb2dbb810ec1a643e2ec31cc2892e",
            is_stock_model : true,
            "url": "https://huggingface.co/divamgupta/controlnet_tensorflow/resolve/main/just_control_v11f1e_sd15_tile_fp16.tdict",
            "title": "ControlNet Tile",
            "description": "ControlNet Tile model.",
            model_meta_data : {"type" : "controlnet_model" , "sd_type" : "SD_1x", "float_type" : "float16" }
        })
    }



    if( self.sd_options.controlnet_model && self.sd_options.controlnet_model == "Inpaint" ){
        to_download.push( {
            "id": "just_control_v11p_sd15_inpaint_fp16",
            "filename": "just_control_v11p_sd15_inpaint_fp16.tdict",
            "md5": "3ad9d8a9d820214d2bfe65c0d37683a7",
            is_stock_model : true,
            "url": "https://huggingface.co/divamgupta/controlnet_tensorflow/resolve/main/just_control_v11p_sd15_inpaint_fp16.tdict",
            "title": "ControlNet Inpaint",
            "description": "ControlNet Inpaint model.",
            model_meta_data : {"type" : "controlnet_model" , "sd_type" : "SD_1x", "float_type" : "float16" }
        })
        
    }






}

function controlnet_proc_form_outputs(self , options){
    if(options.controlnet_model && options.controlnet_model == "Depth" ){
        options.controlnet_tdict_path = self.app.assets_manager.get_downloaded_asset_path("just_control_sd15_depth_fp16")

        if(options.do_controlnet_preprocess)
            options.controlnet_inp_img_preprocesser_model_path = self.app.assets_manager.get_downloaded_asset_path("midas_monodepth")

    }

    if(options.controlnet_model && options.controlnet_model == "BodyPose" ){
        options.controlnet_tdict_path = self.app.assets_manager.get_downloaded_asset_path("just_control_sd15_openpose_fp16")

        if(options.do_controlnet_preprocess)
            options.controlnet_inp_img_preprocesser_model_path = self.app.assets_manager.get_downloaded_asset_path("body_pose_model")
    }

    if(options.controlnet_model && options.controlnet_model == "LineArt" ){
        options.controlnet_tdict_path = self.app.assets_manager.get_downloaded_asset_path("just_control_v11p_sd15_lineart")

        if(options.do_controlnet_preprocess)
            options.controlnet_inp_img_preprocesser_model_path = self.app.assets_manager.get_downloaded_asset_path("lineart_model")
    }


    if(options.controlnet_model && options.controlnet_model == "Scribble" ){
        options.controlnet_tdict_path = self.app.assets_manager.get_downloaded_asset_path("just_control_sd15_scribble_fp16")
    }

    if(options.controlnet_model && options.controlnet_model == "Tile" ){
        options.controlnet_tdict_path = self.app.assets_manager.get_downloaded_asset_path("just_control_v11f1e_sd15_tile_fp16")
    }

}

function controlnet_check_inputs(self , vue){
    
    if(self.sd_options.controlnet_model && self.sd_options.controlnet_model != "None" ){
        if((!self.sd_options.controlnet_input_image_path) || self.sd_options.controlnet_input_image_path == ""){
            vue.$toast.default("You have selected a ControlNet model but not specified an image.")
             return false;
        }
        
    } 

    return true
}


export { controlnet_check_inputs , controlnet_proc_form_outputs , controlnet_required_assets }