<template>
    <div>
        <b-row style="margin-bottom: 10px ;">

            <b-col cols="12" v-if="input_type == 'label'">
                <label  style="padding-top: 6px; font-size: 13px; "><span v-if="get_color_from_text(question)" style="padding-right:15px; margin-right: 5px" :style="{'background-color':get_color_from_text(question) }" ></span>  {{remove_color_from_text(question)}}</label>

            </b-col>

            <b-col cols="4" v-if="input_type != 'label'">
                <label  style="padding-top: 6px; font-size: 13px; "><span v-if="get_color_from_text(question)" style="padding-right:15px; margin-right: 5px" :style="{'background-color':get_color_from_text(question) }" ></span>  {{remove_color_from_text(question)}}</label>

            </b-col>
            <b-col cols="8" v-if="input_type != 'label'">
                <!-- for text box input -->
                <input v-if="input_type == 'textbox'" style="font-size: 13px;" class="form-control"  @input="$emit('input',$event.target.value); on_input_changed()" :value="value" :disabled=is_disabled>
                <!-- for drop down input -->
                <select :disabled=is_disabled  v-if="input_type == 'dropdown'" style="font-size: 13px;"  class="form-select" @input="$emit('input',$event.target.value) ; on_input_changed()" :value="value"  >
                    <option v-for="option in options" :value="option" :key=
                    "option">{{option}}</option>
                </select>
                <!-- the boolean yes no input -->
                <div v-if="input_type == 'yes_no'">
                    <b-row>
                        <b-col cols="6">
                              <input v-model=value2 value="yes" @input="$emit('input',value2); on_input_changed()" class="form-check-input" type="radio" :name=id  :disabled=is_disabled >

                            Yes 
                        </b-col>
                        <b-col cols="6">
                              <input v-model=value2 value="no" @input="$emit('input',value2); on_input_changed()" class="form-check-input" type="radio" :name=id  :disabled=is_disabled>

                             No
                        </b-col>
                    </b-row>
                </div>
                <p style="color:red" v-if="invalid_prompt_str">{{invalid_prompt_str}}</p>
            </b-col>

            

        </b-row>
    </div>
</template>
<script>

import {get_color_from_text, remove_color_from_text} from "../utils.js"



function isItNumber(str) {
  return /^-?[0-9]+(e[0-9]+)?(\.[0-9]+)?$/.test(str);
}


export default {
    name: 'FormInput',
    props: {
        value : String , 
        id : String , 
        question: String,
        input_type: String, // textbox, dropdown, yes_no
        options: Array, // options for the dropdown
        is_disabled : Boolean , 
        contraints : Array , // list of all validation checks applied on the input element

    },
    components: {},
    mounted() {

    },
    data() {
        return {
            value2 : this.value , // for the initial value of the yes / no input 
            is_form_entry_fresh : this.value == "" // used to deterimine if the element is empty and value has not been changed yet
        };
    },
    methods: {
        on_input_changed(){
            this.is_form_entry_fresh = false;
        },
        get_color_from_text(t){
            return get_color_from_text(t)
        },

        remove_color_from_text(t){
            return remove_color_from_text(t)
        },
        is_input_valid(){
            for( let constraint of ( this.contraints|| []) ){
                if( constraint == "non_empty" ){
                    if( (! this.value) ||(this.value == ""))
                        return {
                            "is_valid" : false, 
                            "msg" : "The value cannot be empty"
                        }
                }
                else if( constraint == "is_int" ){
                    if( parseInt(this.value).toString() != this.value.toString()  ){
                        return{
                            "is_valid" : false, 
                            "msg" : "The value should be a valid integer"
                        }
                    }
                }
                else if( constraint == "is_float" ){
                    if(!isItNumber(this.value)){
                        return{
                            "is_valid" : false, 
                            "msg" : "The value should be a valid float number"
                        }
                    }
                }
                else if( constraint.startsWith("maxval_") ){
                    let max_val = parseFloat( constraint.split("maxval_")[1]);
                    if( parseFloat(this.value) > max_val){
                        return{
                            "is_valid" : false, 
                            "msg" : "The value should not greater than " + max_val
                        }
                    }
                }
                else if( constraint.startsWith("minval_") ){
                    let min_val = parseFloat( constraint.split("minval_")[1]);
                    if( parseFloat(this.value) < min_val){
                        return{
                            "is_valid" : false, 
                            "msg" : "The value should not less than " + min_val
                        }
                    }
                }
            }

            return {
                "is_valid" : true , 
                "msg" : ""
            }
        },
    },
    watch : {
        value : function(val){
            this.value2 = val; 
        } , 
    },

    computed : {
        invalid_prompt_str(){
            if(this.is_disabled)
                return "";
            if(this.is_form_entry_fresh)
                return "";
            return this.is_input_valid()['msg']  ;
        }
    }
}
</script>
<style>
</style>
<style scoped>
</style>