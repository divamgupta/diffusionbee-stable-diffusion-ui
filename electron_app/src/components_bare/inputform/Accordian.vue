<template>
    <div style="margin-left:-15px; margin-right:-15px; margin-bottom: -10px;">
         <div class="options_title_box" v-b-toggle="'collapse-'+rand_no"  style="width: 100%; background-color: rgba(0,0,0,0.1); padding:9px; display:block">
             <span  >{{config.title}}</span> <span style="float:right; margin-right:4px"  >+ </span>
        </div>
        
        <b-collapse :id="'collapse-'+rand_no">
            <div style="border-width: 1px; border-color:rgba(0,0,0,0.1); border-style: solid; padding: 15px">
             
             <ResolveInputComponent
                 v-for="child_config in config.children"
                 :form_values="form_values" 
                 :config="child_config"
                 :key="child_config.id"
            > </ResolveInputComponent>
        </div>
    </b-collapse>
        
        
        <br>
    </div>

</template>
<script>

import ResolveInputComponent from "./ResolveInputComponent.vue"

export default {
    name: 'Accordian',
    props: {
        config: Object , 
        form_values: Object,
    },
    components: {'ResolveInputComponent':ResolveInputComponent},
    mounted() {

    },
    data() {
        return {
            rand_no : Math.random().toString()
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