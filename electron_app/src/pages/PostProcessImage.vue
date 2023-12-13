<template>
    <BasicSDApplet
        :app=app 
        :input_form=form_data
        :sd_options=sd_options
        :name="'img_post_process'"
        :form_tags="['img_post_process']"
        :required_assets=[]
        ref="basic_sd_applet"
    >   

    <template v-slot:input_buttons>
            <div v-if="!is_running"  @click="upscale" class="l_button button_colored button_medium" style="float:right">Upscale</div>
    </template>

    <template v-slot:output_workpace>
        <GenerationGallery  :menu_items_skip="['use_params_current_page']" :app="app" :n_to_keep="2" ref="gallery"> </GenerationGallery>
    </template>


    </BasicSDApplet>
</template>
<script>

import BasicSDApplet from "../components/BasicSDApplet.vue"
import GenerationGallery from "../components/GenerationGallery.vue"
import Vue from 'vue'

const PostProcessImage = {
    name: 'PostProcessImage',
    props: {app:Object, },
    components: {BasicSDApplet, GenerationGallery},
    mounted() {
        this.app.functions.send_to_postprocess = this.send_to_postprocess; 
    },
    data() {
        return {
            form_data:[
                {
                    "id" : "input_img",
                    "component" : "ImageInput",
                    "get_img_size" : true,
                }, 

                {
                    "id": "65453545",
                    "component": "InputWithDesc",
                    "title": "Upscaler",
                    "description": "",
                    "children": [
                        {
                            "id": "model",
                            "component": "Dropdown",
                            "options": ["Real-ESRGAN"],
                            "icon": "photo",
                            "default_value" : "Real-ESRGAN" , 
                            "is_persistant" : true
                        }
                    ]
                },
            ], 
            sd_options : {},
            is_running : false,

        };
    },
    methods: {

        send_to_postprocess(im_path ){
          Vue.set( this.sd_options , "input_img" ,  im_path );
          this.app.functions.switch_page("PostProcessImage")
       },

        upscale(){

            let in_img = this.sd_options.input_img

            if(!in_img || in_img==''){
                this.app.show_toast('Please select an input image first')
                return
            }
                

            let that = this

            if(that.is_running)
                return

            this.$refs.gallery.clear_all()

            let h = this.sd_options['input_img__AUX__height' ] 
            let w = this.sd_options['input_img__AUX__width' ]

            if(h > 2048 || w > 2048){
                this.app.show_toast('Input image is too large')
                return
            }

            this.$refs.gallery.add_group({
                group_id : 1 ,
                num_imgs: 1 , 
                img_height: h , 
                img_width:  w, 
                
                imgs : [{params : {}, done_percentage: -1 } ]
            })
            
            that.is_running = true
            window.ipcRenderer.invoke('run_realesrgan', in_img.split("?")[0] ).then((result) => {
                let gallery_group = that.$refs.gallery.get_group(1 )
                let el_to_update = gallery_group.imgs[ 0  ]

                if(result) 
                {
                    el_to_update.image_url = result ;
                }
                else{
                    console.log("got error while upscale")
                    el_to_update.image_url = "ERROR" ;
                    el_to_update.description = "Error in upscaling the image" ;
                }

                this.$refs.gallery.update_group(gallery_group)
                that.is_running = false
            })


        }
    },
}

export default PostProcessImage;
PostProcessImage.title = "Upscaler"
PostProcessImage.description = "Use AI to increase the resolution of an image."
PostProcessImage.icon = "expand-arrows-alt"
PostProcessImage.img_icon = require("../assets/imgs/page_icon_imgs/upscale.png")
PostProcessImage.home_category = "main"
PostProcessImage.sidebar_show = "always"

// add this to the always_on_pages to the PagesRouter

</script>
<style>
</style>
<style scoped>
</style>