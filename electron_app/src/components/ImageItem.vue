<template>
    <div style="height:100%" v-bind:style="style_obj">
                
        <div v-if="!hide_dropdown" style=" position:absolute ; margin-top:7px ; margin-left:7px " class="">
            <b-dropdown left variant="link" size="sm" toggle-class="text-decoration-none" no-caret>
                <template #button-content>
                    <div   class=" l_button button_colored" style="background-color: rgba(0,0,0,0.6);">
                        <font-awesome-icon icon="bars" />
                    </div>
                </template>
                <b-dropdown-item-button   @click="save_image(path, prompt, seed)"  >Save Image</b-dropdown-item-button>
                <b-dropdown-item-button @click="upsclae" >Upscale Image</b-dropdown-item-button>
                <b-dropdown-item-button @click="send_img2img" >Send to Img2Img</b-dropdown-item-button>
                
                
            </b-dropdown>
        </div>
        
        
        <img   @click="open_image_popup( path )"  class="gal_img" :src="'file://' + path " style="max-height: 100% ; max-width: 100%;" >
        <br>
        <div v-if="!hide_extra_save_button" @click="save_image(path, prompt, seed)" class="l_button">Save Image</div>
    </div>
</template>
<script>

import {open_popup} from "../utils"

export default {
    name: 'ImageItem',
    props: {
        path : String,
        prompt: String,
        seed: Number,
        style_obj:Object,
        app_state:Object,
        hide_extra_save_button : Boolean,
        hide_dropdown : Boolean,
    },
    components: {},
    mounted() {

    },
    data() {
        return {};
    },
    methods: {
        open_image_popup(img){
            open_popup("file://"+img , undefined);
        },

        save_image(generated_image, prompt, seed){
            if(!generated_image)
                return;
            generated_image = generated_image.split("?")[0];
            let out_path = window.ipcRenderer.sendSync('save_dialog', prompt, seed);
            if(!out_path)
                return
            let org_path = generated_image.replaceAll("file://" , "")
            window.ipcRenderer.sendSync('save_file', org_path+"||" +out_path);
        },

        send_img2img(){
            if(this.app_state){

                if(this.app_state.app_object.$refs.stable_diffusion.is_input_avail){
                    this.app_state.app_object.$refs.img2img.inp_img = this.path;
                     this.app_state.app_object.$refs.app_frame.selected_tab = 'img2img';
                } 
            }
        } , 

        upsclae(){
            if(this.app_state){
                this.app_state.app_object.$refs.app_frame.selected_tab = 'upscale_img';
                this.app_state.app_object.$refs.upscale_img.do_upscale(this.path);
                
            }
            
        },

    },
}
</script>
<style>
</style>
<style scoped>
</style>