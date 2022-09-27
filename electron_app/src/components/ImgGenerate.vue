<template>


    <div  class="animatable_content_box ">


        <div v-if="stable_diffusion.is_backend_loaded">
            <div class="textbox_section" >
                <textarea 
                    v-model="prompt" 
                    placeholder="Enter your prompt here" 
                    style="border-radius: 12px 12px 12px 12px; border-color: rgba(0, 0, 0, 0.1);  width: calc(100%); resize: none; " 
                    class="form-control"  
                    v-bind:class="{ 'disabled' : !stable_diffusion.is_input_avail}"
                    rows="3"></textarea>

                <div v-if="stable_diffusion.is_input_avail" class="content_toolbox" style="margin-top:10px; margin-bottom:-10px;">
                    
                    <div class="l_button button_medium button_colored" style="float:right ; " @click="generate_from_prompt">Generate</div>

                    <!-- <div style="float:right;"  >
                        <div class="l_button" @click="is_adv_options = !is_adv_options">Advanced options</div>
                    </div> -->

                    <div style="float:right; margin-top: -5px;" >
                        <b-dropdown id="dropdown-form" variant="link" ref="dropdown" toggle-class="text-decoration-none" no-caret >
                        
                            <template #button-content>
                                <div class="l_button"  style="" >Advanced options</div>
                            </template>

                            <b-dropdown-form style="min-width: 240px ; ">
                                
                                <b-form-group inline  label="" style="margin-bottom: 6px;" >
                                    <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Num Images: </label>
                                    <b-form-select
                                    style="border-color:rgba(0,0,0,0.1)"
                                    v-model="num_imgs"
                                    :options="[1,2,3,4,5,6,7,8,9,10,11,12,13,14]"
                                    required
                                    ></b-form-select>
                                </b-form-group>


                                <b-form-group inline label=""  style="margin-bottom: 6px;">
                                    <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Image Height: </label>
                                    <b-form-select
                                    style="border-color:rgba(0,0,0,0.1)"
                                    v-model="img_h"
                                    :options="[128*2 , 128*3 , 128*4 , 128*5 , 128*6, ]"
                                    required
                                    ></b-form-select>
                                </b-form-group>

                                <b-form-group inline label=""  style="margin-bottom: 6px;">
                                    <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Image Width: </label>
                                    <b-form-select
                                    style="border-color:rgba(0,0,0,0.1)"
                                    v-model="img_w"
                                    :options="[128*2 , 128*3 , 128*4 , 128*5 , 128*6, ]"
                                    required
                                    ></b-form-select>
                                </b-form-group>

                                <b-form-group inline label=""  style="margin-bottom: 6px;">
                                <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Steps: </label>
                                <b-form-select
                                    style="border-color:rgba(0,0,0,0.1)"
                                    v-model="dif_steps"
                                    :options="[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49 , 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75]"
                                    required
                                ></b-form-select>
                                </b-form-group>

                                <b-form-group inline label=""  style="margin-bottom: 6px;">
                                <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Batch size: </label>
                                <b-form-select
                                    style="border-color:rgba(0,0,0,0.1)"
                                    v-model="batch_size"
                                    :options="[1, 2, 3, 4, 5, 6, 7, 8]"
                                    required
                                ></b-form-select>
                                </b-form-group>

                                <b-form-group inline  label="" style="margin-bottom: 6px;" >
                                <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Guidance Scale: </label>
                                <b-form-select
                                    style="border-color:rgba(0,0,0,0.1)"
                                    v-model="guidence_scale"
                                    :options="[1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 7.5 , 8.0]"
                                    required
                                ></b-form-select>
                                </b-form-group>

                                


                                <b-form-group inline  label="" style="margin-bottom: 6px;" >
                                <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Seed: </label>
                    
                                <b-form-input onkeypress="return event.keyCode != 13;"  size="sm" class="mr-sm-2"  v-model="seed" style="border-color:rgba(0,0,0,0.1) ; max-width: 40px; float: right; margin-right: 30px;" ></b-form-input>

                                </b-form-group>



                            </b-dropdown-form>
                        </b-dropdown>
                    </div>


                    <div style="float:right; margin-top: -5px; " >
                        <b-dropdown id="dropdown-form" variant="link" ref="dropdown" toggle-class="text-decoration-none" no-caret >
                        
                            <template #button-content>
                                <div class="l_button"  style="margin-right: -20px;" >Styles</div>
                            </template>

                            <b-dropdown-form style="width: 540px ; ">

                                <div style="max-height: calc(100vh - 300px); overflow-y: scroll;">
                                    <div v-for="modifier in modifiers" :key="modifier[0]">
                                        <p>{{modifier[0]}}</p>
                                        <div v-for="tag in modifier[1]" @click="add_style(tag)" :key="tag" class="l_button button_small button_colored" style="float:left; margin-bottom: 7px;">{{tag}}</div>

                                        <div style="clear: both; display: table; margin-bottom: 3px;"> </div>
                                        <hr>
                                    </div>

                                    <p>Source : cmdr2</p>
                                </div>

                                
  
                            </b-dropdown-form>
                        </b-dropdown>
                    </div>

                    <div class="l_button button_medium" style="float:right ;margin-right: -10px; margin-top: -1px;" @click="open_arthub">Prompt Ideas</div>


                    
                </div>
                <div v-else  class="content_toolbox" style="margin-top:10px; margin-bottom:-10px;">
                    <div v-if="is_stopping" class="l_button button_medium button_colored" style="float:right" @click="stop_generation">Stopping ...</div>
                    <div v-else class="l_button button_medium button_colored" style="float:right" @click="stop_generation">Stop</div>
                </div>
            </div>


            <div v-if="generated_images.length == 1" >
                <center>
                    <img @click="open_image_popup( generated_images[0])"  class="gal_img" v-if="generated_images[0]" :src="'file://' + generated_images[0]" style=" height: calc(100vh - 380px ); margin-top: 60px;">
                    <br>
                    <div @click="save_image(generated_images[0], prompt, seed)" class="l_button">Save Image</div>
                </center>
            </div>
            
            <div>
                <br> 
                <b-row v-if="generated_images.length > 1"  class="justify-content-md-center" >

                    <b-col  v-for="img in generated_images" :key="img" style="margin-top:80px"  md="6" lg="4" xl="3"  >
                        <center>
                            <img @click="open_image_popup( img )"  class="gal_img" v-if="img" :src="'file://' + img" style="max-width:85%">
                            <br>
                            <div @click="save_image(img, prompt, seed)" class="l_button">Save Image</div>
                        </center>
                    </b-col>
                        

                
                </b-row>
                <br> 
            </div>
            




            <div v-if="backend_error" style="color:red ; margin-top:50px;">
                <div class="center loader_box">
                     {{backend_error}}
                </div>
            </div>
        </div>

        <div v-if="!stable_diffusion.is_input_avail">
            <LoaderModal :loading_percentage="done_percentage" loading_title="Generating"></LoaderModal>
        </div>
    
    <div class="bottom_float">
        <p>Please close other applications for best speed.</p>
    </div>

    </div>



