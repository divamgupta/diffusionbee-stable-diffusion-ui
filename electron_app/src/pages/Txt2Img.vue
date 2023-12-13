<template>
    <SDImageGenerationApplet ref="sd_applet" name="txt2img"  :form_data="form_data" :form_tags="[ 'txt2img']" :app="app"> </SDImageGenerationApplet>
</template>
<script>


import SDImageGenerationApplet from "../components/SDImageGenerationApplet.vue"


const Txt2Img =  {
    name: 'Txt2Img',
    props: {
        app:Object, 
    },
    components: {SDImageGenerationApplet},
    mounted() {

    },
    data() {
        let form_data = require("../forms/sd_options_adv.json")
        return {
            form_data:form_data
        };
    },
    methods: {
       
    },
}


Txt2Img.title = "Text to image"
Txt2Img.icon = "file-image"
Txt2Img.description = "Generate images with text descriptions"
Txt2Img.img_icon = require("../assets/imgs/page_icon_imgs/txt2img.png")
Txt2Img.home_category = "main"
Txt2Img.sidebar_show = "always"

export default Txt2Img;


</script>
<style>
</style>
<style scoped>
</style>