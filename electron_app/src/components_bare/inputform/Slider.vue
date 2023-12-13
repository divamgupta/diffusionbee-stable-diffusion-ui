<template>
   <div>
        <p style="float:right; margin-bottom:0px; opacity:0.4 "> {{form_values[this.config.id]}} </p>

        <input :id="rand_id" type="range" :min="config.min_val" :max="config.max_val" @input="set_val(); set_slider();" :value="form_values[config.id]"  step='0.01' class="slider"
             list='tickmarks' style="width: 100%;">

        

        <div id="tickmarks">
            <p>{{tick_vals[0]}}</p>
            <p>{{tick_vals[1]}}</p>
            <p>{{tick_vals[2]}}</p>
            <p>{{tick_vals[3]}}</p>
             <p>{{tick_vals[4]}}</p>
            <!-- <p>20</p> -->
        </div>

        

   </div>
</template>
<script>

import FormInputMixin from "./FormInputMixin.vue"
import Vue from 'vue'

export default {
    name: 'Slider',
    mixins: [FormInputMixin],
    props: {
         config: Object , 
         form_values: Object,
    },
    components: {},
    mounted() {
        this.set_slider()

        if(this.form_values[this.config.id] === undefined && this.config.default_value ){
            Vue.set( this.form_values  , this.config.id  , this.config.default_value  )
        } 

    },

    data() {
        return {
            rand_id : Math.random()
        };
    },
    methods: {
        set_val() {
            let el = document.getElementById(this.rand_id)
            let value = (el.value - el.min) / (el.max - el.min) * 100
            value = Number(el.value) + ""
            Vue.set(this.form_values , this.config.id , value)
        } , 

        set_slider(){
            let el = document.getElementById(this.rand_id)
            let value = Number(this.form_values[this.config.id] - el.min) * ( 100/(el.max - el.min)) ;
             el.style.background = 'linear-gradient(to right, var(--slider-progress) 0%, var(--slider-progress) ' + value + '%, var(--slider-progress_end) ' + value + '%, var(--slider-progress_end) 100%)'
        },

        is_input_valid(){
            return true;
        }

    },
    computed:{
        tick_vals(){
            return [ this.config.min_val, 
                Math.round(this.config.min_val + (this.config.max_val-this.config.min_val)/4) , 
                Math.round(this.config.min_val + 2*(this.config.max_val-this.config.min_val)/4  )  , 
                Math.round(this.config.min_val + 3*(this.config.max_val-this.config.min_val)/4  )  , 
                this.config.max_val  ]
        } , 

        cur_val(){
            return this.form_values[this.config.id]
        }
    } , 

    watch: {
        'cur_val' : {
            handler: function() {
               this.set_slider()
            },
            deep: false
        } , 
    }
}
</script>
<style>
</style>
<style scoped>


</style>