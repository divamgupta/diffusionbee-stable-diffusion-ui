<template>
    <div class="main_frame">


        <div class="sidebar" v-if="is_sidebar_open">
           <div class="sidebar_drag"> 
                 <span class="title_bar_icon" style="float:right; margin-top: 15px; margin-right:10px; padding:0; padding-left: 13px; padding-top:2px ;" @click="is_sidebar_open = !is_sidebar_open"  > 
                   <svg width="20" height="16" viewBox="0 0 20 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                       <path :d="icon_library['sidebar_collapse']"  />
                    </svg>
                </span>

           </div>

           <p class="sidebar_cat"> Tools </p>

           <div v-for="sidebar_item in sidebar_items" :key="sidebar_item.id" class="sidebar_item "  :class="{ sidebar_item_selected : sidebar_item.id ===  selected_sidebar_item_id }" @click="sidebar_item_on_click(sidebar_item.id)"> 

              <svg v-if="icon_library[sidebar_item.icon]" class="sidebar_icon" width="15px" height="15px"  style="height: 15px; width: 15px; margin-top:-3px; margin-right:3px;"  v-html="icon_library[sidebar_item.icon]"> </svg>

              <font-awesome-icon v-else class="sidebar_icon" :icon="sidebar_item.icon" />

                 {{sidebar_item.text}}
             </div>

       
        </div>

        <div class="title_bar">
            <div class="app_title_sidebar_collapsed" v-if="(!is_sidebar_open)"  v-bind:class="{'app_title_sidebar_collapsed_mac':is_mac}"> 
                 <span class="title_bar_icon" style=" margin-right: -10px ; margin-left: 10px;" @click="is_sidebar_open = !is_sidebar_open" > 
                   <svg width="20" height="16" viewBox="0 0 20 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                     <path :d="icon_library['sidebar_collapse']" />
                   </svg>
                 </span>

                 <span class="title_bar_icon" style=" margin-right: -10px ; margin-left: 10px;" @click="on_home_click" > 
                   <font-awesome-icon   icon="home" style="zoom:1.15; margin-bottom: -2px;"  />
                 </span>

            </div>
            <div class="app_title" >
                <span @click="$emit('on_title_click',{})"> {{title}} </span>
            </div>
             <div class="title_bar_icons">
                <!-- <font-awesome-icon  class="title_bar_icon" icon="file-image" />  -->

                <slot name="main_toolbar"></slot>
            </div>

        </div>
        
        <div class="tab_content_frame">
            <div class="tab_content">
                <slot name="main_content"></slot>
            </div>

            


        </div>
    </div>
</template>
<script>

import { icon_library } from "./icon_library.js"

export default {
    name: 'ApplicationFrame',
    components: {},
    props: {
        title: String,
        sidebar_items: Array,
        selected_sidebar_item_id: String,
        sidebar_item_on_click: Function, 
        on_home_click : Function

    },

    data: function() {
        return {
            icon_library : icon_library , 

            selected_tab: 'txt2img' ,
            is_fullscreen: false ,
            is_sidebar_open: true,
        }
    },

     watch: {
        'is_sidebar_open': {

            handler: function(is_open) {
                if(is_open){
                    document.querySelector(':root').style.setProperty("--sidebar-width" , "200px")
                } else {
                    document.querySelector(':root').style.setProperty("--sidebar-width" , "0px")
                }
            },
            deep: true
        } , 
    },

    mounted() {
        window.addEventListener('resize', this.detect_fullscreen);
    },
    unmounted() {
        window.removeEventListener('resize', this.detect_fullscreen);
    },

    computed: {
        is_mac(){
            return !(this.detect_windows_os())
        }
    },

    methods: {
        selectTab(tab) {
            this.selected_tab = tab;
        },

        detect_windows_os(){
            return window.navigator.platform.toLowerCase().startsWith('win');
        },

        detect_fullscreen(){
            let that = this;
            setTimeout(function(){
                if ( window.innerWidth == screen.width && window.innerHeight == screen.height && (!window.screenTop && !window.screenY) )
                    that.is_fullscreen = true ;
                else
                    that.is_fullscreen = false; 
            } , 100)

            
        }
    },


}
</script>
<style>
@import '../assets/css/theme.css';
:root {
    --main-font: -apple-system, BlinkMacSystemFont, sans-serif;
    --main-font-text: -apple-system, BlinkMacSystemFont, sans-serif;
    /*SF Pro Text;*/

     --sidebar-width: 200px;
     --titlebar-height: 55px;
    
}


