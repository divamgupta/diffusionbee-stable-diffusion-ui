<template>
    <SDImageGenerationApplet 
        ref="sd_applet"   
        name="img2img" :form_data="form_data" :form_tags="[  'img2img']" :app="app" 
        :check_options_input_fn="check_options_input_fn"
        :postprocess_form_options_fn="postprocess_form_options_fn"> </SDImageGenerationApplet>
</template>
<script>


import SDImageGenerationApplet from "../components/SDImageGenerationApplet.vue"
import Vue from 'vue'


const Img2Img = {
    name: 'Img2Img',
    props: {
        app:Object, 
    },
    components: {SDImageGenerationApplet},
    mounted() {
        this.app.functions.send_to_img2img = this.send_to_img2img; 
    },
    data() {
        let form_data = require("../forms/sd_options_adv.json")
        
        return {
            form_data:form_data, 
        };
    },
    methods: {
       send_to_img2img(im_path, params ){
          Vue.set( this.$refs.sd_applet.sd_options , "input_img" ,  im_path );
          if(params){
             params = JSON.parse(JSON.stringify(params))
             params.input_img = undefined
             params.seed = undefined
             if(params.raw_form_options)
                params.raw_form_options.input_img = undefined
                params.raw_form_options.seed = undefined
             this.$refs.sd_applet.load_options(params)
          }
          this.app.functions.switch_page("Img2Img")

       }, 

       check_options_input_fn(){
            if((!this.$refs.sd_applet.sd_options.input_img) || this.$refs.sd_applet.sd_options.input_img=="" ){
                this.app.show_toast("You need to specify an input image")
                return false
            } else {
                return true
            }
       }, 

       postprocess_form_options_fn(options){
            if(!options.img_width){
                options.img_width = this.$refs.sd_applet.sd_options.input_img__AUX__width
            }
            if(!options.img_height){
                options.img_height = this.$refs.sd_applet.sd_options.input_img__AUX__height
            }

            return options
       }
    },
}

export default Img2Img;
Img2Img.title = "Image to image"
Img2Img.description = "Transform images with text descriptions"
Img2Img.icon = "images"
Img2Img.img_icon = require("../assets/imgs/page_icon_imgs/img2img.png")
Img2Img.home_category = "main"
Img2Img.sidebar_show = "always"

</script>
<style>
</style>
<style scoped>
</style>