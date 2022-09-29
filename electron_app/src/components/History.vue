@import '../assets/css/theme.css';
<template>
    <div  class="animatable_content_box ">
    
        <div v-if="Object.values(app_state.history).length > 0">
            <div v-for="history_box in Object.values(app_state.history).reverse()" :key="history_box.key" style="clear: both;">
            
                <div @click="delete_hist(history_box.key)" style="float:right; margin-top: 10px;"  class="l_button">Delete</div>
                <p class="history_box_info text_bg">
                    <img  v-if="history_box.inp_img" :src="'file://' + history_box.inp_img" style="height:50px">
                    <br  v-if="history_box.inp_img" >
                    <br  v-if="history_box.inp_img" >
              
                    <span style="opacity: 0.5;" v-if="history_box.seed"> Seed : {{history_box.seed}} </span>
                    <br  v-if="history_box.seed">
                    
                    {{history_box.prompt}}


                </p>
                
                <div v-for="img in history_box.imgs" :key="img" class="history_box">
                    
                    <img  @click="open_image_popup({ img, title: history_box.prompt })"  class="gal_img" v-if="img" :src="'file://' + img" style="height:100%">
                    <br>
                    <div @click="save_image(img, history_box.prompt, history_box.seed)" class="l_button">Save Image</div>
                    <br>
                
                </div>
                <div style="clear: both; display: table; margin-bottom: 10px;">
                </div>
                
                <hr>
            </div>
        </div>
        <div v-else>
            <div class="center">
                    <p>No images generated yet.</p>
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
        open_image_popup(props){
            window.ipcRenderer.sendSync('open_popup', props);
        },

    },
}
</script>
<style>
</style>
<style scoped>
.history_box_info {
   
    padding :12px;
    border-radius: 5px;
    max-width: calc(100vw - 200px );
}



.history_box {
    height:230px;
    float:left;
    margin-right: 10px;
    margin-bottom: 30px;
}
</style>