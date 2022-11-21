<template>
     <div  class="animatable_content_box ">

        <div class="content_toolbox" style="margin-bottom: 5px; margin-top: -5px ;">
            <div class="l_button" v-if="stable_diffusion.is_input_avail"  style="float:right "  @click="init_state"> Reset</div>
            <div class="l_button"  v-if="is_stage_modified && stable_diffusion.is_input_avail"   style="float:right "  @click="save_image"> Save Image </div>
            <div v-if="undo_history.length > 0 && stable_diffusion.is_input_avail " class="l_button"  style="float:right " @click="do_undo" > Undo </div>
            <div class="l_button" v-if="stable_diffusion.is_input_avail"  style="float:right "  @click="add_ext_img"> Add Image</div>
            <div class="l_button" v-if="stable_diffusion.is_input_avail && is_stage_modified"  style="float:right "  @click="is_eraser_enabled=!is_eraser_enabled; freeze_last_resizable_img()"> {{is_eraser_enabled?'Stop':'Start'}} Erasing</div>
            
        </div>
       
        <div id="outpainting_container" @drop.prevent="onDragFile" @dragover.prevent style="  ">
        </div>
        <textarea 
                    v-model="prompt" 
                    placeholder="Enter your prompt here" 
                    style="border-radius: 12px 12px 12px 12px; width: calc(100%); resize: none; " 
                    class="form-control outpaint_textbox"  
                    v-bind:class="{ 'disabled' : !stable_diffusion.is_input_avail}"
                    :rows="is_negative_prompt_avail ? 1:2">
        </textarea>
        <textarea 
                    v-if="is_negative_prompt_avail"
                    v-model="negative_prompt" 
                    placeholder="Enter your negative prompt here" 
                    style="border-radius: 12px 12px 12px 12px; width: calc(100%);font-size:13px; margin-top:14px; resize: none; " 
                    class="form-control outpaint_textbox"  
                    v-bind:class="{ 'disabled' : !stable_diffusion.is_input_avail}"
                    :rows="is_negative_prompt_avail ? 1:2">
        </textarea>

       
        
        
        <div v-if="stable_diffusion.is_input_avail" style="margin-top: 15px">
            <SDOptionsDropdown :style="is_negative_prompt_avail?'margin-top:-43px':''" :options_model_values="this_object"  :elements_hidden="[ 'num_imgs', 'inp_img_strength', 'batch_size', 'guidence_scale', 'img_h', 'custom_model', 'seed']"> </SDOptionsDropdown>
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
            <LoaderModal :loading_percentage="done_percentage" loading_title="Generating" :loading_desc="stable_diffusion.generation_state_msg" :remaining_times="stable_diffusion.remaining_times"></LoaderModal>
        </div>

        <p style="opacity:0.5; zoom:0.8; float:left; max-width: calc(100vw - 200px); margin-bottom: 0; "> Please describe image you want to draw in the box. </p>

     </div>