</template>
<script>

import LoaderModal from '../components_bare/LoaderModal.vue'
import Vue from 'vue'
import {open_popup} from "../utils"

export default {
    name: 'ImgGenerate',
    props: {
        app_state : Object   , 
        stable_diffusion : Object,
    },
    components: {LoaderModal},
    mounted() {
       
    },
    data() {
        return {
            img_w : 512, 
            img_h : 512 , 
            dif_steps : 25,
            guidence_scale : 7.5 , 
            is_adv_options : false , 
            seed : ""  , 
            prompt : "",
            num_imgs : 1,
            batch_size : 1 , 
            generated_images : [],
            backend_error : "",
            done_percentage : -1,
            is_stopping : false,
            modifiers : require("../modifiers.json"),
        };
        
    },
    methods: {
        generate_from_prompt(){
            let params = {
                prompt : this.prompt , 
                W : Number(this.img_w) , 
                H : Number(this.img_h) , 
                seed : Number(this.seed),
                scale : this.guidence_scale , 
                ddim_steps : this.dif_steps, 
                num_imgs : this.num_imgs , 
                batch_size : this.batch_size , 

            }
            let that = this;

            if(this.prompt.trim() == "")
                return;

            this.backend_error = "";
            Vue.set(this,'generated_images' ,[]);
            this.done_percentage = -1;

            let history_key = Math.random();

            let callbacks = {
                on_img(img_path){
                    that.generated_images.push(img_path);

                    if(!(that.app_state.history[history_key]))
                        Vue.set(that.app_state.history, history_key , {"prompt":that.prompt , "seed": that.seed, "key":history_key , "imgs" : []});
                    
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
                this.stable_diffusion.text_to_img(params, callbacks);
        } , 

        open_image_popup(img){
            open_popup("file://"+img , undefined);
        },

        open_arthub(){
            window.ipcRenderer.sendSync('open_url', "https://arthub.ai");
        },

        stop_generation(){
            this.is_stopping = true;
            this.stable_diffusion.interupt();
        },

        add_style(tag){
            this.prompt += ", " + tag;
        },

        save_image(generated_image, prompt, seed){
            if(!generated_image)
                return;

            generated_image = generated_image.split("?")[0];
            seed = seed ? seed : '0'
            let out_path = window.ipcRenderer.sendSync('save_dialog', prompt, seed);
            if(!out_path)
                return

            let org_path = generated_image.replaceAll("file://" , "")

            window.ipcRenderer.sendSync('save_file', org_path+"||" +out_path);

        }
    },
}
</script>
<style>

   .center {
      margin: 0;
      position: absolute;
      top: 50%;
      left: 50%;
      -ms-transform: translate(-50%, -50%);
      transform: translate(-50%, -50%);
    }

    .disabled{
        pointer-events:none;
        opacity: 0.5;
    }

    .loader_box{
       padding: 20px;
        background-color: rgba(255,255,255,0.9);
        /*height: calc(160px);*/
        border-radius: 12px 12px 12px 12px;
    }

    .bottom_float{
        position: fixed ;
        bottom: 1px;
    }

    .ad_form_box{
        float:left; 
        background-color: rgba(0, 0, 0, 0.1); 
        padding:10px ; 
        margin-right: 10px;
         border-radius: 3px 3px 3px 3px;
    }

    .gal_img{
        border-radius: 12px 12px 12px 12px;
        background-color: white;
        border-style: solid;
        border-width: 1px;
        border-color: rgba(0, 0, 0, 0.1);
        box-shadow: 0px 0px 1.76351px rgba(40, 41, 61, 0.04), 0px 3.52703px 7.05405px rgba(96, 97, 112, 0.16);

    }

</style>
