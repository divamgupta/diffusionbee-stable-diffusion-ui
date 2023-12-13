<template>
    <div> 
        <div class="options_input" style="width: 100%;">
        <p style="white-space: pre-line; margin-bottom: 1px;" > {{ config.text }} </p>
        
    </div>
    <br> 
    </div>
    
</template>
<script>

import FormInputMixin from "./FormInputMixin.vue"
import { icon_library } from "../icon_library.js"


export default {
    name: 'OutputText',
    mixins: [FormInputMixin],
    props: {
         config: Object , 
        form_values: Object,
    },
    components: {},
    mounted() {
      
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