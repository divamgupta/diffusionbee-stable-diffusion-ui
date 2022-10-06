@import '../assets/css/theme.css';

<template>
     <div  class="animatable_content_box ">
        <div class="left_half">
            <!-- <p>Input Image:</p>
            <img class="gal_img" style="width: 90%;" src="https://colormadehappy.com/wp-content/uploads/2022/02/How-to-draw-a-cute-dog-6.jpg"/> 
         -->

            <div @click="open_input_image" class="image_area" :class="{ pointer_cursor  : is_sd_active }" style="height: calc(100% - 200px);  border-radius: 16px; padding:5px;">
                <img v-if="inp_img" :src="'file://'+inp_img" style="width:100% ; height:100%; object-fit: contain;">
               
                <center v-else>
                    <p style="margin-top: calc( 50vh - 180px); opacity: 70%;" >Click to add input image</p>
                </center>
            </div>
            <br> 
            <textarea 
                    v-model="prompt" 
                    placeholder="Enter your prompt here" 
                    style="border-radius: 12px 12px 12px 12px; width: calc(100%); resize: none; " 
                    class="form-control"  
                    v-bind:class="{ 'disabled' : !stable_diffusion.is_input_avail}"
                    rows="3"></textarea>

            <div v-if="stable_diffusion.is_input_avail" class="content_toolbox" style="margin-top:10px; margin-bottom:-10px;">
                <div class="l_button button_medium button_colored" style="float:right ; " @click="generate_img2img" >Generate</div>

                <div style="float:right; margin-top: -5px;" >
                        <b-dropdown id="dropdown-form" variant="link" ref="dropdown" toggle-class="text-decoration-none" no-caret >
                        
                            <template #button-content>
                                <div class="l_button"  style="" >Options</div>
                            </template>

                            <b-dropdown-form style="min-width: 240px ; ">

                                <b-form-group inline  label="" style="margin-bottom: 6px;" >
                                    <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Input Strength: </label>
                                    <b-form-select
                                    v-model="inp_img_strength"
                                    :options="[ 0.1 , 0.2 , 0.3 , 0.4 , 0.5 , 0.6 , 0.7 , 0.8 , 0.9 ]"
                                    required
                                    ></b-form-select>
                                </b-form-group>
                                
                                <b-form-group inline  label="" style="margin-bottom: 6px;" >
                                    <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Num Images: </label>
                                    <b-form-select
                                    v-model="num_imgs"
                                    :options="[1,2,3,4,5,6,7,8,9,10,11,12,13,14]"
                                    required
                                    ></b-form-select>
                                </b-form-group>

                                <b-form-group inline label=""  style="margin-bottom: 6px;">
                                <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Steps: </label>
                                <b-form-select
                                    v-model="dif_steps"
                                    :options="[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49 , 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75]"
                                    required
                                ></b-form-select>
                                </b-form-group>

                                <b-form-group inline  label="" style="margin-bottom: 6px;" >
                                <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Seed: </label>
                    
                                <b-form-input onkeypress="return event.keyCode != 13;"  size="sm" class="mr-sm-2"  v-model="seed" style="max-width: 40px; float: right; margin-right: 30px;" ></b-form-input>

                                </b-form-group>

                            </b-dropdown-form>
                        </b-dropdown>
                    </div>


            </div>
            <div v-else-if="stable_diffusion.generated_by=='img2img'"  class="content_toolbox" style="margin-top:10px; margin-bottom:-10px;">
                <div v-if="is_stopping" class="l_button button_medium button_colored" style="float:right" @click="stop_generation">Stopping ...</div>
                <div v-else class="l_button button_medium button_colored" style="float:right" @click="stop_generation">Stop</div>
            </div>
        
        </div>

        <div  class="right_half">

        
            <div v-if="generated_images.length > 0 " >

                <br> <br>
                <div   v-for="img in generated_images" :key="img" >
                    <center>
                        
                        <ImageItem :app_state="app_state" :path="img" :style_obj="{ 'width': '75%' }"></ImageItem>

                    </center>
                    <br>
                </div>
                
            </div>

            <div v-if="backend_error" style="color:red ; margin-top:50px;">
                <div class="center loader_box">
                    <p>Error: {{backend_error}} </p>
                </div>
            </div>

            <div v-if="!stable_diffusion.is_input_avail && stable_diffusion.generated_by=='img2img'">
                <LoaderModal :loading_percentage="done_percentage" loading_title="Generating"></LoaderModal>
            </div>
            

        </div>


     </div>
