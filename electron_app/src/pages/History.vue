
<template>
    <div  style="width:100%; height:100%; ">

        <!-- toolbox -->
        <div style="height: 60px ; padding:10px ; width:100% ">
            
            <b-form-input
                @input="currentPage=1"
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
              {{this.show_history_in_oldest_first ? "Newest": "Oldest"}} First
            </div>
            <div @click="clear_history()" style="float:right; margin-bottom: 20px;" class="l_button">
              Clear History
            </div>

            <div v-if="Object.values(history).length > 0">
                <div v-if="history_to_show.length > 30">
                    <b-pagination
                        v-model="currentPage"
                        :total-rows="history_to_show.length"
                        :per-page="30"
                    />
                </div>
            </div>

        </div>

        <div style="height: calc(100% - 60px) ; width: 100% ; overflow-y:auto;">
            <div v-if="Object.values(history).length > 0">

                <hr>
        
                <div v-for="group in history_to_show.slice((currentPage - 1) * 30, currentPage * 30)" :key="group.key" style="clear: both;">

                
                    <div @click="delete_hist(group.key)" style="float:right; margin-top: 10px;"  class="l_button">Delete</div>
                    <!-- <div @click="share_on_arthub(group)" style="float:right; margin-top: 10px;"  class="l_button">Share</div> -->

                    <b-dropdown left variant="link" size="sm" toggle-class="text-decoration-none" no-caret style="float:right; margin-top: 5px;">
                        <template #button-content>
                            <div   class=" l_button "  >
                                Share 
                            </div>
                        </template>
                        <b-dropdown-item-button   @click="share_on_arthub(group)"  >Share on ArtHub.ai</b-dropdown-item-button>
                    </b-dropdown>

                    
                    <p class="history_box_info " style="user-select: text;">
                        <img  v-for=" img in get_inp_imgs_from_group(group)" :src="'file://' +img" :key="img" style="height:50px">
                        <br  v-if="get_inp_imgs_from_group(group).length > 0 " >
                        <br  v-if="get_inp_imgs_from_group(group).length > 0 " >
                  
                        <span style="opacity: 0.5;" v-if="get_box_params_str(group)"> {{get_box_params_str(group)}} </span>
                        <br   v-if="get_box_params_str(group)">
                        
                        {{group.params.prompt}}


                    </p>
                    
                    <GalleryPane :n_imgs="group.num_imgs"  :img_w="group.img_width"  :img_h="group.img_height"  :image_data="group.imgs" :menu_items="menu_items" :on_menu_item_click="on_image_menu_item_click"   :always_fixed_col_size="300"  :on_image_click="on_image_click" > </GalleryPane>


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
    </div>
</template>
<script>
import {native_confirm} from "../native_functions_vue_bridge.js";
import {share_on_arthub} from '../utils.js'
import GalleryPane from "../components_bare/GalleryPane.vue"
import {image_manu_functions} from "../components/image_menu_functions.js"
import {open_popup , form_params_to_text , form_params_to_readable_dict, migrate_history_only_once} from "../utils"

import Vue from 'vue'
import Fuse from 'fuse.js'

const History =  {
    name: 'History',
    props: {
        app:Object, 
    },
    components: {
        GalleryPane
    },
    mounted() {
        this.app.functions.add_to_history = this.add_to_history
    },
    data() {
        let history = {}
        let hist = window.ipcRenderer.sendSync('load_data' , 'history.json')
        if(hist.history){
            history = hist.history;
        }

        try {
            let new_items = migrate_history_only_once( history)
            for(let k in new_items){
                history[k] = new_items[k]
            }
        } catch (error) {
            console.error(error);
        }

        

        let menu_items = []
        for(let fn of Object.keys(image_manu_functions)){
            if(fn != "use_params_current_page")
            {
                menu_items.push({id: fn , text: image_manu_functions[fn].text })
            }
        }


        return {
            app_state : this.app.app_state,
            searchText: '',
            currentPage: 1,
            history : history,
            show_history_in_oldest_first : false,
            menu_items :menu_items,
        };
    },

    computed: {
      history_to_show() {
          let history = Object.values(this.history);
          const that = this;
          const list = this.show_history_in_oldest_first ? history : history.reverse();
          if (that.searchText.trim() === '') {
            return list;
          }
          
          const fuse = new Fuse(list, {
            keys: ['prompt'],
            useExtendedSearch: true,
          });

          return fuse.search(that.searchText).map(r => r.item);

       },
    },

    watch: {
        'history': {
            handler: function() {
                this.save_history()
            },
            deep: false
        } , 
    }, 


    methods: {


        get_inp_imgs_from_group(group){

            let ret = []

            let i1 = (group.params || {}).input_image_with_mask
            if(i1 && i1 != "" && i1 != 'undefined')
                ret.push(i1)

            if( (group.params || {}).controlnet_input_image_path )
                ret.push( (group.params || {}).controlnet_input_image_path )

            return ret
        },


        add_to_history(k , history_vals ){
            history_vals = JSON.parse(JSON.stringify(history_vals))
            console.log("got to hist")
            console.log(history_vals)
            if(history_vals.imgs.length == 0)
                return
            history_vals.params = history_vals.imgs[0].params
            history_vals.key = k
            history_vals.prompt = history_vals.params.prompt
            Vue.set(this.history ,  k , history_vals )
        },

        on_image_click(image_item_data){
            open_popup('file://' + image_item_data.image_url)
        },

        delete_hist(k){
            Vue.delete( this.history , k );
        },

        save_history(){
            window.ipcRenderer.sendSync('save_data', {"history": this.history} , 'history.json');
        },

        toggle_order() {
           Vue.set( this, "show_history_in_oldest_first", !this.show_history_in_oldest_first);
        },

        on_image_menu_item_click(menu_item_id , image_item_data){
            image_manu_functions[menu_item_id](this.app , image_item_data )
        },

        get_box_params_str(box){
            return form_params_to_text(box.params)
        },

         clear_history(){
            if (native_confirm("Are you sure you want to clear history?")){
                Vue.set( this , "history", {});
            }
        },

        share_on_arthub(box){
            this.app.app_state.global_loader_modal_msg = "Uploading";
            let params = form_params_to_readable_dict(box.params);
            let that = this;
            let imgs = (box.imgs.map(x => x.image_url ) )
            share_on_arthub( imgs , params , box.prompt).then((
                function(){ that.app.app_state.global_loader_modal_msg = ""}
            )).catch(
                function(e ){ console.log(e); alert("Error in uploading.") ; that.app.app_state.global_loader_modal_msg = ""}
            )
        }

    },
}

export default History;
History.title = "History"
History.icon = "history"
History.description = "View generated images"
History.img_icon = require("../assets/imgs/page_icon_imgs/history.png")
History.home_category = "pages"
History.sidebar_show = "always"


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
