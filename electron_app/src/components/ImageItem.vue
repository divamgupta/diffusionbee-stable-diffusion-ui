<template>
    <div style="height:100%">
        <img   @click="open_image_popup( path )"  class="gal_img" :src="'file://' + path " v-bind:style="style_obj">
        <br>
        <div @click="save_image(path)" class="l_button">Save Image</div>
    </div>
</template>
<script>

import {open_popup} from "../utils"

export default {
    name: 'ImageItem',
    props: {
        path : String,
        style_obj:String
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

    },
}
</script>
<style>
</style>
<style scoped>
</style>