</template>
<script>
import ImageItem from '../components/ImageItem.vue'

import LoaderModal from '../components_bare/LoaderModal.vue'
import Vue from 'vue'

export default {
    name: 'Img2Img',
    props: {
        app_state : Object   , 
        stable_diffusion : Object,
    },
    components: {LoaderModal, ImageItem},
    mounted() {

    },
    computed:{
        is_sd_active(){
            return this.stable_diffusion.is_input_avail;
        }
    },
    data() {
        return {
            prompt : '',
            inp_img : '',
            num_imgs:1,
            dif_steps: 25,
            batch_size:1 ,
            seed: '',
            generated_images : [],
            backend_error : "",
            done_percentage : -1,
            is_stopping : false,
            inp_img_strength : 0.3 , 
            img_h : 512 , 
            img_w : 512 , 
        };
    },
    methods: {

        generate_img2img(){

            let seed = 0;
            if(this.seed)
                seed = Number(this.seed);
            else
                seed = Math.floor(Math.random() * 100000);

            let params = {
                prompt : this.prompt , 
                W : -1 , 
                H : -1, 
                seed :seed,
                scale : this.guidence_scale , 
                ddim_steps : this.dif_steps, 
                num_imgs : this.num_imgs , 
                batch_size : this.batch_size , 
                img_strength : this.inp_img_strength,
                input_image : this.inp_img,
            }
            let that = this;

            if(this.prompt.trim() == "")
                return;

            if(!this.inp_img)
                return;

            this.backend_error = "";
            Vue.set(this,'generated_images' ,[]);
            this.done_percentage = -1;

            let history_key = Math.random();

            let callbacks = {
                on_img(img_path){
                    that.generated_images.push(img_path);

                    if(!(that.app_state.history[history_key]))
                        Vue.set(that.app_state.history, history_key , {
                            "prompt":that.prompt , "seed": seed, "key":history_key , "imgs" : [] , "inp_img": that.inp_img ,
                            "dif_steps" : that.dif_steps , "inp_img_strength" : that.inp_img_strength,
                        });
                    
                    that.app_state.history[history_key].imgs.push(img_path)

                    console.log(that.app_state.history)

                },
                on_progress(p){
                    that.done_percentage = p;
                },
                on_err(err){
                    that.backend_error = err;
                },
            }

            this.is_stopping = false;


           if(this.stable_diffusion)
                this.stable_diffusion.text_to_img(params, callbacks, 'img2img');
        } , 

        open_input_image(){
            if( !this.stable_diffusion.is_input_avail)
                return;
            let img_path = window.ipcRenderer.sendSync('file_dialog',  'img_file' );
            if(img_path && img_path != 'NULL')
                this.inp_img = img_path;
        },

        stop_generation(){
            this.is_stopping = true;
            this.stable_diffusion.interupt();
        },
    },
}
</script>
<style>
    .left_half{
        position: absolute;
        top :2px;
        bottom: 3px;
        left : 2px ;
        padding: 20px;
        width: calc(100vw / 2 - 10px);
        border-right: 1px solid ;
        border-color: rgba(0,0,0,0.1);
    }

    @media (prefers-color-scheme: dark) {
        .left_half{
            border-color: #606060;
        }
    }

    .right_half{
        position: absolute;
        top :2px;
        bottom: 3px;
        right : 3px ;
        padding: 20px;
        width: calc(100vw / 2 - 10px);
        overflow-y: auto;
    }

    .pointer_cursor{
        cursor: pointer;
    }
</style>
<style scoped>
</style>