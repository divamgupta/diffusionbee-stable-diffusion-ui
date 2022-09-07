<template>
    <div>
        <!-- <FormInput v-model="dd" input_type="textbox" question="name" :contraints="['non_empty','is_float' , 'maxval_50' ,'minval_25']"></FormInput> -->

        <FormInput v-for="form_el in form_entries_to_show"
            v-model="form_values[form_el.id]" 
            ref="form_element"
            :id="form_el.id" 
            :key="form_el.id"
            :input_type="form_el.input_type"
            :question="form_el.question" 
            :contraints="form_el.contraints" 
            :is_disabled="form_el.is_disabled || is_disabled"
            :options="form_el.options"
            >
        </FormInput>

        <!-- <p   v-if="!is_valid"> Invalid  </p> -->

    </div>

</template>
<script>

import FormInput from '../components_bare/FormInput.vue'


// TODO: add conditional rendering of some form elements based on values of other elements

export default {
    name: 'Form',
    props: {
        form_data : Array , // [ {...} , {} ]
        is_disabled : Boolean, 
    },
    components: {FormInput},
    mounted() {

    },
    data() {
        let ret = {
            form_values : {}
        };

        for( let form_el of this.form_data){
            ret.form_values[form_el.id] = form_el.value;
        }

        return ret;
    },
    methods: {
        is_render_condition_satisfied(render_condition){
            if( render_condition['comparator'] == "eq" && this.form_values[render_condition['lhs']] == render_condition['rhs']  )
                return true;
            else
                return false;
        },
        are_form_entry_conditions_safisfied(render_conditions){
            for( let render_condition of render_conditions ){
                if(!( this.is_render_condition_satisfied(render_condition) ))
                    return false ;
            }
            return true;
        }
    },

    watch : {
       
        'form_data': {
            handler: function() {
                for( let form_el of this.form_data){
                        this.form_values[form_el.id] = form_el.value;
                    }

            },
            deep: true
        } , 

    },

    computed : {

        form_entries_to_show(){

            let ret = [];
            for( let form_el of this.form_data){
                if( form_el.render_conditions  && form_el.render_conditions.length > 0 ){
                    if( this.are_form_entry_conditions_safisfied( form_el.render_conditions  ) ){
                        ret.push( form_el );
                    }
                } else {
                    ret.push( form_el );
                }
            }

            return ret;
        } , 

        is_valid(){
            console.log((this.$refs));

            //a simple hacky way t o make is_valid reactive wrt the form_values 
            let dd = '';
            dd;
            for( let form_el in this.form_values){
                dd += this.form_values[form_el];
            }

            if( this.$refs.form_element)
                for( let form_item of this.$refs.form_element ){
                    if(! form_item.is_input_valid()['is_valid'])
                        return false;
                }

            return true;

            
        }
    }
}
</script>
<style>
</style>
<style scoped>

</style>