<template>


    <div  class="animatable_content_box ">
        <div v-if="app_state.is_textbox_avail">
            Width: <input v-model="img_w"><br>
            Height: <input v-model="img_h"><br>
            Prompt: <input v-model="prompt">
            <br>
            <div class="l_button button_colored" @click="generete_from_prompt">Generate</div>
        </div>


        <div v-if="app_state.loading_msg">
            {{app_state.loading_msg}}
        </div>

        <div v-if="!app_state.is_model_loaded">
            Model is loading .....  
        </div>

        <img v-if="app_state.generated_image" :src="'file://' + app_state.generated_image">


        <div v-if="app_state.backedn_error" style="color:red">
            {{app_state.backedn_error}}
        </div>
        

    </div>



</template>
<script>

import { send_to_py } from "../py_vue_bridge.js"


export default {
    name: 'ImgGenerate',
    props: {
        app_state : Object,
    },
    components: {},
    mounted() {

    },
    data() {
        return {
            prompt : "",
            img_w : 256, 
            img_h : 256 , 
        };
    },
    methods: {
        generete_from_prompt(){
            let params = {
                prompt : this.prompt , 
                W : Number(this.img_w) , 
                H : Number(this.img_h) , 
            }
           send_to_py("t2im " + JSON.stringify(params)) 
        }
    },
}
</script>
<style>
</style>
<style scoped>
</style>