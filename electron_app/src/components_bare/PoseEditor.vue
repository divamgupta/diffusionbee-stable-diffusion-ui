<template>
    <div style="height:100% ; width:100%; position:  relative;">
        <div id="openpose_container">
        <div id="openpose_canvas" ></div>
    </div>
   </div>
</template>
<script>
import Konva from 'konva';

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
    name: 'PoseEditor',
    props: {
        canvas_width : Number,
        canvas_height : Number,
    },
    components: {},
    data() {
        return {
            stage_w : this.canvas_width,
            stage_h : this.canvas_height,
        }
    },
    mounted() {
        this.init_state();
        this.resize_stage();
    },
    computed : {
    },
    methods: {
        init_state(){
            this.stage_w = this.canvas_width;
            this.stage_h = this.canvas_height;
            
            this.stage = new Konva.Stage({
                container: 'openpose_canvas',
                width: this.stage_w,
                height: this.stage_h,
            });

            this.alpha_layer = new Konva.Layer({opacity	:1 });
            
            this.stage.add(this.alpha_layer);

            let bg = new Konva.Rect({
                                x: 0,
                                y: 0,
                                width: this.stage.width(),
                                height: this.stage.height(),
                                fill : "black",
                            });
            this.alpha_layer.add(bg);


            function addVertex(alpha_layer, name, x, y, color){
                let box = new Konva.Circle({
                    x: x,
                    y: y,
                    radius: 10,
                    fill: color,
                    draggable: true,
                    name: name
                });
                box.on('mouseover', function () {
                    document.body.style.cursor = 'move';

                });
                box.on('mouseout', function () {
                    document.body.style.cursor = 'default';
                });
                alpha_layer.add(box);
                return box;
            }

            function addEdge(alpha_layer, box1, box2, color){
                let line = new Konva.Line({
                    points: [box1.x(), box1.y(), box2.x(), box2.y()],
                    stroke: color,
                    strokeWidth: 10,
                    lineCap: 'round',
                    lineJoin: 'round',
                    opacity: 0.5,
                });
                alpha_layer.add(line);
                line.setZIndex(1);

                box1.on('dragmove', function () {
                    line.points([box1.x(), box1.y(), box2.x(), box2.y()]);
                });
                box2.on('dragmove', function () {
                    line.points([box1.x(), box1.y(), box2.x(), box2.y()]);
                });
            }

            let vertex_join = [
                ['left_shoulder', 'left_elbow'],
                ['left_elbow', 'left_wrist'],
                ['right_shoulder', 'right_elbow'],
                ['right_elbow', 'right_wrist'],
                ['left_shoulder', 'neck'],
                ['right_shoulder', 'neck'],
                ['neck', 'left_hip'],
                ['neck', 'right_hip'],
                ['left_hip', 'left_knee'],
                ['left_knee', 'left_ankle'],
                ['right_hip', 'right_knee'],
                ['right_knee', 'right_ankle'],
                ['nose', 'neck'],
                ['nose', 'left_eye'],
                ['nose', 'right_eye'],
                ['left_eye', 'left_ear'],
                ['right_eye', 'right_ear'],
            ];

            let point_positions = [
                ['left_shoulder', 100, 100, 'rgb(255, 0, 0)'],
                ['left_elbow', 90, 200, 'rgb(255, 0, 0)'],
                ['left_wrist', 70, 300, 'rgb(255, 0, 0)'],
                ['right_shoulder', 200, 100, 'rgb(0, 255, 0)'],
                ['right_elbow', 210, 200, 'rgb(0, 255, 0)'],
                ['right_wrist', 230, 300, 'rgb(0, 255, 0)'],
                ['neck', 150, 100, 'rgb(0, 0, 255)'],
                ['left_hip', 125, 200, 'rgb(0, 0, 255)'],
                ['right_hip', 175, 200, 'rgb(0, 0, 255)'],
                ['left_knee', 105, 300, 'rgb(0, 0, 255)'],
                ['right_knee', 195, 300, 'rgb(0, 0, 255)'],
                ['left_ankle', 90, 400, 'rgb(0, 0, 255)'],
                ['right_ankle', 210, 400, 'rgb(0, 0, 255)'],
                ['nose', 150, 50, 'rgb(255, 255, 0)'],
                ['left_eye', 130, 30, 'rgb(255, 255, 0)'],
                ['right_eye', 170, 30, 'rgb(255, 255, 0)'],
                ['left_ear', 100, 50, 'rgb(255, 0, 255)'],
                ['right_ear', 200, 50, 'rgb(255, 0, 255)'],
            ];
            
            for (let i = 0; i < point_positions.length; i++) {
                addVertex(this.alpha_layer, point_positions[i][0], point_positions[i][1], point_positions[i][2], point_positions[i][3]);
            }
            for (let i = 0; i < vertex_join.length; i++) {
                let point1 = this.alpha_layer.find('.' + vertex_join[i][0])[0];
                let point2 = this.alpha_layer.find('.' + vertex_join[i][1])[0];
                let vertex_color = point_positions.find((element) => element[0] == vertex_join[i][0])[3];
                addEdge(this.alpha_layer, point1, point2, vertex_color);
            }

            this.resize_stage()
            

            window.addEventListener('resize', this.resize_stage);
            onVisible(document.querySelector("#openpose_container") , this.resize_stage )

        },
        resize_stage() {
            let container = document.querySelector('#openpose_container');

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
        },
        get_img_b64(){
            return this.stage.toDataURL();
        },
    },
}
</script>
<style>
</style>
<style scoped>
</style>