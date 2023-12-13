<template>
    <div    class="gal_item">
        <div class="gal_item_inner" style="height: 100%; width: 100%;   ">


            <div v-if="image_url == 'ERROR'"  style="width:100% ; height:100%;   border-style: solid ; border-color: var(--border-color-invert); border-width: 1px;  padding: 20px; "  >
                <p> Error : {{description}} </p>
            </div>

            <div style="height: 100%; width: 100%;   " v-else>

                <img class="aux_img" v-if="aux_img_url" :src="'file://' + aux_img_url"  style="position:absolute; opacity:0.8; top:0 ; left:0; width:30% ; height:30%; object-fit: cover;   ">
                
                <div v-if="description && image_url" @click="on_image_click(self)" class="gall_top_right_btn_container " style="position:absolute; bottom:5px ; left:5px ; right:0px; padding:20px; background: linear-gradient(to top, rgba(0,0,0,1), rgba(0,0,0,0)); color:white ; font-size: 12px;margin-right: 5px ; padding-top:20px">
                    {{description}}
                </div>

                 <div v-if="image_url" class="cdiv gall_top_right_btn_container" style=" position:absolute ; margin-top:7px ; margin-left:7px "  >
                    <b-dropdown left variant="link" size="sm" toggle-class="text-decoration-none" no-caret>
                        <template #button-content>
                            <div   class=" l_button button_colored" style="background-color: rgba(0,0,0,0.6);">
                                Actions 
                                <!-- <font-awesome-icon icon="bars" /> -->
                            </div>
                        </template>
                        <b-dropdown-item-button v-for="menu_item in menu_items" :key="menu_item.id" @click="on_menu_item_click(menu_item.id , self )">{{menu_item.text}}</b-dropdown-item-button>
                    </b-dropdown>
                 </div>


                 <div style="position:absolute ; top: 50% ; left: 50% ;  transform: translate(-50%, -50%);"  v-if="(!image_url) && (done_percentage != undefined)" >
                     <CircleProgress :done_percentage="done_percentage"> </CircleProgress>
                 </div>


                

                
                <img @click="on_image_click(self)" v-if="image_url"   style="  width:100% ; height:100%; object-fit: cover;  object-position:0px 0px; " :src=" 'file://' + image_url">
                <img  v-bind:class="{ 'animate-flicker': (done_percentage == undefined) }" class="animate-flicker"   v-else :width="img_w" :height="img_h"  style="width:100% ; height:100%;   object-position:0px 0px;  border-style: solid ; border-color: var(--border-color-invert); border-width: 1px;   " src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==">


                


            </div>


        </div>
        
    </div>

</template>
<script>

import CircleProgress from "./CircleProgress.vue"


export default {
    name: 'EmptyComponent',
    props: {
        image_url : String,
        aux_img_url: String,
        img_w:Number, 
        img_h:Number,
        description: String, 
        menu_items : Array,
        params: Object,
        done_percentage: Number,
        on_menu_item_click : Function, 
        on_image_click: Function,
    },
    components: {CircleProgress},
    mounted() {

    },
    data() {
        return {
            self : this,
        };
    },
    methods: {

    },
}
</script>
<style>

.cdiv > div > .dropdown-menu{
    font-size: 13px !important;
}

</style>

<style scoped>


@keyframes flickerAnimation {
  0%   { background-color:var(--border-color-invert-extralight); }
  50%  { background-color: rgba(0, 0, 0, 0.0); }
  100% { background-color:var(--border-color-invert-extralight); }
}


.animate-flicker {
   -webkit-animation: flickerAnimation 1s infinite;
   -moz-animation: flickerAnimation 1s infinite;
   -o-animation: flickerAnimation 1s infinite;
    animation: flickerAnimation 1s infinite;

}


.gal_item{
    position: relative;
    padding:5px;
}

.gall_top_right_btn_container{
    display: none;
}

.gal_item_inner:hover > div > .gall_top_right_btn_container{
    display: block;
    /*opacity: 0.1;*/
}


.aux_img{
    display: block;
}

.gal_item_inner:hover > div > .aux_img{
    display: none;
    /*opacity: 0.1;*/
}


</style>