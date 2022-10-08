@import '../assets/css/theme.css';
<template>
    <div id="app">
        <!-- <img alt="Vue logo" src="./assets/logo.png"> -->
        
        <StableDiffusion ref="stable_diffusion"> </StableDiffusion>

            

        
        <div v-if="app_state.is_start_screen">
            <transition name="slide_show">
                <SplashScreen v-if="app_state.show_splash_screen"></SplashScreen>
            </transition>
        </div>
        <ApplicationFrame ref="app_frame" v-else title="DiffusionBee - Stable Diffusion App"

            @menu_item_click_about="show_about"
            @menu_item_click_help="show_help"
            @menu_item_click_close="close_window"
            @menu_item_click_discord="menu_item_click_discord"

        > 
            <template v-slot:txt2img>
                <ImgGenerate v-if="is_mounted && stable_diffusion.is_backend_loaded"  :app_state="app_state" :stable_diffusion="stable_diffusion"></ImgGenerate>
                <div  v-else  class="animatable_content_box ">
                    <LoaderModal :loading_percentage="stable_diffusion.loading_percentage" :loading_desc="stable_diffusion.model_loading_msg"  :loading_title="stable_diffusion.model_loading_title ||'Loading model'"> </LoaderModal>
                </div>

               
            </template>

            <template v-slot:img2img>

                <Img2Img  ref="img2img" v-if="is_mounted && stable_diffusion.is_backend_loaded"  :app_state="app_state" :stable_diffusion="stable_diffusion"></Img2Img>
                <div  v-else  class="animatable_content_box ">
                    <LoaderModal :loading_percentage="stable_diffusion.loading_percentage" :loading_desc="stable_diffusion.model_loading_msg"  :loading_title="stable_diffusion.model_loading_title ||'Loading model'"> </LoaderModal>
                </div>

            </template>

            <template v-slot:outpainting>
                <Outpainting></Outpainting>
            </template>

            <template v-slot:upscale_img>
                <UpscaleImage  :app_state="app_state" ref="upscale_img"></UpscaleImage>
            </template>

            

            

            <template v-slot:history>
                <History :app_state="app_state"></History>
            </template>

            <template v-slot:logs>
                <div class="animatable_content_box ">
                    <p>Logs : </p>

                    <p>
                        <span style="white-space: pre-line">{{app_state.logs}}</span>
                    </p>

                </div>

            </template>
        </ApplicationFrame>

        <LoaderModal v-if="app_state.global_loader_modal_msg" :loading_percentage="-1"  :loading_title="app_state.global_loader_modal_msg"> </LoaderModal>

           

       

    </div>
</template>
<script>

import { bind_app_component } from "./py_vue_bridge.js"
import { send_to_py } from "./py_vue_bridge.js"
import {native_confirm, native_alert } from "./native_functions_vue_bridge.js"
import StableDiffusion from "./StableDiffusion.vue"
import SplashScreen from './components_bare/SplashScreen.vue'
import ApplicationFrame from './components_bare/ApplicationFrame.vue'
import ImgGenerate from './components/ImgGenerate.vue'
import Img2Img from './components/Img2Img.vue'
import Outpainting from './components/Outpainting.vue'
import UpscaleImage from './components/UpscaleImage.vue'

import History from './components/History.vue'

import LoaderModal from './components_bare/LoaderModal.vue'
import Vue from "vue"

native_alert;

export default 

