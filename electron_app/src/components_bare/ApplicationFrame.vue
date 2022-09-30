<template>
    <div class="main_frame">
        <div class="title_bar">
            <div class="app_title" v-bind:class="{ 'fullscreen' :is_fullscreen||detect_windows_os() }">
                <span @click="$emit('on_title_click',{})"> {{title}} </span>
                <div style="float: right; margin-right: 10px; margin-top: -8.5px;" class="">
                    <b-dropdown right variant="link" size="sm" toggle-class="text-decoration-none" no-caret>
                        <template #button-content>
                            <div style="" class="tab l_button">
                                <font-awesome-icon icon="bars" />
                            </div>
                        </template>
                        <b-dropdown-item @click="$emit('menu_item_click_help',{})" href="#">Help</b-dropdown-item>
                        <b-dropdown-item @click="$emit('menu_item_click_discord',{})" href="#">Discord Group</b-dropdown-item>
                        <b-dropdown-item @click="selectTab('logs')"   href="#">Show Logs</b-dropdown-item>
                        <b-dropdown-item @click="$emit('menu_item_click_about',{})" href="#">About</b-dropdown-item>
                        <b-dropdown-item @click="$emit('menu_item_click_close',{})" href="#">Close</b-dropdown-item>
                        <!-- #TODO set these menu items via python -->
                        
                    </b-dropdown>
                </div>
                <!-- <div style="float: right; margin-right:0" class="tab l_button"><font-awesome-icon icon="bars" /></div> -->
            </div>
        </div>
        <div class="tabs_bar">
            <div @click="selectTab('txt2img')" class="tab l_button" v-bind:class="{ 'button_colored' : selected_tab === 'txt2img'}">Text To Image</div>
            <div @click="selectTab('img2img')" class="tab l_button" v-bind:class="{ 'button_colored' : selected_tab === 'img2img'}">Image To Image</div>
            <div @click="selectTab('outpainting')" class="tab l_button" v-bind:class="{ 'button_colored' : selected_tab === 'outpainting'}">Outpainting</div>

            
            <div @click="selectTab('history')" class="tab l_button" v-bind:class="{ 'button_colored' : selected_tab === 'history'}">History</div>
        </div>
        <div class="tab_content_frame">
            <div class="tab_content">
                <KeepAlive>
                     <slot v-if=" selected_tab === 'txt2img' " name="txt2img"></slot>
                </KeepAlive>

                <KeepAlive>
                     <slot v-if=" selected_tab === 'history' " name="history"></slot>
                </KeepAlive>

                <KeepAlive>
                     <slot v-if=" selected_tab === 'img2img' " name="img2img"></slot>
                </KeepAlive>
                <slot v-if=" selected_tab === 'logs' " name="logs"></slot>

                <slot v-if=" selected_tab === 'outpainting' " name="outpainting"></slot>
                
             
            </div>


        </div>
    </div>
</template>
<script>

export default {
    name: 'ApplicationFrame',
    components: {},
    props: {
        title: String,
    },

    data: function() {
        return {
            selected_tab: 'txt2img' ,
            is_fullscreen: false ,
        }
    },

    mounted() {
        window.addEventListener('resize', this.detect_fullscreen);
    },
    unmounted() {
        window.removeEventListener('resize', this.detect_fullscreen);
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

    color: rgba(0, 0, 0, 0.9);
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


.animatable_content_box {
    height: calc(100vh - 40px - 35px - 2px);
    position: fixed;
    width: 100%;
    padding: 20px;
    overflow: auto;
}


/*the slide transitions */

.slide_show-enter-active,
.slide_show-leave-enter {
    transform: translateX(0);
    transition: all .25s linear;

}

.slide_show-enter,
.slide_show-leave-to {
    transform: translateX(100%);
    transition: all .25s linear;
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

</style>
<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.title_bar {
    height: 35px;
    width: 100%;
    /*background: red;*/
    -webkit-user-select: none;
    -webkit-app-region: drag;
    border-width: 0px;
    border-bottom-width: 1px;
    border-style: solid;
}

.app_title {
    padding-left: 80px;
    padding-top: 10px;

    font-family: var(--main-font-text);
    font-style: normal;
    font-weight: 600;
    font-size: 15px;
    line-height: 16px;

    letter-spacing: -0.08px;

    color: #000000;
}

.app_title.fullscreen{
    padding-left: 22px;
}

@media (display-mode: fullscreen) {
    .app_title {
        /*works in chrome but not electron*/
        display: none;
        background-color: red;
    }
}

.tabs_bar {
    height: 40px;
    width: 100%;
    border-width: 0px;
    border-bottom-width: 1px;
    border-style: solid;

    padding-top: 8px;
    padding-left: 20px;
    padding-right: 20px;
}

.tab_content_frame {
    width: 100%;
    height: calc(100vh - 40px  - 35px - 2px);
    overflow: auto;
}

.tab_content {
    /*padding: 20px;*/

}

.vertical-center {
    margin: 0;
    position: absolute;
    top: 50%;
    -ms-transform: translateY(-50%);
    transform: translateY(-50%);
}

.tab {

    margin-right: 10px;
    cursor: pointer;

}
</style>