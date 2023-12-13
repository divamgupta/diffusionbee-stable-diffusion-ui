<template>
    <div></div>
</template>
<script>

import { send_to_py } from "./py_vue_bridge.js"
import {get_tokens} from './clip_tokeniser/clip_encoder.js'
import {compute_time_remaining} from "./utils.js"
const moment = require('moment')

let notification_sound = new Audio(require('@/assets/notification.mp3'))

function remove_non_ascii(str) {
  
  if ((str===null) || (str===''))
       return false;
 else
   str = str.toString();
  
  return str.replace(/[^\x20-\x7E]/g, '');
}

export default {
    name: 'StableDiffusion',
    props: {},
    components: {},
    mounted() {

    },
    data() {
        return {
            is_stopping: false,
            is_backend_loaded : false,
            is_model_downloading: false, 
            is_input_avail : false,
            model_loading_msg : "",
            model_loading_title : "",
            loading_percentage : -1 , 
            generation_state_msg : "",
            remaining_times: "",
            attached_cbs : undefined,
            model_version : "",
            nb_its: 0,
            iter_times: [],
            generation_loop: undefined
        };
    },
    methods: {
        state_msg(msg){
            let msg_code = msg.substring(0, 4);
            if(msg_code == "mdld"){
                this.is_backend_loaded = true;
            }
            if(msg_code == "mldn"){
                this.is_model_downloading = false;
            }
            if(msg_code == "inrd"){
                console.log("cps unset inrd ")
                this.is_stopping = false
                this.is_input_avail = true; // note : is_input_avail can be watched so set this at last pls
            }
            if(msg_code == "inwk"){
                this.is_input_avail = false;
            }

            if(msg_code == "nwim"){
                if (this.$parent.app_state.app_data.settings.notification_sound == true) {
                    notification_sound.play();
                }
                let img = msg.substring(5).trim()
                img = JSON.parse(img)
                if(this.attached_cbs){
                    if(this.attached_cbs.on_img)
                        this.attached_cbs.on_img(img);
                } else {
                    console.log("got new img but cbs none")
                }
            }

            if(msg_code == "mdvr"){
                this.model_version = msg.substring(5).trim()
            }

            if(msg_code == "mlpr"){
                let p = Number(msg.substring(5).trim());
                this.loading_percentage = p;
            }
            if(msg_code == "mlms"){
                let p = (msg.substring(5).trim());
                this.model_loading_msg = p;
            }
            if(msg_code == "gnms"){
                let p = (msg.substring(5).trim());
                this.generation_state_msg = p;
            }

            if(msg_code == "mltl"){
                let p = (msg.substring(5).trim());

                if( p.includes("Downloading") ){
                    this.is_model_downloading = true;
                }

                this.model_loading_title = p;
            }


            if(msg_code == "errr"){
                this.is_model_downloading = false;
                let error = msg.substring(5).trim()
                if(this.attached_cbs){
                    if(this.attached_cbs.on_err)
                        this.attached_cbs.on_err(error);
                }

            }

            if(msg_code == "dnpr"){
                this.is_model_downloading = false;
                let p = Number(msg.substring(5).trim());
                let iter_time =  Date.now()  -this.last_iter_t;
                this.last_iter_t  = Date.now();
                if(this.attached_cbs){
                    if(this.attached_cbs.on_progress){
                        if(p >= 0 ){
                            this.generation_state_msg = iter_time/1000 + " s/it";
                            this.iter_times.push(iter_time);
                            let median = this.iter_times.sort((a, b) => a - b)[Math.floor(this.iter_times.length / 2)];
                            let time_remaining = moment.duration(median*((100-p)*this.nb_its/100));
                              
                            this.remaining_times = compute_time_remaining(time_remaining);
                            clearInterval(this.generation_loop);
                            this.generation_loop = setInterval(() => {
                                if(this.attached_cbs == undefined){
                                    return clearInterval(this.generation_loop);
                                }
                                time_remaining.subtract(1, 'seconds');
                                this.remaining_times = compute_time_remaining(time_remaining);
                            }, 1000);
    
                        }
                        this.attached_cbs.on_progress(p, iter_time);
                    }
                        
                } else {
                    console.log("got new msg but cbs none")
                }

            }


        } ,

        interupt(){
            send_to_py("t2im __stop__")
            console.log("cps unset st ")
            this.is_stopping = true
            this.attached_cbs = undefined;
        },

        is_ready(){
            if(this.is_model_downloading)
                return false 
            return this.is_backend_loaded
        },

        run_applet(applet_name , params , callbacks ){


            if(!this.is_input_avail)
                return;
            
            this.is_stopping = false

            this.generated_by = applet_name;
            this.attached_cbs = callbacks;

            this.generation_state_msg = "Running " + applet_name

            send_to_py("rapp " + applet_name + " " + JSON.stringify(params)) 
            
        },

        text_to_img(prompt_params, callbacks, generated_by){
            if(!this.is_input_avail)
                return;
            this.is_stopping = false
            let tokens = [49406].concat((get_tokens(prompt_params.prompt))).concat([49407])
            tokens.filter(n => n != null && n != undefined)
            prompt_params.prompt_tokens = tokens;

            if(prompt_params.negative_prompt)
            {
                let tokens2 = [49406].concat((get_tokens(prompt_params.negative_prompt))).concat([49407])
                tokens2.filter(n => n != null && n != undefined)
                prompt_params.negative_prompt_tokens = tokens2
            }

            prompt_params.seed = Number(prompt_params.seed) || 0 

            if(prompt_params.prompt){
                prompt_params.prompt = remove_non_ascii(prompt_params.prompt)
            }

            if(prompt_params.negative_prompt){
                prompt_params.negative_prompt = remove_non_ascii(prompt_params.negative_prompt)
            }                

            this.last_iter_t = Date.now()
            this.generated_by = generated_by;
            this.attached_cbs = callbacks;
            console.log("cps set ")
            this.generation_state_msg = ""
            this.remaining_times = ""
            this.iter_times = []
            this.nb_its = prompt_params.ddim_steps||25
            send_to_py("t2im " + JSON.stringify(prompt_params)) 
        }

    },
}
</script>
<style>
</style>
<style scoped>
</style>