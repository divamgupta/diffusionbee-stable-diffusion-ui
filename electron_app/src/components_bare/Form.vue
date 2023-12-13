<template>
    <div>
        <!-- <FormInput v-model="dd" input_type="textbox" question="name" :contraints="['non_empty','is_float' , 'maxval_50' ,'minval_25']"></FormInput> -->

        <ResolveInputComponent v-for="form_el in filtered_form_data"
            ref="form_element"
            :form_values="form_values" 
            :config="form_el"
            :key="form_el.id"
            >
        </ResolveInputComponent>

        <!-- <p   v-if="!is_valid"> Invalid  </p> -->

    </div>

</template>
<script>

import ResolveInputComponent from './inputform/ResolveInputComponent.vue'
import Vue from 'vue'


// TODO: add conditional rendering of some form elements based on values of other elements

export default {
    name: 'Form',
    props: {
        form_data : Array , // [ {...} , {} ]
        is_disabled : Boolean, 
        form_values: Object,
        tags: Array,
        form_save_key : String, 
        
    },
    components: {ResolveInputComponent},
    mounted() {
        if(this.form_save_key){
            this.keys_to_save = this.collect_savable_keys()

            for( let key of this.keys_to_save ){
                let v = window.localStorage.getItem(this.form_save_key + "__" + key  );
                if(v != null && v != undefined && v != "undefined" && v != "null"){
                    Vue.set(this.form_values , key , v )
                }
            }

        }

        this.has_mounted = true;

    },
    data() {
        let ret = {
            // form_values : {}
            has_mounted : false,
        };

        // for( let form_el of this.form_data){
        //     let first_option = undefined
        //     if(form_el.options && form_el.options.length > 0 ){
        //         first_option = form_el.options[0]
        //     }
        //     ret.form_values[form_el.id] = form_el.value || first_option;
        // }

        return ret;
    },
    methods: {

        collect_savable_keys(elements){

            if(!elements){
                elements = this.form_data;
            }

            let ret = []
            for( let form_el of elements){
                if( form_el.is_persistant ){
                    ret.push(form_el.id)
                }
                if(form_el.children && form_el.children.length > 0){
                    ret = ret.concat(this.collect_savable_keys(form_el.children))
                }
            }

            return ret;
        },

        reset_to_default(elements){
            if(!elements){
                elements = this.form_data;
            }
            for( let form_el of elements){
                if( this.form_values[form_el.id] != undefined  && form_el.default_value ){
                    Vue.set(this.form_values , form_el.id , form_el.default_value  )
                } else if(this.form_values[form_el.id] != undefined){
                    this.form_values[form_el.id] = ""
                }

                if(form_el.children && form_el.children.length > 0){
                    this.reset_to_default(form_el.children)
                }
            }

        },

        is_render_condition_satisfied(render_condition){
            if( render_condition['comparator'] == "eq" && this.form_values[render_condition['lhs']] == render_condition['rhs']  )
                return true;
            else
                return false;
        },
        are_form_entry_conditions_safisfied(render_conditions){ // see if ALL of them are satisfied
            for( let render_condition of render_conditions ){
                if(( this.is_render_condition_satisfied(render_condition) ))
                    return true ;
            }
            return false;
        },

        are_form_entry_conditions_safisfied_AND(render_conditions){ // see if ALL of them are satisfied
            for( let render_condition of render_conditions ){
                if(!( this.is_render_condition_satisfied(render_condition) ))
                    return false ;
            }
            return true;
        },

        post_processed_form_outputs(elements , ret ){

            if(!elements){
                elements = this.filtered_form_data;
            }

            if(!ret){
                ret = {}
            }

            for(let form_el of elements){
                if(this.form_values[form_el.id] != undefined){
                    if(form_el.output_type){
                        if(form_el.output_type == 'int'){
                            ret[form_el.id] = Math.round(Number(this.form_values[form_el.id]))
                        } else if(form_el.output_type == 'float'){
                            ret[form_el.id] = Number(this.form_values[form_el.id])
                        }else if(form_el.output_type == 'str'){
                            ret[form_el.id] = this.form_values[form_el.id].toString()
                        }else if(form_el.output_type == 'bool'){
                            if(this.form_values[form_el.id] == "true" || this.form_values[form_el.id].toString().toLowerCase() == "yes"){
                                ret[form_el.id] = true
                            } else if(this.form_values[form_el.id] == "false" || this.form_values[form_el.id].toString().toLowerCase() == "no"){
                                ret[form_el.id] = false
                            } else if(this.form_values[form_el.id] ){
                                ret[form_el.id] = true
                            } else {
                                ret[form_el.id] = false
                            }
                        }
                    } else {
                        ret[form_el.id] = this.form_values[form_el.id]
                    }
                    
                }

                if(form_el.children && form_el.children.length > 0){
                    this.post_processed_form_outputs(form_el.children , ret )
                }

            }

            return ret;

        } , 

        filter_form_data(form_data){
            let ret = []
            let tags = this.tags || []
            for( let form_el of form_data){
                let is_allowed = true;

                if(form_el.include_in != undefined && form_el.include_in.length > 0 ){
                    // if any tags then allow else dissallow
                    if( (tags.filter(value => form_el.include_in.includes(value))).length > 0 ){
                        is_allowed = true
                    } else {
                        is_allowed = false
                    }
                }

                if(form_el.cond_include_in != undefined && form_el.cond_include_in.length > 0  ){
                    if(this.are_form_entry_conditions_safisfied(form_el.cond_include_in)){
                        is_allowed = true 
                    } 
                }

                if(form_el.cond_include_in_AND != undefined && form_el.cond_include_in_AND.length > 0  ){
                    if(this.are_form_entry_conditions_safisfied_AND(form_el.cond_include_in_AND)){
                        is_allowed = true 
                    } 
                }

                if(form_el.exclude_in != undefined && form_el.exclude_in.length > 0 ){
                    if( (tags.filter(value => form_el.exclude_in.includes(value))).length > 0 ){
                        is_allowed = false
                    } 
                }

                if(form_el.include_in_AND != undefined  ){
                    for(let t of form_el.include_in_AND){
                        if( ! tags.includes(t) ){
                            is_allowed = false
                        }
                    }
                }

                if(is_allowed){
                    if(form_el.children){
                        let filtered_children = this.filter_form_data(form_el.children)
                        let new_form_el = {}
                        for(let k in form_el){
                            new_form_el[k] = form_el[k]
                        }
                        new_form_el['children'] = filtered_children
                        ret.push(new_form_el)
                    } else {
                        ret.push(form_el)
                    }
                    
                }
                    
            }
            return ret
        }


    },

    watch : {
       
        'form_values': {
            handler: function() {
                if(!this.has_mounted)
                    return;
                if(this.form_save_key){
                    for( let key of this.keys_to_save ){
                        window.localStorage.setItem(this.form_save_key + "__" + key , this.form_values[key]);
                    }
                }
            },
            deep: true
        } , 

    },

    computed : {

        filtered_form_data(){ //TODO make it recursive //TODO also allow dymamic filters
            return this.filter_form_data(this.form_data)
        },

        is_valid(){

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