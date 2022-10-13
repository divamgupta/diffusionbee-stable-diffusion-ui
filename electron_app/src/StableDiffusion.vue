<template>
    <div></div>
</template>
<script>

import { SD_STATE } from "./constants";
import { send_to_py } from "./py_vue_bridge.js"

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
            model_loading_msg : "",
            model_loading_title : "",
            loading_percentage : -1 , 
            attached_cbs : undefined,
        };
    },
    methods: {
        state_msg(msg) {
            const code = msg.substring(0, 4);
            let p = msg.substring(5).trim();

            switch (code) {
                case SD_STATE.model_loaded:
                    this.is_backend_loaded = true;
                    break;
                case SD_STATE.input_ready:
                    this.is_input_avail = true;
                    this.attached_cbs = undefined;
                    break;
                case SD_STATE.input_busy:
                    this.is_input_avail = false;
                    break;
                case SD_STATE.new_done_percent:
                    p = Number(msg.substring(5).trim());
                    let iter_time = this.last_iter_t -  Date.now();
                    if (this.attached_cbs) {
                        if (this.attached_cbs.on_progress) this.attached_cbs.on_progress(p);
                        this.attached_cbs.on_progress(p, -1*iter_time);
                    }
                    break;
                case SD_STATE.new_image_ready:
                    let impath = msg.substring(5).trim();
                    if (this.attached_cbs) {
                        if (this.attached_cbs.on_img) this.attached_cbs.on_img(impath);
                    }
                    break;
                case SD_STATE.model_new_loading_percentage:
                    p = Number(msg.substring(5).trim());
                    this.loading_percentage = p;
                    break;
                case SD_STATE.model_new_loading_message:
                    p = msg.substring(5).trim();
                    this.model_loading_msg = p;
                    break;
                case SD_STATE.model_new_loading_title:
                    p = msg.substring(5).trim();
                    this.model_loading_title = p;
                    break;
                case SD_STATE.error:
                    let error = msg.substring(5).trim();
                    if (this.attached_cbs) {
                        if (this.attached_cbs.on_err) this.attached_cbs.on_err(error);
                    }
                    break;

                default:
                    break;
            }
        },

        interupt(){
            send_to_py("t2im __stop__") 
        },

        text_to_img(prompt_params, callbacks, generated_by){
            if(!this.is_input_avail)
                return;
            this.last_iter_t = Date.now()
            this.generated_by = generated_by;
            this.attached_cbs = callbacks;
            send_to_py("t2im " + JSON.stringify(prompt_params)) 
        }
    },
}
</script>
<style>
</style>
<style scoped>
</style>