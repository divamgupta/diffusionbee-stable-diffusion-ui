<template>

    <div class="options_input" style="width: 125px;">
        
         <svg style="height:auto" width="19px" height="19px"  v-html="icon_library[config.icon]"> </svg>

        <b-form-input onkeypress="return event.keyCode != 13;" class="custom-input"
               v-model="form_values[config.id]" :placeholder="config.placeholder"  :type="config.type" width="70"  style="height: 20px;"
             ></b-form-input>
    </div>

</template>
<script>

import FormInputMixin from "./FormInputMixin.vue"
import { icon_library } from "../icon_library.js"
import Vue from 'vue'


export default {
    name: 'Textbox',
    mixins: [FormInputMixin],
    props: {
         config: Object , 
        form_values: Object,
    },
    components: {},
    mounted() {
        if(this.form_values[this.config.id] === undefined && this.config.default_value != undefined){
            Vue.set( this.form_values  , this.config.id  , this.config.default_value  )
        } 
    },
    data() {
        return {
            icon_library:icon_library,
        };
    },
    methods: {

    },
}
</script>
<style>
</style>
<style scoped>

</style>