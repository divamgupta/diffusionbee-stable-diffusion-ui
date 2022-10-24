<template>
     <div  class="animatable_content_box ">
       
        <div id="outpainting_container" style="  ">
        </div>
        <textarea 
                    v-model="prompt" 
                    placeholder="Enter your prompt here" 
                    style="border-radius: 12px 12px 12px 12px; width: calc(100%); resize: none; " 
                    class="form-control outpaint_textbox"  
                    v-bind:class="{ 'disabled' : !stable_diffusion.is_input_avail}"
                    :rows="2">
        </textarea>
        
        <div v-if="stable_diffusion.is_input_avail" class="l_button button_medium button_colored" style="float:right ; margin-top: 20px; " @click="generate()" >Generate</div>
        <span v-else-if="stable_diffusion.generated_by=='outpainting'"   >
            <div v-if="is_stopping" class="l_button button_medium button_colored" style="float:right; float:right ; margin-top: 20px; " @click="stop_generation">Stopping ...</div>
            <div v-else class="l_button button_medium button_colored" style="float:right; float:right ; margin-top: 20px; " @click="stop_generation">Stop</div>
        </span>


        <div v-if="backend_error" style="color:red ; margin-top:50px;">
            <div class="center loader_box">
                <p>Error: {{backend_error}} </p>
            </div>
        </div>

        <div v-if="!stable_diffusion.is_input_avail && stable_diffusion.generated_by=='outpainting'">
            <LoaderModal :loading_percentage="done_percentage" loading_title="Generating" :loading_desc="stable_diffusion.generation_state_msg"></LoaderModal>
        </div>


     </div>
</template>
<script>
import Konva from 'konva';
import LoaderModal from '../components_bare/LoaderModal.vue'


export default {
    name: 'Outpainting',
    props: {
        app_state : Object   , 
        stable_diffusion : Object,
    },
    components: {LoaderModal},
    mounted() {
           this.init_state();
           this.resize_stage()
    },
    data() {
        return {
            stage : undefined,
            stage_w : 1000 , 
            stage_h : 500 ,
            prompt : "" ,

            is_stopping : false,
            backend_error : "",
            done_percentage : -1,
        };
    },
    methods: {
        init_state(){
            this.stage = new Konva.Stage({
                container: 'outpainting_container',   // id of container <div>
                width: this.stage_w,
                height: this.stage_h
            });

            let rectX = this.stage.width() / 2 - 100;
            let rectY = this.stage.height() / 2 - 100;

            let box = new Konva.Rect({
                x: rectX,
                y: rectY,
                width: 200,
                height: 200,
                stroke: 'red',
                strokeWidth: 1,
                draggable: true,
            });
            this.box = box;

            // add cursor styling
            box.on('mouseover', function () {
                document.body.style.cursor = 'move';
            });
            box.on('mouseout', function () {
                document.body.style.cursor = 'default';
            });

            this.alpha_layer = new Konva.Layer();
            this.stage.add(this.alpha_layer);

            this.images_layer = new Konva.Layer();
            this.stage.add(this.images_layer);

            


            this.box_layer = new Konva.Layer();
            this.stage.add(this.box_layer);
            this.box_layer.add(box);

            

            window.addEventListener('resize', this.resize_stage);
        },

        resize_stage() {
            let container = document.querySelector('#outpainting_container');

            // now we need to fit stage into parent container
            let containerWidth = container.offsetWidth;

            // but we also make the full scene visible
            // so we need to scale all objects on canvas
            let scale = containerWidth / this.stage_w;

            this.stage.width(this.stage_w * scale);
            this.stage.height(this.stage_h * scale);
            this.stage.scale({ x: scale, y: scale });
        } , 

        add_img_to_box(img_path){
            
            let that = this;
            let scale =  that.box.width() / 512 

            Konva.Image.fromURL('file://'+ img_path , function (imgg) {
                imgg.setAttrs({
                x: that.box.x(),
                y: that.box.y(),
                scaleX: scale,
                scaleY: scale ,
                });
                that.images_layer.add(imgg);

                let box = new Konva.Rect({
                                x: that.box.x(),
                                y: that.box.y(),
                                width: that.box.width(),
                                height: that.box.height(),
                                fill : "white",
                                strokeWidth : 0,
                            });
                that.alpha_layer.add(box);


            });
        } , 

        get_img_of_box(is_mask=false){
            let s = this.stage.scale().x
            let layer;
            if(is_mask)
                layer = this.alpha_layer
            else
                layer = this.images_layer

            let data_uri = layer.toDataURL({ 
                pixelRatio: 3 , 
                x:  this.box.x() * s  , 
                y: this.box.y()  * s   , 
                width: this.box.width() * s , 
                height: this.box.height() * s } );
            let img_url = window.ipcRenderer.sendSync('save_b64_image',  data_uri , true );
            console.log(img_url)
            return img_url
        } , 

        stop_generation(){
            this.is_stopping = true;
            this.stable_diffusion.interupt();
        },



        // get_mask_of_box(){
        //     let s = this.stage.scale().x
        //     let data_uri = this.images_layer.toDataURL({ 
        //         pixelRatio: 3 , 
        //         x:  this.box.x() * s  , 
        //         y: this.box.y()  * s   , 
        //         width: this.box.width() * s , 
        //         height: this.box.height() * s } );

        //     let canvas = document.createElement('canvas');
        //     canvas.width = this.box.width() * s * 3
        //     canvas.height = this.box.height() * s *3

        //     let ctx =  canvas.getContext("2d");

        //     ctx.filter = ' grayscale(1) brightness(10000) contrast(10000)'; // blur('+filt_w+'px)
        //     ctx.fillStyle = "black";
        //     ctx.fillRect(0, 0, canvas.width, canvas.height);
            
        //     let myImage = new Image();
        //     myImage.src = data_uri;

        //     myImage.onload = function() {
        //         ctx.drawImage(myImage , 0, 0);
        //         data_uri = canvas.toDataURL();
        //         let img_url = window.ipcRenderer.sendSync('save_b64_image',  data_uri , true );
        //         console.log(img_url)
        //     };
        // },



        generate(){
            let img_path = this.get_img_of_box(false)
            let mask_path = this.get_img_of_box(true)

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
                mask_image: mask_path ,
                input_image : img_path,
                model_id: 1 , 
                is_inpaint : true,
            }

            this.backend_error = "";
            this.done_percentage = -1;
            this.is_stopping = false;

            let that = this;

            let callbacks = {
                on_img(img_path){
                    that.add_img_to_box(img_path)
                },
                on_progress(p){
                    that.done_percentage = p;
                    
                },
                on_err(err){
                    that.backend_error = err;
                },
            }

            if(this.stable_diffusion)
                this.stable_diffusion.text_to_img(params, callbacks, 'outpainting');


        }

    },
}
</script>
<style>
    #outpainting_container{
        /* background-color: #e5e5f7; */
        opacity: 0.8;
        background-image: radial-gradient( rgba(255,255,255,0.25) 0.5px, rgba(0,0,0,0) 0.5px);
        background-size: 10px 10px;
        border-color: rgba(255,255,255,0.25);
        border-width: 1px;
        border-style: solid;

    }

    .outpaint_textbox{
        margin-top: 15px; 
        max-width: calc(100vw - 160px);
        float:left
    }
</style>
<style scoped>
</style>