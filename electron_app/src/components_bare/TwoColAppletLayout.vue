<template>
    <div class="applet_container" style="width:100% ; height:100%;  ">
        
        <div class="left_controls" style="height: 100%; max-width: 350px;   ">
            <div class="left_controls_inputs " style="padding: 20px">
                <slot name="input_workspace"></slot>
            </div>
           
            <div style="padding:10px;">
                <slot name="input_buttons"></slot>
            </div>

        </div>

        <div class="right_workpace">
            <slot name="output_workpace"></slot>
        </div>
        
    </div>
</template>
<script>

export default {
    name: 'TwoColAppletLayout',
    props: {
        app:Object, 
    },
    components: {   },
    mounted() {

    },
    data() {
        return {
           
        };
    },
    methods: {
        
    },  
}
</script>
<style>
</style>
<style scoped>

.applet_container{
  display: flex;
  flex-wrap: wrap;
   justify-content: center;
   align-items: center;

}

.right_workpace{
    height: 100%;
    width: calc( 100% - 350px);
    overflow-y: auto;
}

.left_controls{
    border-width: 0px;
    border-right-width: 1px;
    border-style: solid;
    border-color: var( --thin-border-color);
    height: 100%;

}

.left_controls_inputs{
    max-height: calc( 100% - 50px );
    overflow-y: auto;
    width: 100%;

}


</style>