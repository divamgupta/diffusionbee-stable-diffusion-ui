<template>
     <div  class="animatable_content_box ">
        <!-- <div class="center">
            <p >Coming Soon!</p>
        </div> -->
        <div id="outpainting_container" style=" border: medium dashed green; ">

        </div>
     </div>
</template>
<script>
import Konva from 'konva';


export default {
    name: 'Outpainting',
    props: {},
    components: {},
    mounted() {
           this.init_state();
           this.resize_stage()
    },
    data() {
        return {
            stage : undefined,
            stage_w : 1000 , 
            stage_h : 500 ,
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
                strokeWidth: 4,
                draggable: true,
            });

            // add cursor styling
            box.on('mouseover', function () {
                document.body.style.cursor = 'move';
            });
            box.on('mouseout', function () {
                document.body.style.cursor = 'default';
            });

            let layer = new Konva.Layer();
            layer.add(box);
            this.stage.add(layer);

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
        }

    },
}
</script>
<style>
</style>
<style scoped>
</style>