{
    name: 'App',
    components: {
        SplashScreen,
        ApplicationFrame,
        ImgGenerate, 
        StableDiffusion,
        LoaderModal,
        History,
        Img2Img,
        Outpainting,
        UpscaleImage
    },

    mounted() {

        this.stable_diffusion = this.$refs.stable_diffusion;

        bind_app_component(this);
        send_to_py("strt");

        if( require('../package.json').is_dev || require('../package.json').build_number.includes("dev") )
            alert("Not checking for updates.")
        else
            this.check_for_updates()

        let that = this;

        setTimeout( function(){
             
            that.app_state.is_start_screen = false;
        }  , 4000)

        this.is_mounted = true;


        let data = window.ipcRenderer.sendSync('load_data');
        if( data.history)
            Vue.set(this.app_state , 'history' , data.history)
     
    },

    watch: {
        'app_state.is_start_screen': {

            handler: function(new_value) {
                if (new_value == false) {
                    if(this.is_screen_frozen){
                        window.ipcRenderer.sendSync('unfreeze_win', '');
                        this.is_screen_frozen = false;
                    }
                    
                }
                else{
                    if(!this.is_screen_frozen){
                        window.ipcRenderer.sendSync('freeze_win', '');
                        this.is_screen_frozen = true;
                    }
                }
            },
            deep: true
        } , 

        'app_state.history': {

            handler: function(new_value) {
                window.ipcRenderer.sendSync('save_data', {"history": new_value });
            },
            deep: true
        } , 
        

    },

    computed : {
    },

    methods: {

        main_screen() {


        },

        
        change_startscreen_tab(tab_name){
            let that = this;
            setTimeout( function(){
                that.$refs.start_screen.on_sidebar_click(tab_name);
            } , 50 )
            
        },

       
        check_for_updates(){
            
            let xmlHttp = new XMLHttpRequest();
            let user_id = window.ipcRenderer.sendSync('get_instance_id' , '');
            let updates_url = "https://aeyfmzu2ac.execute-api.us-east-1.amazonaws.com/check_diffusionbee_updates?user_id="+user_id;
            xmlHttp.onreadystatechange = function() { 
                if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
                {

                    let latest_app_version = xmlHttp.responseText.split("|")[0];
                    console.log("Latest app version" + latest_app_version+ " " + user_id)
                    let current_versoin = require('../package.json').version + "_" + require('../package.json').build_number
                    if( latest_app_version != current_versoin ){
                        if(native_confirm("A new version of " + require('../package.json').name +" is available. Do you want to visit " +require('../package.json').website+ " to update?"  ))
                            window.ipcRenderer.sendSync('open_url', require('../package.json').website);
                    }
                }
            }
            xmlHttp.open("GET", updates_url, true); // true for asynchronous 
            xmlHttp.send(null);
        },

        switch_frame_tab(tab_name){
            // switch the tab of the frame 
            this.$refs.app_frame.selected_tab = tab_name;
        } , 

        set_show_dialog_on_quit(){
            // determine whether electron process should show a confirmation message while closing or not 
            if(! this.$refs.stable_diffusion.is_backend_loaded )
            {
                this.should_show_dialog_on_quit = true;
                this.show_dialog_on_quit_msg = 'Model has not finished loading. Are you sure you want to quit?';
                window.ipcRenderer.sendSync('show_dialog_on_quit', this.show_dialog_on_quit_msg);
            }
            else if( ! this.$refs.stable_diffusion.is_input_avail )
            {
                this.should_show_dialog_on_quit = true;
                this.show_dialog_on_quit_msg = 'Images are still being generated. Are you sure you want to quit?';
                window.ipcRenderer.sendSync('show_dialog_on_quit', this.show_dialog_on_quit_msg);
            }
            else
            {
                this.should_show_dialog_on_quit = false;
                window.ipcRenderer.sendSync('dont_show_dialog_on_quit', '');
            }
        } , 

        show_about(){
            window.ipcRenderer.sendSync('show_about', '');
        },
        show_help(){
            window.ipcRenderer.sendSync('open_url', "https://diffusionbee.com");
        } ,

        menu_item_click_discord(){
            window.ipcRenderer.sendSync('open_url', "https://discord.gg/t6rC5RaJQn");
        },

        close_window(){
            window.ipcRenderer.sendSync('close_window', '');
        }
    },

    data() {
        let app_state = {
            is_start_screen: true, // if the start screen is showing or not
            app_object : this , 
            should_show_dialog_on_quit : false ,  // should ask "do you wanna quit" on closing
            show_dialog_on_quit_msg : "" ,  // the message to show while quiting 
            show_splash_screen : true , // is showing the loading splash screen
            logs : "",
            global_loader_modal_msg : "",
            history : {},
        };

        return {
            is_mounted : false,
            app_state: app_state,
            is_screen_frozen : true , 
            is_dev : require('../package.json').is_dev ||  require('../package.json').build_number.includes("dev") ,
        }
    },



}
</script>
<style>
#app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #2c3e50;
    /*margin-top: 60px;*/
}

body {
    margin: 0;
    padding: 0;
}
</style>