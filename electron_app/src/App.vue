<template>
    <div id="app">
        <!-- <img alt="Vue logo" src="./assets/logo.png"> -->


        <div v-if="app_state.is_start_screen">
            <transition name="slide_show">
                <SplashScreen v-if="app_state.show_splash_screen"></SplashScreen>
            </transition>
        </div>
        <ApplicationFrame v-else title="DiffusionBee - Stable Diffusion GUI"

            @menu_item_click_about="show_about"
            @menu_item_click_help="show_help"
            @menu_item_click_close="close_window"

        > 


            <template v-slot:txt2img>
                <ImgGenerate :app_state="app_state"></ImgGenerate>

            </template>
            <template v-slot:img2img>
                <div class="center">
                     Coming soon!
                </div>
               
            </template>
            <template v-slot:logs>
                
                <div  class="animatable_content_box ">
                    

                    Logs : 

                    <p>
                        <span style="white-space: pre-line">{{app_state.logs}}</span>


                        
                    </p>

                </div>

            </template>

        </ApplicationFrame>



    </div>
</template>
<script>

import { bind_app_component } from "./py_vue_bridge.js"
import { send_to_py } from "./py_vue_bridge.js"
import {native_confirm, native_alert } from "./native_functions_vue_bridge.js"
import SplashScreen from './components_bare/SplashScreen.vue'
import ApplicationFrame from './components_bare/ApplicationFrame.vue'
import ImgGenerate from './components/ImgGenerate.vue'

native_alert;

export default 

{
    name: 'App',
    components: {
        SplashScreen,
        ApplicationFrame,
        ImgGenerate
    },

    mounted() {
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

        'app_state.train.state': {
            handler: function() {
                this.set_show_dialog_on_quit();
            },
            deep: true
        } ,   

        'app_state.progress_modal.is_showing': {
            handler: function() {
                this.set_show_dialog_on_quit();
            },
            deep: true
        } ,   

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
            if(this.app_state.train.state == "paused" || this.app_state.train.state == "training" )
            {
                this.should_show_dialog_on_quit = true;
                this.show_dialog_on_quit_msg = 'Training has not been completed. Are you sure you want to quit?';
                window.ipcRenderer.sendSync('show_dialog_on_quit', this.show_dialog_on_quit_msg);
            }
            else if( this.app_state.progress_modal.is_showing)
            {
                this.should_show_dialog_on_quit = true;
                this.show_dialog_on_quit_msg = 'Are you sure you want to quit?';
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
            window.ipcRenderer.sendSync('open_url', "https://github.com/divamgupta/diffusionbee-stable-diffusion-ui");
        } ,

        close_window(){
            window.ipcRenderer.sendSync('close_window', '');
        }



    },


    data() {

        let app_state = {

            is_start_screen: true, // if the start screen is showing or not
            
            should_show_dialog_on_quit : false ,  // should ask "do you wanna quit" on closing
            show_dialog_on_quit_msg : "" ,  // the message to show while quiting 

            is_model_loaded : false , 
            is_textbox_avail : false, 
            loading_msg : "" , 
            loading_percentage : - 2 ,
            loading_desc : "" , 


            show_splash_screen : true , // is showing the loading splash screen
            current_project_type : "" , // the project type whcih is opened right now 
            logs : "",

            generated_image : "",
            backedn_error : "",

            prompt : "",



        };



        return {
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