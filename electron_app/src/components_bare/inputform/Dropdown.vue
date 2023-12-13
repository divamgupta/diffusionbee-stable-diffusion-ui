<template>

        <div class="options_input" style="width: 95px; margin-left: 6px;">
            <!-- <span v-html="icon_library"></span> -->
            
            <svg width="19px" height="19px"  v-html="icon_library[config.icon]"> </svg>


            <b-form-select v-model="form_values[config.id]" :options="config.options"
                required></b-form-select>
        </div>
</template>
<script>

import FormInputMixin from "./FormInputMixin.vue"
import { icon_library } from "../icon_library.js"
import Vue from "vue"

export default {
    name: 'Dropdown',
    mixins: [FormInputMixin],
    props: {
        config: Object , 
        form_values: Object,
    },
    components: {},
    
    mounted() {
        if(this.form_values[this.config.id] === undefined){
            Vue.set( this.form_values  , this.config.id  , this.config.default_value || this.config.options[0])
        }
        this.reset_selected_if_invalid()
    },
    data() {
        return {
            icon_library:icon_library,
        };
    },
    methods: {
        // if the selected option not in options list then reset the selected 
        reset_selected_if_invalid(){
            if(!this.config.options.includes(this.form_values[this.config.id])){
                  if(this.config.options.length > 0){
                    if( this.config.default_value != undefined && this.config.options.includes(this.config.default_value) ){
                        Vue.set(this.form_values,this.config.id , this.config.default_value )
                    } else {
                        Vue.set(this.form_values,this.config.id , this.config.options[0] )
                    }
                    
                  }
              }
        }
    },

    watch : {
       
       'config.options': {
           handler: function() {
              this.reset_selected_if_invalid()
           },
           deep: true
       } , 

   },


}
</script>
<style>
</style>
<style scoped>


</style>