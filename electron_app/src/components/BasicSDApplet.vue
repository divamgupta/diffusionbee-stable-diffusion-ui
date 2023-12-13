<template>
    <TwoColAppletLayout>
        
        <template v-slot:input_workspace>
              <slot name="input_workspace_pre_form"></slot>
              <Form ref="form"  :form_data="input_form_elements_processed"  :form_values="sd_options" :form_save_key="'1fdaedjdfddeef1'+name" :tags="all_tags" ></Form>
              <div @click="$refs.form.reset_to_default()" class="l_button" style="margin-left:-10px"> Reset to default </div>
              <slot name="input_workspace_post_form"></slot>
        </template>

        <template v-slot:input_buttons>
            <slot name="input_buttons"></slot>
        </template>

        <template v-slot:output_workpace>
            <div class="model_dialog_container" v-if="to_download_left.length > 0 ">
                
            </div>
            <div class="model_dialog" v-if="to_download_left.length > 0 ">
                <h2> You need to download the following models to generate: </h2>
                <br>
                <p>{{to_download_left[0].title}}</p> <DownloadButton :app=app  :asset_details="to_download_left[0]"> </DownloadButton>
            </div>

            <slot name="output_workpace"></slot>
        </template>

    </TwoColAppletLayout>
</template>
<script>

import Form from "../components_bare/Form.vue"
import TwoColAppletLayout from "../components_bare/TwoColAppletLayout.vue"
import DownloadButton from "./DownloadButton.vue"
import Vue from 'vue'
import {find_in_form_recursive} from "../utils.js"

function prep_sd_options(options){
    options = JSON.parse(JSON.stringify(options))


    if(options.seed)
        options.seed = Number(options.seed);
    else if(options.seed != undefined)
        options.seed = Math.floor(Math.random() * 100000);

    if(options.seed < 0){
        options.seed = Math.floor(Math.random() * 100000);
    }

    return options
}