html {
    user-select: none;
    -moz-user-select: none;
    -webkit-user-select: none;
    -ms-user-select: none;
}

body {
    font-family: var(--main-font);
}


.bl_display{
    display:block !important;
}


.sidebar_icon > path{
    fill:#0A84FF;
}

.sidebar_icon > svg > path{
    fill:#0A84FF;
}

.l_button {
    display: inline-block;
    margin: 0px;
    padding: 3px 10px;
    height: 22px;
    border-radius: 5px;
    font-family: var(--main-font-text);
    font-style: normal;
    font-weight: 600;
    font-size: 13px;
    line-height: 16px;

    text-align: center;
    letter-spacing: -0.08px;

    margin-right: 9px;

    transition: background-color 150ms ease-out 10ms, color 150ms ease-out 10ms;
}

.no_hover_bg:hover{
    background-color: transparent !important;
}


.button_white {
    background-color: white;
    box-shadow: 0px 1px 0px 1px rgba(96, 97, 112, 0.1);
}

.button_white:hover {
    background-color: #E0E0E0;
}

.rounded_button {
    border-radius: 23.3711px;
}

.button_colored {
    background: #3E7BFA;
    color: #FFFFFF;
}

.button_grey {
    background: rgba(0, 0, 0, 0.25);
    color: #FFFFFF;
}

.button_grey:hover {
    background: rgba(0, 0, 0, 0.4);
}

.button_colored:hover {
    background: #3d6ffa;
}

.button_medium {
    height: 30px;
    padding-top: 7px;
    padding-left: 15px;
    padding-right: 15px;
}

.button_color_fancy {

    background: #3E7BFA;
    color: #FFFFFF;
    height: 30px;
    box-shadow: 0px 4px 4px #CCDDFF;
}

.button_color_fancy:hover {

    background: #3E7BFA;
    color: #FFFFFF;
    box-shadow: 1px 1px 4px #CCDDFF;
    ;
}


p {
    font-family: var(--main-font);
    font-style: normal;
    font-weight: 274;
    font-size: 13px;
    line-height: 16px;
    align-items: center;
    letter-spacing: -0.08px;
}

.p_light{
    color: rgba(0, 0, 0, 0.5);
}

h1 {
    font-family: var(--main-font);
    font-style: normal;
    font-weight: 334;
    font-size: 30px;
    line-height: 38px;
    /* identical to box height, or 53% */

    display: flex;
    align-items: center;
    letter-spacing: -0.08px;
}

h2 {

    font-family: var(--main-font-text);
    font-style: normal;
    font-weight: 600;
    font-size: 15px;
    line-height: 16px;
    letter-spacing: -0.08px;
}

h3 {
    font-family: var(--main-font);
    font-style: normal;
    font-weight: 274;
    font-size: 15px;
    line-height: 22px;
    /* or 107% */

    display: flex;
    align-items: center;
    letter-spacing: -0.08px;

}


h4{
    font-family: var(--main-font-text);
    font-style: normal;
    font-weight: 600;
    font-size: 13px;
    line-height: 16px;
}

img {
    user-drag: none;
    -webkit-user-drag: none;
    user-select: none;
    -moz-user-select: none;
    -webkit-user-select: none;
    -ms-user-select: none;
}



/*overriding some styles of bootstrap dropdown*/
.dropdown-item {
    font-size: 13px;
}

.dropdown-menu {
    box-shadow: 0px 5px 10px rgba(0, 0, 0, 0.16);
    border-radius: 5px;
    border: 0.5px solid rgba(0, 0, 0, 0.1);
    /*background: #F4F5F5;*/
}

.opaciy_half{
    opacity: 0.5;
}

/*overriding the bootstraps dropdown highlighting*/
.btn-check:focus, .btn:focus {
    box-shadow: none !important;
}


.content_toolbox{
    margin-bottom: 23px; 
    display: inline-block;
    height: 22px; 
    width: 100%;
}


.bottom_float{
    position: fixed ;
    bottom: 1px;
}


