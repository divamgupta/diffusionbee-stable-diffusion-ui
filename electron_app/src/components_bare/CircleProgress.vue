<template>

   <div class="progress_circ">
        <svg class="progress-circle" width="200px" height="200px" xmlns="http://www.w3.org/2000/svg">
            <circle class="progress-circle-back"
                    cx="80" cy="80" r="74"></circle>
            <circle class="progress-circle-prog" v-if="done_percentage >= 0 "
                    cx="80" cy="80" r="74" :style="'stroke-dasharray: '+ 475*(done_percentage)/100 +' 999 ;   '"></circle>
            <circle class="progress-circle-prog" v-else
                    cx="80" cy="80" r="74" :style="'stroke-dasharray: '+ 475*(10)/100 +' 999 ; stroke-dashoffset: '+offset_val+'px; '"></circle>
        </svg>
    </div>  

</template>
<script>
export default {
    name: 'CircleProgress',
    props: {
        done_percentage:Number,
    },
    components: {},

    created: function(){
        let that = this;
          this.counterInterval =  setInterval(
            function()
            {
               that.offset_val += -10;
               if(that.offset_val < -400)
                that.offset_val = 0
            }.bind(this), 20);
      },
      destoyed: function(){
        clearInterval( this.counterInterval )
      },


    mounted() {

    },
    data() {
        return {
            offset_val: 0 
        };
    },
    methods: {

    },
}
</script>
<style>
</style>
<style scoped>


.progress_circ {
/*    position: absolute;   */
    height: 160px;
    width: 160px;
    zoom : 0.5;
/*    top: 50%;*/
/*    left: 50%;*/
/*    margin: -80px 0 0 -80px;*/
}

.progress-circle {
  transform: rotate(-90deg);
    margin-top: -40px;
}

.progress-circle-back {
    fill: none; 
    stroke: var(--border-color-invert-extralight);
    stroke-width:10px;
}

.progress-circle-prog {
    fill: none; 
    stroke: #3d6ffa ;
    stroke-width: 10px;  
    stroke-dasharray: 0 999;    
    stroke-dashoffset: 0px;
    transition: stroke-dasharray 0.2s linear 0s;
}

.progress-text {
    width: 100%;
    position: absolute;
    top: 60px;
    text-align: center;
    font-size: 2em;
}

</style>