export default {
    name: 'BasicSDApplet',
    props: {
        app:Object, 
        input_form : Array,
        sd_options: Object,
        name:String,
        form_tags: Array,
        required_assets : Array, 
        model_options_types : Array, // what kind of models should it show in teh dropdown ( sd, sd_inpaint etc )
    },
    components: {Form  , TwoColAppletLayout, DownloadButton },
    mounted() {

    },
    data() {
        return {
            input_form_options: {}
        };
    },
    methods: {
        
        // given an options dict, load those values inthe form
        load_options(options){
            console.log("load")
            console.log(options)
            let raw_options = options; // the unprocessed form ouptuts
            if(options.raw_form_options){
                raw_options = options.raw_form_options
            }

            for(let k of Object.keys(options)){
                if(raw_options[k] != undefined){
                    console.log("setting " + k )
                    Vue.set(this.sd_options, k ,  raw_options[k])
                }
                    
            }
        } , 

        request_ojects_from_img_element(object_name , object ){
            console.log(object_name)
            if(object_name == "get_mask_img_b64"){
                this.get_mask_img_b64 = object
            }

            if(object_name == "get_mask_b64"){
                this.get_mask_b64 = object
            }
            
       },

        get_sd_form_outputs(){
            let options = this.$refs.form.post_processed_form_outputs()
            options = prep_sd_options(options)

            options.applet_name = this.name

            // map the selected avail model to the tdict
            if(options.selected_sd_model){
                options.model_tdict_path = this.app.assets_manager.get_downloaded_asset_path(options.selected_sd_model)

                let asset = this.app.assets_manager.get_downloaded_asset(options.selected_sd_model)
                let asset_metadata = (asset||{}).model_meta_data
                if(asset_metadata && asset_metadata.do_v_prediction){
                    options.do_v_prediction = true 
                }

                if(asset_metadata && asset_metadata.trigger_word && options.prompt && !(options.prompt.includes(asset_metadata.trigger_word)) ){
                    options.prompt = asset_metadata.trigger_word + " " + options.prompt
                }
            }

            // if possible get the input image masks and stuff
            if(options.input_img){
                if(this.get_mask_b64){
                    let mask_b64 = this.get_mask_b64()
                    if(mask_b64){
                        options.mask_image = (window.ipcRenderer.sendSync('save_b64_image',  mask_b64 , true ))
                    }
                }
                if(this.get_mask_img_b64){
                    let mask_img_b64 = this.get_mask_img_b64()
                    if(mask_img_b64){
                        options.input_image_with_mask =  (window.ipcRenderer.sendSync('save_b64_image',  mask_img_b64  ))
                    }
                }
            }

            return options
        } , 

        check_input_form_n_show_error(){
            if(this.to_download_left.length > 0){
                this.app.show_toast("First you need to download the model to generate")
                return false;
            } 

            if( this.get_sd_form_outputs().prompt != undefined && this.get_sd_form_outputs().prompt.trim() == ""){
                console.log(this.get_sd_form_outputs())
                this.app.show_toast('You need to enter a prompt')
                return false;
            }

            if(this.sd_options.selected_sd_model){
                if(!(this.app.assets_manager.get_downloaded_asset_path(this.sd_options.selected_sd_model))){
                    this.app.show_toast("Model not found. Please select a valid model.")
                    return false                    
                }
            }

            return true;
        },

    },
    computed : {
        all_tags(){
            console.log("sddd options ")
            console.log(this.sd_options)
            let l = (this.form_tags || []).concat( this.sd_options.is_adv_mode ? ['advanced']:[]  )
            return l
        } , 

        input_form_elements_processed(){
            let form = JSON.parse(JSON.stringify(this.input_form))
            

            // add the avail models to the form
            let el = find_in_form_recursive( "selected_sd_model" , form)
            if(el){
                let assets = Object.values(this.app.assets_manager.all_avail_assets)
                assets = assets.filter(x => x.model_meta_data && (this.model_options_types ||["sd_model"]).includes(x.model_meta_data.type))
                let new_ids = assets.map(x => x.id)
                for( let idd of new_ids){
                    if(!el['options'].includes(idd))
                        el['options'].push(idd)
                }
            }

            // get the functions to get the mask and stuff
            el =  find_in_form_recursive( "input_img" , form)
            if(el && el.draw_mask && el.store_masked_image){
                el.request_objects_from_element = "yes"
                el.request_objects_from_element_fn = this.request_ojects_from_img_element
            }

            // for SDXL make sure that we only allow certain schedulers ( disabled for now )
            // if(this.sd_options && this.sd_options.selected_sd_model){
            //     let selected_asset =  this.app.assets_manager.all_avail_assets[this.sd_options.selected_sd_model  ]
            //     if(selected_asset &&  selected_asset.model_meta_data && selected_asset.model_meta_data.sd_type && selected_asset.model_meta_data.sd_type == "sdxl_base"  ){
            //         let el2 = find_in_form_recursive( "scheduler" , form)
            //         if(el2){
            //             el2['default_value'] = "karras"
            //             el2['options'].splice(0, el2['options'].length);
            //             el2['options'].push("karras")
                        
            //         }
            //     } 
            // }

            // for sdxl make use different image sizes
            if(this.sd_options && this.sd_options.selected_sd_model){
                let selected_asset =  this.app.assets_manager.all_avail_assets[this.sd_options.selected_sd_model  ]
                if(selected_asset &&  selected_asset.model_meta_data && selected_asset.model_meta_data.sd_type && selected_asset.model_meta_data.sd_type == "sdxl_base"  ){
                    let el2 = find_in_form_recursive( "img_width" , form)
                    if(el2){
                        el2['default_value'] = 768
                        el2['options'].splice(0, el2['options'].length);
                        el2['options'].push(  576, 640, 704, 768, 832, 896 , 960 , 1024, 1088  , 1152 , 1216  )
                        
                    }

                    let el3 = find_in_form_recursive( "img_height" , form)
                    if(el3){
                        el3['default_value'] = 768
                        el3['options'].splice(0, el3['options'].length);
                        el3['options'].push(   576, 640, 704, 768, 832, 896 , 960 , 1024, 1088  , 1152 , 1216  )
                        
                    }

                    // Vue.set(this.sd_options , 'img_width',768  )
                    // Vue.set(this.sd_options , 'img_height',768  )

                } 
            }



            return form;
        },

        required_assets_modified(){
            let ret = []
            if(!this.required_assets){
                ret = []
            } else {
                ret = JSON.parse(JSON.stringify(this.required_assets))
            }

            if(  this.sd_options.selected_sd_model == "Default_SD1.5"){
                ret.push( { 
                    id : 'Default_SD1.5' , 
                    filename: 'sd-v1-5_fp16.tdict' ,   
                    md5: 'a36c79b8edb4b21b75e50d5834d1f4ae' , 
                    is_stock_model : true,
                    url : 'https://huggingface.co/divamgupta/stable_diffusion_mps/resolve/main/sd-v1-5_fp16.tdict' , 
                    title: "Stable Diffusion 1.5 (Default)", 
                    model_meta_data : {"type" : "sd_model", "float_type" : "float16" ,  "sd_type" : "SD_1x" }
                } )
            }
            
            return ret
        },

        to_download_left(){
            let to_download = []
           
            for(let asset of this.required_assets_modified){
                let asset_id = asset.id
                if(!(this.app.is_mounted && this.app.assets_manager.downloaded_assets[asset_id] && this.app.assets_manager.downloaded_assets[asset_id].status == 'done')){
                    to_download.push(asset)
                }
            }
            return to_download
        }
    }
}
</script>
<style>
</style>
<style scoped>


.model_dialog_container{
    position: fixed;
    left: calc(    var(--sidebar-width )  + 360px );
    right:0 ;
    bottom:0;
    background-color: rgba(0,0,0,0.3);
/*    height: 100%;*/
    z-index: 900;
    top: var(--titlebar-height);
}

.model_dialog{
    position: fixed;
    width: 250px ;
    height:170px;
    background: var(--options-input-bg );
    left: calc( 50% +  var(--sidebar-width ) /2 + 175px );
    top:50%;
     transform: translateY(-50%) translateX(-50%);
    z-index: 1000;
    padding:20px;
}


</style>