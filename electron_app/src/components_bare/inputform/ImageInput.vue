<template>

   <div>

        <div v-if="form_values[config.id]" @drop.prevent="onDragFile" @dragover.prevent class="image_area" :class="{ crosshair_cur  : is_inpaint }"  style="height: 300px;  border-radius: 5px; padding:5px;">
            <ImageCanvas :on_img_load="on_img_load" ref="inp_img_canvas" :is_inpaint="is_inpaint" :image_source="form_values[config.id]"  :is_disabled="false"  :canvas_id="rand_id" :canvas_d_id="rand_id+'d' "  ></ImageCanvas>
        </div>
        <div v-else @drop.prevent="onDragFile" @dragover.prevent @click="open_input_image" class="image_area" :class="{ pointer_cursor  : is_input_avail }" style="height:150px;  border-radius: 5px; padding:5px;">
                <center>
                <p style="margin-top: 60px; opacity: 70%; font-size: 13px;" >Click to add input image</p>
            </center>
        </div>

        <div v-if="form_values[config.id] && is_input_avail" class="l_button" @click="open_input_image" >Change Image</div>
        <div v-if="form_values[config.id] && is_input_avail" class="l_button" @click="form_values[config.id] =''">Clear</div>
        <div v-if="form_values[config.id] && config.draw_mask && is_input_avail && !is_inpaint" class="l_button" @click="is_inpaint = !is_inpaint ">Draw Mask</div>
        <div v-if="form_values[config.id] && config.draw_mask && is_input_avail && is_inpaint" class="l_button" @click="is_inpaint = !is_inpaint ">Remove Mask</div>

        <br v-if="form_values[config.id] && is_input_avail"> 

        <!-- <div style="height: 340px;  "> </div>
        <ImageCanvas ref="inp_img_canvas" :is_inpaint="true" image_source="/Users/divamgupta/Downloads/512_576-1.png"  :is_disabled="false" :canvas_id="rand_id" :canvas_d_id="rand_id+'d' " ></ImageCanvas> -->

     <br>
  </div> 

</template>
<script>

import FormInputMixin from "./FormInputMixin.vue"
import { icon_library } from "../icon_library.js"
import ImageCanvas from "../ImageCanvas.vue"
import Vue from 'vue'

export default {
    name: 'ImageInput',
    mixins: [FormInputMixin],
    props: {
         config: Object , 
        form_values: Object,
    },
    components: {ImageCanvas},
    mounted() {
        if(this.config.request_objects_from_element){
            // the Applet / component needs to laod the image b64 etc
            // so the applet provised the function request_objects_from_element in the config
            // the form input component calls that function to give it the function to request the base64
            this.config.request_objects_from_element_fn("get_mask_img_b64" , this.get_mask_img_b64)
            this.config.request_objects_from_element_fn("get_mask_b64" , this.get_mask_b64)
        }
    },
    data() {
        return {
            is_inpaint: false,
            is_input_avail: true,
            icon_library:icon_library,
            rand_id:  Math.random().toString()
        };
    },
    methods: {
        open_input_image(){
            
            let img_path = window.ipcRenderer.sendSync('file_dialog',  'img_file' );
            if(img_path && img_path != 'NULL'){
                Vue.set(this.form_values , this.config.id , img_path)
                this.is_inpaint = false;
            }      
        },
        onDragFile(e){
           
            if(!e.dataTransfer.files[0].type.startsWith('image/'))
                return;
            let img_path = e.dataTransfer.files[0].path;
            if(img_path && img_path != 'NULL'){
                Vue.set(this.form_values , this.config.id , img_path)
                this.is_inpaint = false;
            }      
        },

        on_img_load(){
            if(this.config.get_img_size){
                Vue.set(this.form_values , this.config.id + "__AUX__height" , this.get_size().height )
                Vue.set(this.form_values , this.config.id + "__AUX__width" , this.get_size().width )
            }
        },  

        get_mask_img_b64(){
            return this.$refs.inp_img_canvas.get_img_mask_b64() 
        },

        get_mask_b64(){
            if(this.is_inpaint){
                return  this.$refs.inp_img_canvas.get_mask_b64() 
            } else {
                return undefined
            }
        } , 

        get_size(){
            return this.$refs.inp_img_canvas.get_size()
        },

    },

    computed:{
        img_src(){
            return this.form_values[this.config.id]
        }
    },

    watch: {
        'img_src': {

            handler: function() {
                this.is_inpaint = false
            },
            deep: true
        } , 
    }
}
</script>
<style>
</style>
<style scoped>
.crosshair_cur{
        cursor: crosshair;
    }
</style>