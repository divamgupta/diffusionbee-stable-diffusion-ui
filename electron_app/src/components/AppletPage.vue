<template>
    <BasicSDApplet
        :app=app 
        :input_form=input_form
        :sd_options=input_form_options
        :name="'applet_' + applet_id "
        :required_assets="[]"
        ref="basic_sd_applet"
    >
        

        <template v-slot:input_buttons>
            
            <div class="l_button button_medium"   style="float:right" v-if="is_mounted && !(stable_diffusion.is_input_avail) && stable_diffusion.generated_by==applet_id " > 
                Running 
                <MoonLoader   class="moonloader1" color="#3E7BFA" size="25px" style="zoom:0.6; float:right; margin-left: 15px;"></MoonLoader>
            </div>
            <div v-else @click="start" class="l_button button_colored button_medium" style="float:right">Start</div>


            <span v-if="is_stop_avail && is_mounted &&  stable_diffusion.generated_by==applet_id && !stable_diffusion.is_input_avail "   >
                <div v-if="is_stopping" class="l_button button_medium button_colored" style="float:right; float:right ;  " >Stopping ...</div>
                <div v-else class="l_button button_medium button_colored" style="float:right; float:right ;  " @click="stop_all">Stop</div>
            </span>



            

        </template>

        <template v-slot:output_workpace>

            <div v-if="backend_error" style="padding: 20px"> 
                 <p style="color:red"> Error : {{ backend_error  }} </p>
            </div>
            
            <div v-if="!backend_error" style="padding: 20px"> 
                <Form ref="output_form"  :form_data="output_form"  :form_values="out_vals" :form_save_key="'out'+applet_id"  ></Form>
                
            </div>
             
        </template>

    </BasicSDApplet>
</template>
<script>

import BasicSDApplet from "../components/BasicSDApplet.vue"
import Form from "../components_bare/Form.vue"
import MoonLoader from 'vue-spinner/src/MoonLoader.vue'

export default {
    name: 'AppletPage',
    props: {
        app:Object,
        input_form : Array,
        applet_id: String, 
        output_form:Array,
        is_stop_avail:Boolean

    },
    components: { BasicSDApplet, Form , MoonLoader},
    mounted() {
        this.stable_diffusion = this.app.stable_diffusion
        this.is_mounted = true
    },
    data() {
        return {
            is_mounted: false,
            input_form_options: {}, 
            out_vals : {},
            backend_error : "",
            is_stopping: true
        };
    },
    methods: {
        start(){
            if(!this.is_mounted)
                return;
            
            if(!(this.stable_diffusion.is_input_avail)){
                this.app.show_toast("Currently some images are being generated. Please wait for them to finish or stop them.")
                return;
            }

            if(!this.$refs.basic_sd_applet.check_input_form_n_show_error()){
                return
            }

            this.is_stopping = false

            let options =  this.$refs.basic_sd_applet.get_sd_form_outputs()

            let that = this

            let callbacks = {
                on_img(){
                },
                on_progress(){                    
                },
                on_err(err){
                    that.app.show_toast("Error : " + err)
                    that.backend_error = err;
                },
            }

            this.backend_error = ""

            this.stable_diffusion.run_applet( this.applet_id ,options , callbacks );
                
        } , 
        stop_all(){
            if(!this.is_mounted)
                return;
            this.is_stopping = true;
            this.stable_diffusion.interupt();
            
        }
    },
}
</script>
<style>
</style>
<style scoped>


</style>