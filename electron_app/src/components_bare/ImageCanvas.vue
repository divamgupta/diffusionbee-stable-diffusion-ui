<template>
    <div style="height:100% ; width:100%; position:  relative;">
        <img  @load="on_img_load2" :id="canvas_d_id+'img'" :src="'file://'+image_source" style="display:none">
        <canvas :id="canvas_d_id" style="width:100% ; height:100%; position: absolute ; top:0 , left:0  " ></canvas>
        <canvas :id="canvas_id" style="width:100% ; height:100%; position: absolute ; top:0 , left:0 ; opacity:0.7" ></canvas>
       
   </div>
</template>
<script>
import Vue from 'vue'

function addImageProcess(src){
  return new Promise((resolve, reject) => {
    let img = new Image()
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = src
  })
}

export default {
    name: 'ImageCanvas',
    props: {
        image_source : String,
        is_inpaint : Boolean,
        is_disabled : Boolean,
        canvas_d_id : String, 
        canvas_id: String,
        stroke_size_no : String,
        on_img_load: Function, 
    },
    components: {},
    computed: {
        stroke_size(){
            if(this.stroke_size_no)
                return Number( this.stroke_size_no)/5
            return 7;
        }
    },
    mounted() {
        this.ro = new ResizeObserver(this.on_resize);
        let canvas = document.getElementById(this.canvas_id);
        this.canvas = canvas;
        this.canvasD = document.getElementById(this.canvas_d_id);
        this.ctx = canvas.getContext("2d");
        this.ro.observe(canvas.parentElement);
        let that = this;

        if(this.image_source)
            this.on_img_change();

        canvas.addEventListener("mousemove", function (e) {
            that.findxy('move', e)
        }, false);
        canvas.addEventListener("mousedown", function (e) {
            that.findxy('down', e)
        }, false);
        canvas.addEventListener("mouseup", function (e) {
            that.findxy('up', e)
        }, false);
        canvas.addEventListener("mouseout", function (e) {
            that.findxy('out', e)
        }, false);

    },
    beforeDestroy(){
        this.ro.disconnect()
    },
    data() {
        return {
            img_tag : undefined,
            prevX : 0 , 
            prevY : 0 , 
            currX : 0 , 
            currY : 0 , 
            
            stroke_color : "#ff00ff" ,
            // x : "#ffffff" ,
            
            flag : false,
            is_something_drawn : false,
        };
    },
    methods: {

        on_img_load2(){
            if(this.on_img_load)
                 this.on_img_load()
        },

        findxy(res, e) {

            if(!(this.is_inpaint))
                return;

            if(this.is_disabled)
                return;

            if (res == 'down') {
                this.prevX = this.currX;
                this.prevY = this.currY;
                this.currX = e.clientX - this.canvas.getBoundingClientRect().x;
                this.currY = e.clientY - this.canvas.getBoundingClientRect().y;
        
                this.flag = true;
                let dot_flag = true;
                if (dot_flag) {
                    this.ctx.beginPath();
                    this.ctx.fillStyle = this.stroke_color;
                    this.ctx.fillRect(this.currX, this.currY, 2, 2);
                    this.ctx.closePath();
                    dot_flag = false;
                }
            }
            if (res == 'up' || res == "out") {
                this.flag = false;
            }
            if (res == 'move') {
                if (this.flag) {
                    this.prevX = this.currX;
                    this.prevY = this.currY;
                    this.currX = e.clientX - this.canvas.getBoundingClientRect().x;
                    this.currY = e.clientY - this.canvas.getBoundingClientRect().y;
                    this.draw();
                }
            }
        },

        draw() {
            if(this.is_disabled)
                return;

            let xmul =  this.canvas.width / this.canvas.offsetWidth;
            let ymul = this.canvas.height / this.canvas.offsetHeight;
            // this.ctx.beginPath();
            // this.ctx.moveTo(this.prevX*xmul, this.prevY*ymul  );
            // this.ctx.lineTo(this.currX*xmul, this.currY*ymul );
            // this.ctx.strokeStyle = this.x;
            // this.ctx.lineWidth = this.y * Math.sqrt(xmul * ymul);
            // this.ctx.stroke();
            // this.ctx.closePath();

            this.ctx.beginPath();
            this.ctx.arc(this.prevX*xmul, this.prevY*ymul , this.stroke_size* Math.sqrt(xmul * ymul), 0, 2 * Math.PI);
            this.ctx.arc((this.prevX+this.currX)*xmul/2, (this.prevY+this.currY)*ymul/2 , this.stroke_size* Math.sqrt(xmul * ymul), 0, 2 * Math.PI);
            this.ctx.arc(this.currX*xmul, this.currY*ymul , this.stroke_size* Math.sqrt(xmul * ymul), 0, 2 * Math.PI);
            this.ctx.fill();
            this.is_something_drawn = true

        },

        get_size(){
            let img =  document.getElementById(this.canvas_d_id+"img")
            return {width: img.width ,height: img.height }
        },

        on_resize(){
            let canvas = document.getElementById(this.canvas_id);
            let canvasD = document.getElementById(this.canvas_d_id);
            let img = this.img_tag;

            if(!img)
                return;
            
            let ph = canvas.parentElement.offsetHeight;
            let pw = canvas.parentElement.offsetWidth;

            let r = img.width / img.height;
            let r2 = img.height / img.width;
            if(ph*r <= pw ){
                canvas.style.height = ph +'px';
                canvas.style.width = ph*r +'px';

                canvasD.style.height = ph +'px';
                canvasD.style.width = ph*r +'px';

                canvas.style.marginLeft = (pw - ph*r )/2  + "px"
                canvasD.style.marginLeft = (pw - ph*r )/2  + "px"

                canvas.style.marginTop = 0 + "px"
                canvasD.style.marginTop = 0 + "px"

            }
            else{
                canvas.style.height = pw*r2 +'px';
                canvas.style.width = pw +'px';

                canvasD.style.height = pw*r2 +'px';
                canvasD.style.width = pw +'px';

                canvas.style.marginLeft =  0 + "px"
                canvasD.style.marginLeft =  0 + "px"

                canvas.style.marginTop = (ph - pw*r2 )/2 + "px"
                canvasD.style.marginTop = (ph - pw*r2 )/2 + "px"

            }
            
        },
        clear_inpaint(){
            let canvas = document.getElementById(this.canvas_id);
            let ctx = canvas.getContext("2d");
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            this.is_something_drawn = false 
        },
        on_img_change(){
            let that = this;
            addImageProcess('file://'+this.image_source).then(function(img_tag){

                that.img_tag = img_tag;
                let canvasD = document.getElementById(that.canvas_d_id);
                let canvas = document.getElementById(that.canvas_id);
                let img = that.img_tag;
                let ctxD = canvasD.getContext("2d");
                
                that.on_resize()

                canvasD.height = img.height;
                canvasD.width = img.width;
                canvas.height = img.height;
                canvas.width = img.width;

                ctxD.clearRect(0, 0, canvasD.width, canvasD.height);
                ctxD.drawImage(img, 0,0, img.width, img.height, 0,0, canvasD.width, canvasD.height);

                that.clear_inpaint()

            })
        },
        get_img_b64(){
            return this.canvasD.toDataURL();
        } , 
        get_mask_b64(){
            let canvas = document.createElement('canvas');
            canvas.width = this.canvas.width;
            canvas.height = this.canvas.height;
            let ctx =  canvas.getContext("2d");
            // let filt_w = canvas.width/50    
            ctx.filter = ' grayscale(1) brightness(10000) contrast(10000)'; // blur('+filt_w+'px)
            ctx.fillStyle = "black";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(this.canvas, 0, 0);
            return canvas.toDataURL();

        }, 
        get_img_mask_b64(){
            let canvas = document.createElement('canvas');
            canvas.width = this.canvasD.width;
            canvas.height = this.canvasD.height;
            let ctx =  canvas.getContext("2d");
            ctx.drawImage(this.canvasD, 0, 0);
            ctx.drawImage(this.canvas, 0, 0);
            
            return canvas.toDataURL();
        } , 

        get_mask_for_cache(){
            return this.canvas.toDataURL();
        },
       
       restore_mask(mask_b64){
            let canvas = this.canvas;
            let ctx =  canvas.getContext("2d");
            
            var image = new Image();
            image.onload = function() {
                ctx.drawImage(image, 0, 0);
            };
            image.src = mask_b64
        }
    },

    watch: {
        'image_source': {

            handler: function() {
                Vue.nextTick(this.on_img_change)
                // this.on_img_change()
            },
            deep: true
        } , 

        'is_inpaint': {
            handler: function(v) {
                if(!v){
                    this.clear_inpaint();
                }
            },
            deep: true
        } , 
    }
}
</script>
<style>
</style>
<style scoped>
</style>