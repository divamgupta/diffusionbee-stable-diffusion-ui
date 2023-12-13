<template>
    <div> 
        <div class="options_input" style="width: 100%;">
         
            <img :src="'file://'+config.img_path" style="max-width: 100%;"> 
            <div v-if="config.is_save" @click="save_image" class="l_button" > Save </div>
        
        </div>
    <br> 
    </div>
    
</template>
<script>

import FormInputMixin from "./FormInputMixin.vue"
import { icon_library } from "../icon_library.js"


export default {
    name: 'OutputImage',
    mixins: [FormInputMixin],
    props: {
         config: Object , 
        form_values: Object,
    },
    components: {},
    mounted() {
      
    },
    data() {
        return {
            icon_library:icon_library,
        };
    },
    methods: {

        save_image(){

            let image_url = this.config.img_path
          
            if(!image_url)
                return;
            let im_path = image_url.split("?")[0];


            let suggested_fname = "Output"
            let out_path = window.ipcRenderer.sendSync('save_dialog', suggested_fname, this.config.save_ext );
            if(!out_path)
                return
            let org_path = im_path.replaceAll("file://" , "")
            window.ipcRenderer.sendSync('save_file', org_path+"||" +out_path);

        }
       
    },
}
</script>
<style>
</style>
<style scoped>

</style>