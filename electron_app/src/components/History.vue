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

        <b-popover
          :target="`searchText`"
          title="Extended Search Rules"
          triggers="hover"
        >
            By default the search is fuzzy (i.e. matches search patterns approximately), but you can make it more strict:
            <ul>
            <li>use double quotes to group words</li>
            <li>white space acts as an <b>AND</b> operator, while a single pipe (|) character acts as an <b>OR</b> operator</li>
            <li>use equal sign "=text" to search for prompts that are exactly <b>EQAUL</b> to text</li>
            <li>use single quote "'text" to search for prompts that <b>CONTAIN</b> text exactly</li>
            <li>use exclamation point "!text" to <b>IGNORE</b> prompts containing text</li>
            <li>use caret "^text" to search for prompts <b>BEGINING</b> with text</li>
            <li>use dollar sign "text$" to search for prompts <b>ENDING</b> with text</li>
            </ul>

            <b>Example:</b> <i>!^red | '"red herring"</i> - search for prompts <b>NOT BEGINING</b> with "red" <b>OR</b> prompts <b>CONTAINING</b> text "red herring" (in that order) 
        </b-popover>
        <div @click="toggle_order()" style="float:right; margin-bottom: 20px;" class="l_button">
          {{this.app_state.show_history_in_oldest_first ? "Oldest": "Newest"}} First
        </div>
        <div v-if="Object.values(app_state.history).length > 0">
            <div v-for="history_box in get_history()" :key="history_box.key" style="clear: both;">
            
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
import {share_on_arthub} from '../utils.js'

import Fuse from 'fuse.js'
import Vue from 'vue'

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
            searchText: ''
        };
    },
    methods: {
        delete_hist(k){
            Vue.delete( this.app_state.history , k );
        },

        get_history() {
          let history = Object.values(this.app_state.history);
          const that = this;
          const list = this.app_state.show_history_in_oldest_first ? history : history.reverse();

          if (that.searchText === '') {
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
            let vals = {"seed" : "Seed" , "guidence_scale" : "Scale" , "dif_steps":"Steps"  , "inp_img_strength" : "Image Strength" , "img_w":"Img Width" , "img_h": "Img Height" , "negative_prompt" : "Negative Prompt"}
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
