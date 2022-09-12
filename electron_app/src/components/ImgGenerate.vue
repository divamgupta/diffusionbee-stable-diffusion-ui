<template>


    <div  class="animatable_content_box ">

        

        <div v-if="app_state.is_model_loaded">

            <div class="textbox_section" v-bind:class="{ 'disabled' : !app_state.is_textbox_avail}">
                    <textarea v-model="app_state.prompt" placeholder="Enter your prompt here" style="border-radius: 12px 12px 12px 12px; border-color: rgba(0, 0, 0, 0.1);  width: calc(100%); resize: none; " class="form-control"  rows="4"></textarea>

                    <div class="content_toolbox" style="margin-top:10px; margin-bottom:-10px;">
                        
                        <div class="l_button button_medium button_colored" style="float:right" @click="generete_from_prompt">Generate</div>

                        <div style="float:right;"  >
                            <div class="l_button" @click="is_adv_options = !is_adv_options">Advanced options</div>
                        </div>

                        <div  v-if="is_adv_options">

                            <div class="ad_form_box" >

                                <b-form-group inline label="Image Height:" >
                                    <b-form-select
                                      v-model="img_h"
                                      :options="[128*2 , 128*3 , 128*4 , 128*5 , 128*6, ]"
                                      required
                                    ></b-form-select>
                                  </b-form-group>

                            </div>


                            <div class="ad_form_box" >

                                <b-form-group label="Image Width:" >
                                    <b-form-select
                                      v-model="img_w"
                                      :options="[128*2 , 128*3 , 128*4 , 128*5 , 128*6, ]"
                                      required
                                    ></b-form-select>
                                  </b-form-group>

                            </div>

                            <div class="ad_form_box" >

                                <b-form-group label="Steps:" >
                                    <b-form-select
                                      v-model="dif_steps"
                                      :options="[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49 , 50]"
                                      required
                                    ></b-form-select>
                                  </b-form-group>

                            </div>


                            <div class="ad_form_box" >

                                <b-form-group label="Guidance Scale:" >
                                    <b-form-select
                                      v-model="guidance_scale"
                                      :options="[1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 7.5 , 8.0]"
                                      required
                                    ></b-form-select>
                                  </b-form-group>

                            </div>
                            
                        </div>

                        
                    </div>
                </div>


            
            <div v-if="app_state.generated_image" style="margin-top:80px" >
                <center>
                    <img v-if="app_state.generated_image" :src="'file://' + app_state.generated_image">
                    <br>
                    <div @click="save_image" class="l_button">Save Image</div>
                </center>
                <br><br><br>
            </div>
            


            <div v-if="app_state.backedn_error" style="color:red ; margin-top:50px;">
                <div class="center loader_box">
                     {{app_state.backedn_error}}
                </div>
            </div>
        </div>

        <div>
            
             <center>
                <div class="center loader_box" v-if="app_state.loading_msg">
                    <h2 style=" margin-bottom:-5px   "  class="head ">{{app_state.loading_msg}}</h2>
                     <span v-if="app_state.loading_percentage <  0 "  style="zoom:0.35;   margin-left: 25px;   ">
                            <MoonLoader color="#000000" size="50px"></MoonLoader>
                    </span>
                    
                   <div style="margin-bottom:30px"></div>
                    <b-progress v-if="app_state.loading_percentage >= 0 "  :value="app_state.loading_percentage" style="height: 10px;"></b-progress>

                    <div style="margin-bottom:10px"></div>
                    <p>{{app_state.loading_desc}}</p>
                </div>

             </center>
             


        </div>
    
    <div class="bottom_float">
        <p>Stable diffusion requires a lot of RAM. 16GB recommended. Close other applications for best speed.</p>
    </div>

    </div>



</template>
<script>

import { send_to_py } from "../py_vue_bridge.js"
import MoonLoader from 'vue-spinner/src/MoonLoader.vue'


export default {
    name: 'ImgGenerate',
    props: {
        app_state : Object,
    },
    components: {MoonLoader},
    mounted() {

    },
    data() {
        return {
            img_w : 512, 
            img_h : 512 , 
            dif_steps : 25,
            guidance_scale : 7.5 , 
            is_adv_options : false , 
            seed : 42  , 

        };
    },
    methods: {
        generete_from_prompt(){
            let params = {
                prompt : this.app_state.prompt , 
                W : Number(this.img_w) , 
                H : Number(this.img_h) , 
                seed : Number(this.seed),
                scale : this.guidance_scale , 
                ddim_steps : this.dif_steps, 

            }
           send_to_py("t2im " + JSON.stringify(params)) 
        } , 

        save_image(){
            if(!this.app_state.generated_image)
                return;
            let out_path = window.ipcRenderer.sendSync('save_dialog', '');
            if(!out_path)
                return

            let org_path = this.app_state.generated_image.replaceAll("file://" , "")

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
        background-color: rgba(255,255,255,0.5);
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
</style>
