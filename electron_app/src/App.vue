@import '../assets/css/theme.css';
<template>
    <div id="app">
        <!-- <img alt="Vue logo" src="./assets/logo.png"> -->
        
        <StableDiffusion ref="stable_diffusion"> </StableDiffusion>
        <SDManager :app="app" ref="sd_manager"> </SDManager>
        <AssetsManager ref="assets_manager"> </AssetsManager>
        
        <div v-if="app_state.is_start_screen">
            <transition name="slide_show">
                <SplashScreen v-if="app_state.show_splash_screen"></SplashScreen>
            </transition>
        </div>
        <ApplicationFrame ref="app_frame" v-else :title="current_applet_title + ' - ' + 'DiffusionBee'" :sidebar_item_on_click="sidebar_item_on_click"
        :sidebar_items="
            (all_pages_ready ) ?  $refs.router.all_sidebar_items : []
        " :selected_sidebar_item_id="current_selected_tab"
        :on_home_click="on_home_click"
        > 
            
            <template v-slot:main_content>
                <PagesRouter  v-if="is_mounted && stable_diffusion.is_ready()"  :app="app" ref="router" > </PagesRouter>
            </template>

            <template v-slot:main_toolbar>
                <MainToolbar  v-if="is_mounted"  :app="app" ref="toolbar" > </MainToolbar>
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
import SDManager from "./SDManager.vue"
import AssetsManager from "./AssetsManager.vue"

import SplashScreen from './components_bare/SplashScreen.vue'
import ApplicationFrame from './components_bare/ApplicationFrame.vue'

import PagesRouter from "./components/PagesRouter.vue"
import MainToolbar from "./components/MainToolbar.vue"

import LoaderModal from './components_bare/LoaderModal.vue'
import Vue from "vue"

native_alert;

export default 

{
    name: 'App',
    components: {
        SplashScreen,
        ApplicationFrame,
        AssetsManager,
        StableDiffusion,
        SDManager,
        LoaderModal,
        PagesRouter,
        MainToolbar
       
    },

    mounted() {
        this.app = this;
        window.app = this.app; // so that we can access from console
        this.stable_diffusion = this.$refs.stable_diffusion;
        this.stable_diffusion_manager = this.$refs.sd_manager;
        this.stable_diffusion_manager.stable_diffusion = this.stable_diffusion;
        this.assets_manager = this.$refs.assets_manager;

        bind_app_component(this);
        send_to_py("strt");

        if( require('../package.json').is_dev || require('../package.json').build_number.includes("dev") )
            alert("Not checking for updates.")
        else
            this.check_for_updates()

        let that = this;

        this.start_screen_interval = setInterval( function(){
            console.log(that.stable_diffusion.is_input_avai)
            if(that.stable_diffusion && that.stable_diffusion.is_input_avail){
                that.app_state.is_start_screen = false;
                clearInterval(that.start_screen_interval)
            }
            
        }  , 1500)

        this.is_mounted = true;

        let data = window.ipcRenderer.sendSync('load_data', 'app_data_2.json');
        if(!data.history){
            data.history = {}
        }
        if(!data.settings){
            data.settings = {}
        }
        if(data.settings.notification_sound == undefined)
            data.settings.notification_sound = true

        if(!data.custom_models){
            data.custom_models = {}
        }
        if( data ){
            Vue.set(this.app_state , 'app_data' , data)
        }
     
    },

    watch: {
        'app_state.is_start_screen': {

            handler: function(new_value) {
                if (new_value == false) {
                    if(this.is_screen_frozen){
                        console.log("Unfreeze win!")
                        window.ipcRenderer.sendSync('unfreeze_win', '');
                        this.is_screen_frozen = false;
                    }
                    
                }
                else{
                    if(!this.is_screen_frozen){
                        console.log("Freeze win!")
                        window.ipcRenderer.sendSync('freeze_win', '');
                        this.is_screen_frozen = true;
                    }
                }
            },
            deep: true
        } , 

        'app_state.app_data': {

            handler: function(new_value) {
                window.ipcRenderer.sendSync('save_data', new_value , "app_data_2.json");
            },
            deep: true
        } , 

        'is_sd_avail' : {
            handler: function() {
                this.set_show_dialog_on_quit()
            },
            deep: true
        }
        
    },

    computed : {
        is_sd_avail(){
            if(!this.is_mounted)
                return false
            return this.$refs.stable_diffusion.is_input_avail 
        }
    },

    methods: {

        main_screen() {

        },

        show_toast(msg){
            Vue.$toast.default(msg)
        },

        sidebar_item_on_click(t){
            this.current_selected_tab = t;
            this.functions.switch_page(t);
        }, 

        on_home_click(){
            this.functions.switch_page("Homepage")
        },
       
        check_for_updates(){
            
            let xmlHttp = new XMLHttpRequest();
            let user_id = window.ipcRenderer.sendSync('get_instance_id' , '');
            let updates_url = "https://checkupdates.diffusionbee.com/check_diffusionbee_updates?user_id="+user_id;
            xmlHttp.onreadystatechange = function() { 
                if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
                {

                    let latest_app_version = xmlHttp.responseText.split("|")[0];
                    console.log("Latest app version" + latest_app_version+ " " + user_id)
                    let current_versoin = require('../package.json').version + "_" + require('../package.json').build_number
                    let latest_build_no = Number(latest_app_version.split("_")[1])
                    let current_build_no = Number(require('../package.json').build_number)
                    if( latest_app_version != current_versoin && latest_build_no > current_build_no ){
                        if(native_confirm("A new version of " + require('../package.json').name +" is available. Do you want to visit " +require('../package.json').website+ " to update?"  ))
                            window.ipcRenderer.sendSync('open_url', require('../package.json').website);
                    }
                }
            }
            xmlHttp.open("GET", updates_url, true); // true for asynchronous 
            xmlHttp.send(null);
        },

        set_show_dialog_on_quit(){
            // determine whether electron process should show a confirmation message while closing or not 
            if( ! this.$refs.stable_diffusion.is_input_avail )
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
            registered_ext_applets : {}, // {id, title, desc, icon, inputs, outputs }
            app_data: {history : {}},
        };

        return {
            current_build_number : Number(require('../package.json').build_number), 
            all_pages_ready: false, // set to true by PagesRouter
            is_mounted : false, // set when app is mounted
            functions: {},
            app_state: app_state,
            app: this , // will be set after mount
            current_selected_tab : "Homepage",
            current_applet_title: "Home",
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
