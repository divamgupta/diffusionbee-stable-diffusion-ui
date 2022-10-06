@import '../assets/css/theme.css';

<template>
    <div  class="animatable_content_box ">

        <div v-if="output_image">
            
            <center>
                <h2>Image Upscaled 4x</h2>
                <ImageItem :hide_dropdown="true" :app_state="app_state"  :path="output_image" :style_obj="{ 'max-height': '90%' , 'max-width': '80%' , 'margin-top': '30px' }"></ImageItem>
            </center>
        </div>
        <div v-else-if="error">
            <p>{{error}}</p>
        </div>
        <div v-else>
            <LoaderModal :loading_percentage="-1" loading_title="Upscaling"></LoaderModal>
        </div>
    </div>
</template>
<script>

import LoaderModal from '../components_bare/LoaderModal.vue'
import ImageItem from '../components/ImageItem.vue'


export default {
    name: 'UpscaleImage',
    props: {
        app_state : Object , 
    },
    components: {LoaderModal ,  ImageItem },
    mounted() {

    },
    data() {
        return {
            output_image : "",
            error : "",
        };
    },
    methods: {
        do_upscale(in_img){
            let that = this;
            that.output_image = "";
            this.error = "";
            window.ipcRenderer.invoke('run_realesrgan', in_img.split("?")[0] ).then((result) => {
                if(result) 
                    that.output_image = result;
                else
                    that.error = "Error in upscaling this image";
            })
        }
    },
}
</script>
<style>
</style>
<style scoped>
</style>