</template>
<script>
import Konva from 'konva';
import LoaderModal from '../components_bare/LoaderModal.vue'
import Vue from 'vue'
import SDOptionsDropdown from '../components_bare/SDOptionsDropdown.vue'

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
    components: {LoaderModal, SDOptionsDropdown},
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

            is_earasing: false, 
            is_eraser_enabled: false,
            is_negative_prompt_avail : false,
            negative_prompt : "",
            selected_model : 'Default'
        };
    },
    watch: {
        'stable_diffusion.is_input_avail': {
            handler: function() {
                if(this.stable_diffusion.is_input_avail && (!this.is_eraser_enabled))
                    this.box.draggable(true)
                else
                    this.box.draggable(false)
            },
            deep: true
        } , 
        'is_eraser_enabled' : {
            handler: function() {
                if(this.stable_diffusion.is_input_avail && (!this.is_eraser_enabled))
                    this.box.draggable(true)
                else
                    this.box.draggable(false)
            },
            deep: true
        } , 
    },
    computed:{
        this_object(){
            return this;
        }
    },
    methods: {
        init_state(){
            let that = this;
            this.stage_h = this.stage_w / (window.innerWidth  / ( window.innerHeight - 230 ));

            this.prompt = ""

            this.canvas_bg_color = "#F2F2F2"
            let box_color = '#4070f7'
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                // dark mode
                this.canvas_bg_color = "#1c1c1c"
            }

            this.freeze_last_resizable_img()

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
                if(!that.is_eraser_enabled)
                    document.body.style.cursor = 'move';
                else 
                    document.body.style.cursor = 'default';

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
                    

            this.images_layer = new Konva.Layer({opacity:1});
            this.stage.add(this.images_layer);

            bg = new Konva.Rect({
                                x: 0,
                                y: 0,
                                width: this.stage.width(),
                                height: this.stage.height(),
                                fill : this.canvas_bg_color,
                            });
            this.images_layer.add(bg);

            


            this.box_layer = new Konva.Layer();
            this.stage.add(this.box_layer);
            this.box_layer.add(box);

            let tr = new Konva.Transformer({keepRatio : true , rotateEnabled:false , flipEnabled:false, enabledAnchors: ['top-left', 'top-right', 'bottom-left', 'bottom-right']  });
            this.box_layer.add(tr);
            tr.nodes([box]);
            
            box.on('transform', function () {
                box.setAttrs({
                    width: Math.round(box.width() * box.scaleX()),
                    height: Math.round(box.height() * box.scaleY()),
                    scaleX: 1,
                    scaleY: 1
                });
            });
            
            this.resize_stage()
            

            window.addEventListener('resize', this.resize_stage);
            onVisible(document.querySelector("#outpainting_container") , this.resize_stage )

            this.init_eraser()
        },

        init_eraser(){
            let that = this;
            this.stage.on('mousedown touchstart', function () {
                if(!that.is_eraser_enabled)
                    return;
                that.is_earasing = true;
                let pos = that.stage.getPointerPosition();
                let sx = that.stage.scale().x
                let sy = that.stage.scale().y
                
                that.lastLine = new Konva.Line({
                    stroke: that.canvas_bg_color,
                    strokeWidth: 15,
                    globalCompositeOperation: 'source-over',
                    // round cap for smoother lines
                    lineCap: 'round',
                    lineJoin: 'round',
                    // add point twice, so we have some drawings even on a simple click
                    points:[pos.x/sx, pos.y/sy, pos.x/sx, pos.y/sy],
                });

                

                that.lastLine_alpha = new Konva.Line({
                    stroke: 'white',
                    strokeWidth: 20,
                    globalCompositeOperation: 'source-over',
                    
                    // round cap for smoother lines
                    lineCap: 'round',
                    lineJoin: 'round',
                    // add point twice, so we have some drawings even on a simple click
                    points: [pos.x/sx, pos.y/sy, pos.x/sx, pos.y/sy],
                });

                that.undo_history.push({alpha : that.lastLine_alpha  , img : that.lastLine })


                that.images_layer.add(that.lastLine);
                that.alpha_layer.add(that.lastLine_alpha)
            });


            this.stage.on('mouseup touchend', function () {
                that.is_earasing  = false;
                that.is_eraser_enabled = false;
            });

            this.stage.on('mousemove touchmove', function () {
                if (! that.is_earasing  ) {
                    return;
                }
                if(!that.is_eraser_enabled)
                    return;

                let sx = that.stage.scale().x
                let sy = that.stage.scale().y
                const pos = that.stage.getPointerPosition();
                let newPoints = that.lastLine.points().concat([pos.x/sx, pos.y/sy]);
                that.lastLine.points(newPoints);
                that.lastLine_alpha.points(newPoints);
            });

        },

        freeze_last_resizable_img(){
            if(this.last_resizable_img){
                this.last_resizable_img.img.draggable(false)
                this.last_resizable_img.tr.destroy()
                this.last_resizable_img = undefined
            }
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


        add_img_to_stage(img_path, is_resizable  ){
            
            let that = this;
            let scale =  that.box.scaleX()

            this.freeze_last_resizable_img()

            Konva.Image.fromURL('file://'+ img_path , function (imgg) {
            

                imgg.setAttrs({
                    x: that.box.x(),
                    y: that.box.y(),
                    width: that.box.width(),
                    height: that.box.height(),
                    });
                that.images_layer.add(imgg);

                let box = new Konva.Rect({
                                x: imgg.x()+2,
                                y: imgg.y()+2,
                                width: imgg.width()-4/scale,
                                height: imgg.height()-4/scale,
                                scaleX: scale,
                                scaleY: scale ,
                                fill : "black",
                                strokeWidth : 0,
                            });


                that.alpha_layer.add(box);
                that.undo_history.push({alpha : box , img : imgg })
                that.is_stage_modified = true

                if(is_resizable){
                    imgg.draggable(true)
                    let tr = new Konva.Transformer({keepRatio : true , rotateEnabled:false , flipEnabled:false  });
                    that.images_layer.add(tr);
                    tr.nodes([imgg]);
                    that.last_resizable_img = { img: imgg, tr:tr }

                    imgg.on('transformend',     function () {
                        box.height(imgg.height() - 4/imgg.scaleY())
                        box.width(imgg.width() - 4/imgg.scaleX())
                        box.x(imgg.x() + 2)
                        box.y(imgg.y() + 2)
                        box.scaleY(imgg.scaleY() )
                        box.scaleX(imgg.scaleX() )
                    });

                    imgg.on('dragmove',     function () {
                        box.height(imgg.height() - 4/imgg.scaleY())
                        box.width(imgg.width() - 4/imgg.scaleX())
                        box.x(imgg.x() + 2)
                        box.y(imgg.y() + 2)
                        box.scaleY(imgg.scaleY() )
                        box.scaleX(imgg.scaleX() )
                    });


                }


            });
        } , 

        add_ext_img(){
            if( !this.stable_diffusion.is_input_avail)
                return;
            let img_path = window.ipcRenderer.sendSync('file_dialog',  'img_file' );
            if(img_path && img_path != 'NULL'){
                this.add_img_to_stage(img_path, true)
            }
        },

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

        onDragFile(e) {
           if (!this.stable_diffusion.is_input_avail)
               return;
           if (!e.dataTransfer.files[0].type.startsWith('image/'))
               return;
           let img_path = e.dataTransfer.files[0].path;
           this.add_img_to_stage(img_path, true)
       },

        do_undo(){
            this.freeze_last_resizable_img()
            let im = this.undo_history.pop()
            im.img.destroy()
            im.alpha.destroy()

        },

        generate(){

            

            if(this.prompt == ""){
                Vue.$toast.default('You need to enter a prompt')
                return; 
            }
                

            if(this.last_resizable_img){
                this.freeze_last_resizable_img()
                setTimeout(this.generate, 100); // there is delay coz the rectangle wont go away
                return;
            }

            let img_path = this.get_img_of_box(false)
            let mask_path = this.get_img_of_box(true)

            

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

            if(this.is_negative_prompt_avail)
                params['negative_prompt'] = this.negative_prompt;

            let that = this;

            let callbacks = {
                on_img(img_path){
                    that.add_img_to_stage(img_path)
                },
                on_progress(p){
                    that.done_percentage = p;
                    
                },
                on_err(err){
                    that.backend_error = err;
                },
            }

            if(this.is_negative_prompt_avail)
                params['negative_prompt'] = this.negative_prompt;

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