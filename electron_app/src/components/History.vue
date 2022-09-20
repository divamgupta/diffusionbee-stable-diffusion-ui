<template>
    <div  class="animatable_content_box ">
    
        <div v-if="Object.values(app_state.history).length > 0">
            <div v-for="history_box in Object.values(app_state.history)" :key="history_box.key" style="clear: both;">
            
                <div @click="delete_hist(history_box.key)" style="float:right; margin-top: 10px;"  class="l_button">Delete</div>
                <p style="background-color: rgba(0, 0, 0, 0.05); padding :12px; border-radius: 5px; max-width: calc(100vw - 200px );">{{history_box.promt}}</p>
            
                
                
                <div v-for="img in history_box.imgs" :key="img" style="height:230px; float:left; margin-right: 10px; margin-bottom: 30px;">
                    
                    <img  class="gal_img" v-if="img" :src="'file://' + img" style="height:100%">
                    <br>
                    <div @click="save_image(img)" class="l_button">Save Image</div>
                    <br>
                
                </div>
                <div style="clear: both; display: table; margin-bottom: 10px;">
                </div>
                
                <hr>
            </div>
        </div>
        <div v-else>
            <div class="center">
                    No images generated yet.
                </div>
        </div>
        
        
    </div>
</template>
<script>

import Vue from 'vue'

export default {
    name: 'History',
    props: {
        app_state : Object,
    },
    components: {
       
    },
    mounted() {

    },
    data() {
        return {};
    },
    methods: { 
        delete_hist(k){
            Vue.delete( this.app_state.history , k );
        }, 

        save_image(generated_image){
            if(!generated_image)
                return;
            generated_image = generated_image.split("?")[0];
            let out_path = window.ipcRenderer.sendSync('save_dialog', '');
            if(!out_path)
                return
            let org_path = generated_image.replaceAll("file://" , "")
            window.ipcRenderer.sendSync('save_file', org_path+"||" +out_path);
        }

    },
}
</script>
<style>
</style>
<style scoped>
</style>