.title_bar_icon{
    color : var(--title-icon_color);
    padding : 8px;
    padding-right: 8px;
    padding-left: 8px;

    margin-right: 2px;
    margin-left: 2px;
    
    height: calc(100% - 24px);
    width:50px;
    border-radius: 5px;

/*    background: rgba(0, 0, 0, 0.05);*/
    -webkit-app-region: none;
    
}

.title_bar_icon svg{
    fill : var(--title-icon_color);
}

.title_bar_icon:hover{
    background-color: var(--button-highlight-one);
}



::-webkit-scrollbar {
    appearance: none;
    width: 7px;
    padding-right: 7px;
}
::-webkit-scrollbar-thumb {
    border-radius: 4px;
    background-color: var(--border-color-invert);
}



</style>
<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>


.title_bar {
    height: var(--titlebar-height);
    width: calc( 100vw - var(--sidebar-width) );
    /*background: red;*/
    margin-left : var(--sidebar-width);
    -webkit-user-select: none;
    -webkit-app-region: drag;
    border-width: 0px;
    border-bottom-width: 1px;
    border-style: solid;
    border-color: var( --thin-border-color);
}


.title_bar_icons{
    float: right;
    margin-right: 20px; 
    height: var(--titlebar-height);
    margin-top: 16px;
}





.sidebar_drag{
    -webkit-user-select: none;
    -webkit-app-region: drag;
    height: var(--titlebar-height);
}

.app_title_sidebar_collapsed{
    float:left;
    height: var(--titlebar-height);
    margin-top: 16px;

}

.app_title_sidebar_collapsed_mac{
    margin-left: 72px;
}

.app_title {
    float: left;
    padding-left: 22px;
    padding-top: 20px;

    font-family: var(--main-font-text);
    font-style: normal;
    font-weight: 600;
    font-size: 15px;
    line-height: 16px;

    letter-spacing: -0.08px;

    color: #000000;
}






.sidebar{
    position: fixed;
    top:0 ;
    left: 0 ;
    bottom: 0 ;
    background-color: var(--sidebar-color);
 
    width: var(--sidebar-width) ;
}


.sidebar_cat{
   
    color: rgba(0, 0, 0, 0.27);
    font-family: var(--main-font-text);
    font-style: normal;
    font-weight: 600;
    font-size: 12px;
    line-height: 13px;
    /* identical to box height, or 130% */

    letter-spacing: 0.12px;
    margin-left: 15px ;
    margin-top: 15px ;
    margin-bottom: 7px;
}


.sidebar_item{

    font-family: var(--main-font-text);
    font-style: normal;
    font-weight: 400;
    font-size: 14px;
    line-height: 14px;
    /* identical to box height, or 127% */

    letter-spacing: 0.06px;

    /* Dark/Text */

    color: var(--text-color-solid);;
    margin-left: 15px ;
    margin-right: 15px ;
    margin-bottom: 4px ;

    padding-right: 15px;
    padding-left: 15px;
    padding-bottom: 7px;
    padding-top: 7px;

    border-radius: 5px;

    
}

.sidebar_icon{
    margin-right: 5px;
    color: #0A84FF;
}

.sidebar_item_selected{
     background: rgba(0, 0, 0, 0.1);
}

.sidebar_item:hover{
    background-color: var(--button-highlight-one);
}


.tab_content_frame{
    position: absolute;
    margin-left: var(--sidebar-width);
    height: calc( 100vh - var(--titlebar-height) );
    width: calc(100% - var(--sidebar-width) );
}

.tab_content{
    height:100%; 
    width:100%; 
}

@media (prefers-color-scheme: dark) {
    .sidebar_item_selected{
        background: rgba(255, 255, 255, 0.1);
    }

    .sidebar_cat{
         color: rgba(255, 255, 255, 0.40);
    }
}




/*DROPDOWN buggle */

.dropdown-bubble {
  margin-top: 10em;
}

.dropdown-bubble:before,
.dropdown-bubble:after{
  content: ' ';
  display: block;
  border-style: solid;
  border-width: 0 7px 7px 7px;
  border-color: transparent;
  position: absolute;
  left: 193px;
}

.dropdown-bubble:before {
  top: -2px;
  border-bottom-color: rgba(255,255,255,0.5);
}

.dropdown-bubble:after {
  top: -2px;
    border-bottom-color: rgb(34, 34, 34) ;
}





</style>