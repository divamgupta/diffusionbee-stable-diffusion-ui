<template>

    <BasicSDApplet
        :app=app 
        :input_form=form_data
        :sd_options=sd_options
        :name=name
        :form_tags=form_tags
        :required_assets=required_assets
        ref="basic_sd_applet"
    >   
        
        <template v-slot:input_buttons>
            <div v-if="app.stable_diffusion_manager.is_ready" @click="generate" class="l_button button_colored button_medium" style="float:right">Generate</div>

            <div v-else-if="is_input_changed_after_last_run " @click="generate" class="l_button button_colored button_medium" style="float:right">Add to Queue</div>

            <div v-if="(!app.stable_diffusion_manager.is_ready) && !is_stopping"  @click="stop_all" class="l_button button_colored button_medium" style="float:right">Stop all</div>
            <div v-if="(!app.stable_diffusion_manager.is_ready) && is_stopping" class="l_button button_colored button_medium" style="float:right">Stopping ...</div>

        </template>

        <template v-slot:output_workpace>
            
            
            
            
            <GenerationGallery  :app="app" ref="gallery"> </GenerationGallery>
        </template>

    </BasicSDApplet>

</template>
<script>

import GenerationGallery from "./GenerationGallery.vue"
import BasicSDApplet from "../components/BasicSDApplet.vue"
import { controlnet_check_inputs , controlnet_proc_form_outputs , controlnet_required_assets } from "../utils/controlnet_frontend_utils.js"
import Vue from 'vue'

export default {
    name: 'SDImageGenerationApplet.vue',
    props: {
        app:Object, 
        form_data: Array,
        name:String,
        form_tags: Array,
        postprocess_form_options_fn: Function, // if you want to append   modify the input options valus from form 
        check_options_input_fn : Function, // if you want to add checks to the inpus 
    },
    components: { GenerationGallery , BasicSDApplet  },
    mounted() {
        this.is_mounted = true
    },
    data() {
        return {
            sd_options : {},
            is_input_changed_after_last_run : false, 
            is_mounted : false,
        };
    },
    methods: {
        generate(){

            this.is_input_changed_after_last_run = false

            if(!this.$refs.basic_sd_applet.check_input_form_n_show_error()){
                return
            }

            if(this.check_options_input_fn){
                if(!(this.check_options_input_fn()))
                    return
            }

            if(!controlnet_check_inputs(this, Vue)){
                return
            }
            
            let sd_options_object = this.get_sd_form_outputs()
            this.app.stable_diffusion_manager.add_job(sd_options_object, this.sd_options  ,  this.$refs.gallery)
        }, 

        get_sd_form_outputs(){
            let options =  this.$refs.basic_sd_applet.get_sd_form_outputs()
            if(this.postprocess_form_options_fn)
                options = this.postprocess_form_options_fn(options)

            controlnet_proc_form_outputs(this , options)

            return options
        },

        stop_all(){
            this.app.stable_diffusion_manager.stop_all() 
        },
        load_options(options){
            this.$refs.basic_sd_applet.load_options(options)
        } , 

        generate_similar_images(options){
            options = JSON.parse(JSON.stringify(options))
            if(!this.is_sd_ready){
                this.app.show_toast('Currently some images are already being generated. Please wait for them to finish.')
                return false
            }
            this.$refs.basic_sd_applet.$refs.form.reset_to_default()
            options.raw_form_options.is_adv_mode = true
            options.raw_form_options.small_mod_seed = Math.floor(Math.random()*1000) + 1 
            options.is_adv_mode = true
            options.small_mod_seed = Math.floor(Math.random()*1000)+ 1 
            options.num_imgs = 4
            options.raw_form_options.num_imgs = 4
            this.load_options(options)
            Vue.nextTick(this.generate)
            return true;
        } ,

    },  

    computed:{
        all_tags(){
            let l = this.form_tags.concat( this.sd_options.is_adv_mode ? ['advanced']:[]  )
            return l
        } , 
        required_assets(){
            // what is left to download
            let to_download = []

            controlnet_required_assets(this , to_download)
            return to_download;
        } , 
        is_sd_ready(){
            if(this.app.stable_diffusion_manager)
                return this.app.stable_diffusion_manager.is_ready
            return false
        } , 

        is_stopping(){
            if(this.app.stable_diffusion_manager   )
                return this.app.stable_diffusion_manager.is_stopping
            return false
        }
    },

    watch : {
       
        'sd_options': {
            handler: function() {
                this.is_input_changed_after_last_run = true
            },
            deep: true
        } , 

    },

}
</script>
<style>
</style>
<style scoped>

</style>