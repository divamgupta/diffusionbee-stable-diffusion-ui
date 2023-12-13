<template>

    <div class="options_input" style="width: 100%;">
        

        <b-form-input onkeypress="return event.keyCode != 13;" class="custom-input"
               v-model="form_values[config.id]" :placeholder="config.placeholder"  :type="config.type"   style="height: 20px;"
             ></b-form-input>
        <div @click="choose_path" class="l_button button_small button_colored"> Choose </div>

        <br>
    </div>


</template>
<script>

import FormInputMixin from "./FormInputMixin.vue"
import { icon_library } from "../icon_library.js"
import Vue from 'vue'


export default {
    name: 'FilePathTextBox',
    mixins: [FormInputMixin],
    props: {
         config: Object , 
        form_values: Object,
    },
    components: {},
    mounted() {
        if(this.form_values[this.config.id] === undefined && this.config.default_value ){
            Vue.set( this.form_values  , this.config.id  , this.config.default_value  )
        } 
    },
    data() {
        return {
            icon_library:icon_library,
        };
    },
    methods: {
        choose_path(){
            let file_path = window.ipcRenderer.sendSync('file_dialog',  this.config.path_type );
            
            if(file_path && file_path != 'NULL'){
                
                Vue.set(this.form_values , this.config.id , file_path)
            }  
        }
    },
}
</script>
<style>
</style>
<style scoped>

</style>