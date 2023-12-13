<template>

   <div style="margin-left: 80px; padding-bottom:10px"> 
        <!-- <input  :id="rand_id" type="checkbox"  @input="set_val()"> -->
        <label class="switch" >
            <input  :id="rand_id"  type="checkbox"  @input="set_val()" >
            <span class="toggle round"></span>
        </label>

  </div> 

</template>
<script>

import FormInputMixin from "./FormInputMixin.vue"
import Vue from 'vue'

export default {
    name: 'Checkbox',
    mixins: [FormInputMixin],
    props: {
        config: Object , 
        form_values: Object,
    },
    components: {},
    mounted() {

       if(this.form_values[this.config.id] === undefined){
            Vue.set( this.form_values  , this.config.id  , this.config.default_value || false )
        } 
        
        this.set_el()
    },
    data() {
        if(this.form_values[this.config.id] == 'true'){
            Vue.set(this.form_values , this.config.id , true)
        }
        if(this.form_values[this.config.id] == 'false'){
            Vue.set(this.form_values , this.config.id , false)
        }

        return {
            rand_id : Math.random()
        };
    },
    methods: {
        set_val() {
            let el = document.getElementById(this.rand_id)
            let value = el.checked
            Vue.set(this.form_values , this.config.id , value)
        }, 
        set_el(){

            if(this.form_values[this.config.id] == 'true'){
                Vue.set(this.form_values , this.config.id , true)
            }
            if(this.form_values[this.config.id] == 'false'){
                Vue.set(this.form_values , this.config.id , false)
            }   

            let el = document.getElementById(this.rand_id)
            let val = this.form_values[this.config.id]
           
            if(val == true  ){
               el.checked = true
            }
            else{
               el.checked = false
            }
        }
    },

    computed:{

        cur_val(){
            return this.form_values[this.config.id]
        }
    } , 

    watch: {
        'cur_val' : {
            handler: function() {
              this.set_el()
            },
            deep: false
        } , 
    }

}
</script>
<style>
</style>
<style scoped>

.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 30px;
  zoom:0.7;
}

.switch input { 
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--input-form-el-color);
  -webkit-transition: .4s;
  transition: .4s;
}

.toggle:before {
  position: absolute;
  content: "";
  height: 22px;
  width: 23px;
  left: 5px;
  bottom: 4px;
  background-color: white;
  -webkit-transition: .4s;
  transition: .4s;
}

input:checked + .toggle {
  background-color: #3E7BFA;
}


input:checked + .toggle:before {
  transform: translateX(27px);
}

.toggle.round {
  border-radius: 34px;
}

.toggle.round:before {
  border-radius: 50%;
}


</style>