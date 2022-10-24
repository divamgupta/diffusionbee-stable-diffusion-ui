<template>
     <div  class="animatable_content_box ">

        <div class="content_toolbox" style="margin-bottom: 5px; margin-top: -5px ;">
            <div class="l_button" v-if="is_stage_modified && stable_diffusion.is_input_avail"  style="float:right "  @click="init_state"> Clear</div>
            <div class="l_button"  v-if="is_stage_modified && stable_diffusion.is_input_avail"   style="float:right "  @click="save_image"> Save Image </div>
            <div v-if="undo_history.length > 0 && stable_diffusion.is_input_avail " class="l_button"  style="float:right " @click="do_undo" > Undo </div>
        </div>
       
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
        
        <div v-if="stable_diffusion.is_input_avail" style="margin-top: 20px">
            
            <div  class="l_button button_medium button_colored" style="float:right ; " @click="generate()" >Generate</div>
            

        </div>
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

function onVisible(element, callback) {
  new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if(entry.intersectionRatio > 0) {
        callback(element);
        observer;
        // observer.disconnect();
      }
    });
  }).observe(element);
}


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
            stage_h : 400 ,
            prompt : "" ,

            undo_history : [],
            is_stage_modified: false, 
            is_stopping : false,
            backend_error : "",
            done_percentage : -1,
        };
    },
    watch: {
        'stable_diffusion.is_input_avail': {
            handler: function(v) {
                if(v)
                    this.box.draggable(true)
                else
                    this.box.draggable(false)
            },
            deep: true
        } , 
    },

    methods: {
        init_state(){

            let canvas_bg_color = "#F2F2F2"
            let box_color = '#4070f7'
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                // dark mode
                canvas_bg_color = "#1c1c1c"
            }

            this.undo_history = []
            this.is_stage_modified = false


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
                stroke: box_color,
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

            this.alpha_layer = new Konva.Layer({opacity	:1 });
            this.stage.add(this.alpha_layer);

            let bg = new Konva.Rect({
                                x: 0,
                                y: 0,
                                width: this.stage.width(),
                                height: this.stage.height(),
                                fill : "white",
                            });
            this.alpha_layer.add(bg);
                    

            this.images_layer = new Konva.Layer();
            this.stage.add(this.images_layer);

            

            bg = new Konva.Rect({
                                x: 0,
                                y: 0,
                                width: this.stage.width(),
                                height: this.stage.height(),
                                fill : canvas_bg_color,
                            });
            this.images_layer.add(bg);

            


            this.box_layer = new Konva.Layer();
            this.stage.add(this.box_layer);
            this.box_layer.add(box);
            
            this.resize_stage()
            

            window.addEventListener('resize', this.resize_stage);
            onVisible(document.querySelector("#outpainting_container") , this.resize_stage )
        },

        resize_stage() {
            let container = document.querySelector('#outpainting_container');

            // now we need to fit stage into parent container
            let containerWidth = container.offsetWidth;
            if(containerWidth < 10 )
                return;

            // but we also make the full scene visible
            // so we need to scale all objects on canvas
            let scale = containerWidth / this.stage_w;

            this.stage.width(this.stage_w * scale - 5 );
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
                                fill : "black",
                                strokeWidth : 0,
                            });
                that.alpha_layer.add(box);

                that.undo_history.push({alpha : box , img : imgg })
                that.is_stage_modified = true


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

        save_image(){
            let img_b64 = this.images_layer.toDataURL({ pixelRatio: 3})

            let out_path = window.ipcRenderer.sendSync('save_dialog' );
            if(!out_path)
                return
            let org_path = window.ipcRenderer.sendSync('save_b64_image',  img_b64 , true );
            org_path = org_path.replaceAll("file://" , "")
            window.ipcRenderer.sendSync('save_file', org_path+"||" +out_path);


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

        do_undo(){
            // if(! this.prev_canvas_b64)
            //     return;
            // let myImage = new Image();
            // myImage.src = this.prev_canvas_b64 ;
            // let that = this;
            // myImage.onload = function() {
            //     var kimg = new Konva.Image({
            //         x: 0,
            //         y: 0,
            //         image: myImage,
            //         width: 300,
            //          height: 300,
            //     });
            //     that.images_layer.add(kimg)
            // }
            let im = this.undo_history.pop()
            im.img.destroy()
            im.alpha.destroy()

        },

        generate(){
            let img_path = this.get_img_of_box(false)
            let mask_path = this.get_img_of_box(true)

            if(this.prompt == "")
                return; 

            this.prev_canvas_b64 = this.images_layer.toDataURL()

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
        /* opacity: 0.8; */
        /* background-image: radial-gradient( rgba(255,255,255,0.25) 0.5px, rgba(0,0,0,0) 0.5px); */
        background-size: 10px 10px;
        border-color: rgb(206, 212, 218);
        border-width: 1px;
        border-style: solid;

    }

    @media (prefers-color-scheme: dark) {
        #outpainting_container{
            border-color: #606060
        }
    }

    .outpaint_textbox{
        margin-top: 15px; 
        max-width: calc(100vw - 160px);
        float:left
    }
</style>
<style scoped>
</style>