@import '../assets/css/theme.css';
<template>
    <div  class="animatable_content_box ">

        <b-form-input
            onkeypress="return event.keyCode != 13;"
            size="sm"
            placeholder="Search by prompt text"
            v-model="searchText"
            autofocus
            debounce="200"
            style="max-width: 240px; float: left; margin-right: 30px;"
            id="searchText"
        />

        <div @click="toggle_order()" style="float:right; margin-bottom: 20px;" class="l_button">
          {{this.app_state.show_history_in_oldest_first ? "Oldest": "Newest"}} First
        </div>
        <div @click="clear_history()" style="float:right; margin-bottom: 20px;" class="l_button">
          Clear History
        </div>
        <div v-if="Object.values(app_state.app_data.history).length > 0">
                <div v-if="Object.values(app_state.app_data.history).length > 30">
                    <b-pagination
                        v-model="currentPage"
                        :total-rows="Object.values(app_state.app_data.history).length"
                        :per-page="30"
                    />
                </div>
                <div v-for="history_box in get_history().slice((currentPage - 1) * 30, currentPage * 30)" :key="history_box.key" style="clear: both;">

            
                <div @click="delete_hist(history_box.key)" style="float:right; margin-top: 10px;"  class="l_button">Delete</div>
                <!-- <div @click="share_on_arthub(history_box)" style="float:right; margin-top: 10px;"  class="l_button">Share</div> -->

                <b-dropdown left variant="link" size="sm" toggle-class="text-decoration-none" no-caret style="float:right; margin-top: 5px;">
                    <template #button-content>
                        <div   class=" l_button "  >
                            Share 
                        </div>
                    </template>
                    <b-dropdown-item-button   @click="share_on_arthub(history_box)"  >Share on ArtHub.ai</b-dropdown-item-button>
                </b-dropdown>

                
                <p class="history_box_info text_bg" style="user-select: text;">
                    <img  v-if="history_box.inp_img" :src="'file://' + history_box.inp_img" style="height:50px">
                    <br  v-if="history_box.inp_img" >
                    <br  v-if="history_box.inp_img" >
              
                    <span style="opacity: 0.5;" v-if="get_box_params_str(history_box)"> {{get_box_params_str(history_box)}} </span>
                    <br   v-if="get_box_params_str(history_box)">
                    
                    {{history_box.prompt}}


                </p>
                
                <div v-for="img in history_box.imgs" :key="img" class="history_box">
                
                    <ImageItem :app_state="app_state" :hide_extra_save_button="true" :path="img" :style_obj="{height:'100%'}"></ImageItem>
                
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
import ImageItem from '../components/ImageItem.vue'
import {native_confirm} from "../native_functions_vue_bridge.js";
import {share_on_arthub} from '../utils.js'

import Vue from 'vue'
import Fuse from 'fuse.js'

export default {
    name: 'History',
    props: {
        app_state : Object,
    },
    components: {
        ImageItem
    },
    mounted() {

    },
    data() {
        return {
            searchText: '',
            currentPage: 1,
        };
    },
    methods: {
        delete_hist(k){
            Vue.delete( this.app_state.app_data.history , k );
        },

        get_history() {
          let history = Object.values(this.app_state.app_data.history);
          const that = this;
          const list = this.app_state.show_history_in_oldest_first ? history : history.reverse();

          if (that.searchText.trim() === '') {
            return list;
          }
          
          const fuse = new Fuse(list, {
            keys: ['prompt'],
            useExtendedSearch: true,
          });
          
          return fuse.search(that.searchText).map(r => r.item);

        },

        toggle_order() {
           Vue.set( this.app_state, "show_history_in_oldest_first", !this.app_state.show_history_in_oldest_first);
        },

        get_box_params_dict(box){
            let r = {};
            let vals = {"seed" : "Seed" , "guidence_scale" : "Scale" , "dif_steps":"Steps"  , "inp_img_strength" : "Image Strength" , "img_w":"Img Width" , "img_h": "Img Height" , "negative_prompt" : "Negative Prompt" , "model_version":"model_version"}
            for(let k in vals)
                if( box[k])
                    r[vals[k]] =  box[k];
            return r;
        },

        get_box_params_str(box){
            let r = "";
            let d = this.get_box_params_dict(box)
            for(let k in d)
                    r += " " +k  +  " : " + d[k] + " |";
            if(r.charAt(r.length - 1) == "|")
                r = r.slice(0, -1);
            return r;
        },

         clear_history(){
            if (native_confirm("Are you sure you want to clear history?")){
                Vue.set( this.app_state.app_data, "history", {});
            }
        },

        share_on_arthub(box){
            this.app_state.global_loader_modal_msg = "Uploading";
            let params = this.get_box_params_dict(box);
            let that = this;
            share_on_arthub(box.imgs , params , box.prompt).then((
                function(){ that.app_state.global_loader_modal_msg = ""}
            )).catch(
                function(){alert("Error in uploading.") ; that.app_state.global_loader_modal_msg = ""}
            )
        }

    },
}
</script>
<style>
.page-item .page-link{
    outline: none !important;
   box-shadow: none;
}
.page-item .page-link{
    font-size: 13px;
}
@media (prefers-color-scheme: dark) {
    .page-item .page-link, .page-item.disabled .page-link{
        background-color:#303030;
        border-color: #303030;
        color:rgba(255, 255, 255, 0.5);
    }
    .page-item.active .page-link{
        background-color:#606060;
        border-color: #606060;
    }
}
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
