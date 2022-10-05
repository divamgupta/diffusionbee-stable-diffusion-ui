@import '../assets/css/theme.css';
<template>
    <div  class="animatable_content_box ">
        <div @click="toggle_order()" style="float:right; margin-bottom: 20px;" class="l_button">
          {{this.app_state.show_history_in_oldest_first ? "Oldest": "Newest"}} First
        </div>
        <div v-if="Object.values(app_state.history).length > 0">
            <div v-for="history_box in get_history()" :key="history_box.key" style="clear: both;">
            
                <div @click="delete_hist(history_box.key)" style="float:right; margin-top: 10px;"  class="l_button">Delete</div>
                <p class="history_box_info text_bg" style="user-select: text;">
                    <img  v-if="history_box.inp_img" :src="'file://' + history_box.inp_img" style="height:50px">
                    <br  v-if="history_box.inp_img" >
                    <br  v-if="history_box.inp_img" >
              
                    <span style="opacity: 0.5;" v-if="get_box_params_str(history_box)"> {{get_box_params_str(history_box)}} </span>
                    <br   v-if="get_box_params_str(history_box)">
                    
                    {{history_box.prompt}}


                </p>
                
                <div v-for="img in history_box.imgs" :key="img" class="history_box">
                    
                    <img  @click="open_image_popup( img )"  class="gal_img" v-if="img" :src="'file://' + img" style="height:100%">
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
import {open_popup} from "../utils"

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

        get_history() {
          let history = Object.values(this.app_state.history);
          return this.app_state.show_history_in_oldest_first ? history : history.reverse();
        },

        toggle_order() {
           Vue.set( this.app_state, "show_history_in_oldest_first", !this.app_state.show_history_in_oldest_first);
        },

        get_box_params_str(box){
            let r = "";
            let vals = {"seed" : "Seed" , "guidence_scale" : "Scale" , "dif_steps":"Steps"  , "inp_img_strength" : "Image Strength" , "img_w":"Img Width" , "img_h": "Img Height"}
            for(let k in vals)
                if( box[k])
                    r += " " + vals[k] +  " : " + box[k] + " |";
            if(r.charAt(r.length - 1) == "|")
                r = r.slice(0, -1);
            return r;

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

        open_image_popup(img){
            open_popup("file://"+img , undefined);
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
