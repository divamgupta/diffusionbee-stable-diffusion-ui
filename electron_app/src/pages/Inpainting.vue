<template>

    <BasicSDApplet
        :app=app 
        :input_form=input_form_elements_processed
        :sd_options=sd_options
        name="inpainting"
        :form_tags="form_tags_computed"
        :required_assets=required_assets
        ref="basic_sd_applet"
        :model_options_types="model_options_types"
    >   
        
        <template v-slot:input_buttons>
            
            <div v-if="is_mounted && stable_diffusion.is_input_avail"  @click="generate(false)" class="l_button button_colored button_medium" style="float:right">Generate</div>
            <div v-if="is_mounted && stable_diffusion.is_input_avail"  @click="clear_canvas" class="l_button button_medium" style="float:right">Clear Stage</div>
            
            <span v-else-if="is_mounted &&  stable_diffusion.generated_by=='Inpainting'"   >
                <div v-if="is_stopping" class="l_button button_medium button_colored" style="float:right; float:right ;  " >Stopping ...</div>
                <div v-else class="l_button button_medium button_colored" style="float:right; float:right ;  " @click="stop_all">Stop</div>
            </span>

        </template>

        <template v-slot:output_workpace>
            <div>
                <br> 
                <div v-if="(redo_history.length > 0 ||  undo_history.length > 0) && is_mounted && stable_diffusion.is_input_avail" class="l_button" style="float:right " @click="do_redo" > Redo</div>
                <div v-if="(redo_history.length > 0 ||  undo_history.length > 0)  && is_mounted && stable_diffusion.is_input_avail" class="l_button" style="float:right " @click="do_undo" > Undo</div>
                <div class="l_button" style="float:right " @click="open_input_image" > Open </div>
                <div  v-if="inp_img"  class="l_button" style="float:right "  @click="save_img" > Save </div>
                <div v-if="inp_img"   class="l_button" style="float:right " @click="$refs.inp_img_canvas.clear_inpaint()" > Clear Mask</div>

                <div v-if="is_mounted && stable_diffusion.is_input_avail && inp_img"   style="float:right ; margin-right: 10px" >
                    <input v-model="stroke_size_no" style="zoom:0.8; margin-top: 7px; width:100px" type="range"
                            min="1" max="200" >                
                </div>
                <div v-if="is_mounted && stable_diffusion.is_input_avail && inp_img"   class="l_button no_hover_bg" style="float:right ; margin-right: -5px; " > Stroke Size</div>

                <br> 
            </div>

            <div class="inapint_container"  @drop.prevent="onDragFile" @dragover.prevent > 
                <ImageCanvas style="cursor: crosshair;"  v-if="inp_img"  ref="inp_img_canvas" :is_inpaint="true" :image_source="inp_img"  :is_disabled="!stable_diffusion.is_input_avail" id="inpaint"  canvas_id="inpaintcan" canvas_d_id="inpaintcand" :stroke_size_no="stroke_size_no" ></ImageCanvas>
                <div v-else @click="open_input_image" style=" "  :class="{ pointer_cursor  : is_sd_active }" >
                    <center>
                        <p style="padding-top: calc( 50vh - 115px);padding-bottom: calc( 50vh - 155px);  opacity: 70%;" >Click to add input image and draw a mask</p>
                    </center>
                </div>
            </div>

            <div v-if="is_post_generate_box_showing" class="post_generate_box"> 
                <div  class="l_button button_medium" @click="discard_generation"  > Discard </div>
                <div  class="l_button button_colored button_medium" @click="is_post_generate_box_showing = false"  > Keep </div>
                <div  class="l_button button_colored button_medium"  @click="retry_generatge" > Retry </div>
               
            </div>
            
            
            
            <div style="" v-if="is_mounted && !stable_diffusion.is_input_avail && stable_diffusion.generated_by=='Inpainting'">
                <LoaderModal  :loading_percentage="done_percentage" loading_title="Generating" :loading_desc="stable_diffusion.generation_state_msg" :remaining_times="stable_diffusion.remaining_times"></LoaderModal>
            </div>

        </template>

    </BasicSDApplet>

</template>



