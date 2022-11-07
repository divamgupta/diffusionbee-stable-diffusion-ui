<template>
    <div></div>
</template>
<script>

import { send_to_py } from "./py_vue_bridge.js"
import {get_tokens} from './clip_tokeniser/clip_encoder.js'
const nsfwjs = require('nsfwjs');

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
            is_backend_loaded : false,
            is_input_avail : false,
            nsfw_filter: true,
            model_loading_msg : "",
            model_loading_title : "",
            loading_percentage : -1 , 
            generation_state_msg : "",
            attached_cbs : undefined,
            model_version : "",
        };
    },
    methods: {
        state_msg(msg){
            let msg_code = msg.substring(0, 4);
            if(msg_code == "mdld"){
                this.is_backend_loaded = true;
            }
            if(msg_code == "inrd"){
                this.is_input_avail = true;
                this.attached_cbs = undefined;
            }
            if(msg_code == "inwk"){
                this.is_input_avail = false;
            }
            if(msg_code == "nwim"){
                let impath = msg.substring(5).trim()

                const img = new Image();
                img.src = "file://" + impath;

                img.attached_cbs = this.attached_cbs;


                img.onload = () => {
                    if (this.nsfw_filter == false) {
                        if (img.attached_cbs) {
                            if (img.attached_cbs.on_img)
                                img.attached_cbs.on_img(impath);
                        }
                    }
                    nsfwjs.load()
                        .then(model => model.classify(img))
                        .then(predictions => {
                            switch (predictions[0].className) {
                                case 'Hentai':
                                case 'Porn':
                                case 'Sexy':
                                    impath = "nsfw";
                            }
                            if (img.attached_cbs) {
                                if (img.attached_cbs.on_img)
                                    img.attached_cbs.on_img(impath);
                            }
                        });
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
                this.model_loading_title = p;
            }


            if(msg_code == "errr"){
                let error = msg.substring(5).trim()
                if(this.attached_cbs){
                    if(this.attached_cbs.on_err)
                        this.attached_cbs.on_err(error);
                }

            }

            if(msg_code == "dnpr"){
                let p = Number(msg.substring(5).trim());
                let iter_time =  Date.now()  -this.last_iter_t;
                this.last_iter_t  = Date.now();
                if(this.attached_cbs){
                    if(this.attached_cbs.on_progress){
                        if(p >= 0 )
                            this.generation_state_msg = iter_time/1000 + " s/it";
                        this.attached_cbs.on_progress(p, iter_time);
                    }
                        
                }

            }


        } ,

        interupt(){
            send_to_py("t2im __stop__") 
        },

        text_to_img(prompt_params, callbacks, generated_by){
            if(!this.is_input_avail)
                return;
            let tokens = [49406].concat((get_tokens(prompt_params.prompt))).concat([49407])
            prompt_params.prompt_tokens = tokens;

            if(prompt_params.negative_prompt)
            {
                let tokens2 = [49406].concat((get_tokens(prompt_params.negative_prompt))).concat([49407])
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
            this.generation_state_msg = ""
            send_to_py("t2im " + JSON.stringify(prompt_params)) 
        }

    },
}
</script>
<style>
</style>
<style scoped>
</style>