<template>
    <div class="img_container"> 

        <div v-for="option in zipped" :key="option.id"> 
            <div 
                :class="{ selected : form_values[config.id] == option.id }"  
                @click="form_values[config.id] = option.id" 
                style="float:left" > 
                    <img class="grid_img" src="https://hips.hearstapps.com/hmg-prod/images/dog-puppy-on-garden-royalty-free-image-1586966191.jpg?crop=0.752xw:1.00xh;0.175xw,0&resize=1200:*">
                    <span class="clear"></span>
                    <center> 
                        <p style="margin-bottom: 4px; zoom: 0.8">{{  option.val }}  </p>
                    </center>
                    
                </div>

                
        </div>
        <span class="clear"></span>
    </div>
</template>
<script>

import FormInputMixin from "./FormInputMixin.vue"
import { icon_library } from "../icon_library.js"
import Vue from "vue"

export default {
name: 'BetterSelector',
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
},
data() {
    return {
        icon_library:icon_library,
    };
},
methods: {

},

computed: {
    zipped(){
        let ret = []
        for(let i=0 ; i < this.config.options.length; i++ ){
            ret.push({id : this.config.options[i] , val :this.config.option_vals[i]  } )
        }
        return ret
    }
},

watch : {
   
   'config.options': {
       handler: function() {
          if(!this.config.options.includes(this.form_values[this.config.id])){
              if(this.config.options.length > 0){
                if( this.config.default_value != undefined && this.config.options.includes(this.config.default_value) ){
                    Vue.set(this.form_values,this.config.id , this.config.default_value )
                } else {
                    Vue.set(this.form_values,this.config.id , this.config.options[0] )
                }
                
              }
          }
       },
       deep: true
   } , 

},


}
</script>
<style>
</style>
<style scoped>

.selected > img {
    border-color: #3E7BFA;
    border-width: 1;
    border-style: solid;
}

span.clear { clear: left; display: block; }


.grid_img{
    height:93px;
    width:93px;
    margin:3px
}

.grid_img_five{
    height: 53px;
    width: 53px;
    margin:3px
}


.img_container{
    /* padding:10px; */
    margin-bottom: 20px;
}

</style>