<script>

import LoaderModal from '../components_bare/LoaderModal.vue'
import BasicSDApplet from "../components/BasicSDApplet.vue"
import ImageCanvas from '../components_bare/ImageCanvas.vue'

import {find_in_form_recursive} from "../utils.js"
import {inpaint_assets , prep_sd_optins} from "../utils/in_out_paint_utils.js"


const Inpainting = {
    name: 'Inpainting.vue',
    props: {
        app:Object, 
    },
    components: { LoaderModal, BasicSDApplet , ImageCanvas  },
    mounted() {
        this.stable_diffusion = this.app.stable_diffusion
        this.app.functions.send_to_inpaint = this.send_to_inpaint; 
        this.is_mounted = true
    },
    data() {
        return {
            sd_options : {"num_imgs":"1"},
            backend_error : "",
            is_mounted: false,
            is_stopping : false,
            undo_history : [],
            redo_history : [],
            done_percentage: -1,
            retry_params: undefined,
            inp_img: "",
            is_post_generate_box_showing : false,
            stroke_size_no: "30",


        };
    },
    computed : {

        is_sd_active(){
            if(!this.is_mounted)
                return false;
            return this.stable_diffusion.is_input_avail;
        },

        required_assets(){
            return inpaint_assets(this , "Generative Fill");
        }, 

        form_tags_computed(){
            if(this.sd_options.outpaint_function_name =="Image To Image"){
                return ['inpainting', 'input_image_strength']
            }

            return ['inpainting']
        },

        model_options_types(){
            return ["sd_model" ,"sd_model_inpaint"]
            
        },

        input_form_elements_processed(){
            let form_or = require("../forms/sd_options_adv.json")
            form_or = JSON.parse(JSON.stringify(form_or))
            let el = find_in_form_recursive( "selected_sd_model" , form_or)

            el['options'] = [ "SD1.5_Inpainting" , "Default_SD1.5" ]

            return form_or
        }
    },
    methods: {
        generate(is_retry){

            if(!(this.stable_diffusion.is_input_avail))
                return;

            if(!this.$refs.basic_sd_applet.check_input_form_n_show_error()){
                return
            }

            this.is_stopping = false;
            this.backend_error = "";
            this.done_percentage = -1;

            this.is_post_generate_box_showing = false


            let sd_options_object = this.$refs.basic_sd_applet.get_sd_form_outputs()

            let img_url
            let img_mask_url

            if(this.retry_params == undefined)
                this.retry_params = {}

            if(is_retry){
                img_url = this.retry_params.img_url
                img_mask_url = this.retry_params.img_mask_url
                
            } else {
                let box_img_b64 = this.$refs.inp_img_canvas.get_img_b64();
                img_url = window.ipcRenderer.sendSync('save_b64_image',  box_img_b64 , true );


                let box_mask_img_b64 =  this.$refs.inp_img_canvas.get_mask_b64();
                img_mask_url = window.ipcRenderer.sendSync('save_b64_image',  box_mask_img_b64 , true );

                this.retry_params.mask_b64_image = box_mask_img_b64
                this.retry_mask_cached =  this.$refs.inp_img_canvas.get_mask_for_cache()
            }


            
            
            this.retry_params.img_url = img_url
            this.retry_params.img_mask_url = img_mask_url
            



            console.log(img_url)
            console.log(img_mask_url)

            sd_options_object.input_img = img_url

            prep_sd_optins(this , sd_options_object , "Generative Fill" , img_mask_url)

            let that = this;

            this.undo_history.push(img_url)
            this.redo_history =  []

            let callbacks = {
                on_img(img_path){
                    that.$refs.inp_img_canvas.clear_inpaint()
                    that.inp_img = img_path.generated_img_path
                    that.is_post_generate_box_showing = true

                },
                on_progress(p){
                    that.done_percentage = p;
                    
                },
                on_err(err){
                    that.app.show_toast("Error : " + err)
                    that.backend_error = err;
                },
            }
                
            this.stable_diffusion.text_to_img(sd_options_object, callbacks, 'Inpainting');
           
        }, 

        retry_generatge(){
            let that = this
            this.inp_img = this.retry_params.img_url
            setTimeout(function(){
                that.$refs.inp_img_canvas.restore_mask(that.retry_mask_cached)
            } , 150 ) 
            this.generate(true)
        },

        do_undo(){
            if(this.undo_history.length == 0)
                return;

            this.is_post_generate_box_showing = false
            let a = this.undo_history.pop()

            if(a){
                this.redo_history.push(this.inp_img)
                this.inp_img = a;
                if(this.$refs.inp_img_canvas){
                    this.$refs.inp_img_canvas.clear_inpaint()
                }
            }
                
        },

        do_redo(){
            if(this.redo_history.length == 0)
                return;
            this.is_post_generate_box_showing = false
            let a = this.redo_history.pop()
            if(a){
                this.undo_history.push(this.inp_img )
                this.inp_img = a;
                if(this.$refs.inp_img_canvas){
                    this.$refs.inp_img_canvas.clear_inpaint()
                }
               
            }
            
        },

        discard_generation(){
            this.inp_img = this.retry_params.img_url
            let that = this;
            setTimeout(function(){
                that.$refs.inp_img_canvas.restore_mask(that.retry_mask_cached)
            } , 150 ) 
            this.is_post_generate_box_showing = false
            
        },

        onDragFile(e) {
            if (!this.stable_diffusion.is_input_avail)
                return;
            if (!e.dataTransfer.files[0].type.startsWith('image/'))
                return;
            let img_path = e.dataTransfer.files[0].path;
            this.set_inp_image(img_path)
        },

        set_inp_image(img_path){
            this.is_post_generate_box_showing = false
            this.inp_img = img_path;
            this.undo_history = []
            this.redo_history = []
            this.input_img_orig = img_path
            this.history_key = Math.random()+"inp"
            if(this.$refs.inp_img_canvas){
                this.$refs.inp_img_canvas.clear_inpaint()
            }
        },


        open_input_image(){
            if( !this.stable_diffusion.is_input_avail)
                return;
            let img_path = window.ipcRenderer.sendSync('file_dialog',  'img_file' );
            if(img_path && img_path != 'NULL'){
               this.set_inp_image(img_path)
            }
        },

        stop_all(){
            this.is_post_generate_box_showing = false
            this.is_stopping = true;
            this.stable_diffusion.interupt();
        }, 

        clear_canvas(){
            this.is_post_generate_box_showing = false
            if(this.$refs.inp_img_canvas){
                this.$refs.inp_img_canvas.clear_inpaint()
            }
            this.inp_img = ""
            this.undo_history = []
            this.redo_history = []
            this.prompt = ""
            this.input_img_orig = ""
            this.history_key = ""
            this.retry_params  = undefined
        },

        save_img(){
            let out_path = window.ipcRenderer.sendSync('save_dialog' );
            if(!out_path)
                return
            
            let org_path = window.ipcRenderer.sendSync('save_b64_image',  this.$refs.inp_img_canvas.get_img_b64()  );
            if(!org_path)
                return
            org_path = org_path.replaceAll("file://" , "")
            window.ipcRenderer.sendSync('save_file', org_path+"||" +out_path);
        },

       
        send_to_inpaint(im_path ){
          this.set_inp_image(im_path)
          this.app.functions.switch_page("Inpainting")

       }
    },  
}

export default Inpainting;
Inpainting.title = "Inpainting"
Inpainting.description = "Add or remove objects from an image"
Inpainting.icon = "paint-brush"
Inpainting.img_icon = require("../assets/imgs/page_icon_imgs/inpainting.png")
Inpainting.home_category = "main"
Inpainting.sidebar_show = "always"

</script>
<style>
</style>

<style scoped>

.inapint_container{
        border-color:var(--border-color-invert);
        border-width: 1px;
        border-style: solid;
        width:  calc(100% - 30px) ; 
        height: calc(100% - 30px - 70px) ;  
        margin-left:15px ;
        margin-top: 15px; 
    }

.post_generate_box{
    position: fixed;
    background-color: var(--canvas-toolbox-bg );
    padding:18px;
    margin-top: -100px;
    right:50px
}


</style>