<script>

function isItNumber(str) {
  return /^-?[0-9]+(e[0-9]+)?(\.[0-9]+)?$/.test(str);
}


export default {
    data: () => ({
      is_form_entry_fresh : true 
    }),
    methods: {
        
        on_input_changed(){
            this.is_form_entry_fresh = false;
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
       
        'value': {
            handler: function() {
               this.on_input_changed()
            },
            deep: true
        } , 

    },


    computed: {
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