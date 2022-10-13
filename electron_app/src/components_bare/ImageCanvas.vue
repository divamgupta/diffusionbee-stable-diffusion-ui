<template>
    <div style="height:100% ; width:100%">
        <img id="myImg" :src="'file://'+image_source" style="display:none">
        <canvas id="myCanvas" style="width:100% ; height:100%;" ></canvas>
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
    },
    components: {},
    mounted() {
        this.ro = new ResizeObserver(this.on_resize);
        let canvas = document.getElementById("myCanvas");
        this.canvas = canvas;
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
            x : "violet" ,
            y : 15 ,
            flag : false,
        };
    },
    methods: {

        findxy(res, e) {

            if(!(this.is_inpaint))
                return;

            if (res == 'down') {
                this.prevX = this.currX;
                this.prevY = this.currY;
                this.currX = e.clientX - this.canvas.parentElement.getBoundingClientRect().x;
                this.currY = e.clientY - this.canvas.parentElement.getBoundingClientRect().y;
        
                this.flag = true;
                let dot_flag = true;
                if (dot_flag) {
                    this.ctx.beginPath();
                    this.ctx.fillStyle = this.x;
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
                    this.currX = e.clientX - this.canvas.parentElement.getBoundingClientRect().x;
                    this.currY = e.clientY - this.canvas.parentElement.getBoundingClientRect().y;
                    this.draw();
                }
            }
        },

        draw() {
            let xmul =  this.canvas.width / this.canvas.offsetWidth;
            let ymul = this.canvas.height / this.canvas.offsetHeight;
            this.ctx.beginPath();
            this.ctx.moveTo(this.prevX*xmul, this.prevY*ymul  );
            this.ctx.lineTo(this.currX*xmul, this.currY*ymul );
            this.ctx.strokeStyle = this.x;
            this.ctx.lineWidth = this.y * Math.sqrt(xmul * ymul);
            this.ctx.stroke();
            this.ctx.closePath();
        },

        on_resize(){
            let canvas = document.getElementById("myCanvas");
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
            }
            else{
                canvas.style.height = pw*r2 +'px';
                canvas.style.width = pw +'px';
            }
            
        },
        clear_inpaint(){
            this.on_img_change();
        },
        on_img_change(){
            let that = this;
            addImageProcess('file://'+this.image_source).then(function(img_tag){

                that.img_tag = img_tag;
                let canvas = document.getElementById("myCanvas");
                let img = that.img_tag;
                let ctx = canvas.getContext("2d");
                
                that.on_resize()

                canvas.height = img.height;
                canvas.width = img.width;

                ctx.clearRect(0, 0, canvas.width, canvas.height);
            

                ctx.drawImage(img, 0,0, img.width, img.height, 0,0, canvas.width, canvas.height);

            })
            
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