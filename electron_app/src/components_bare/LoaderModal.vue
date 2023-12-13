@import '../assets/css/theme.css';
<template>
    <center>
        
        <div class="center loader_box">
            
            <h2 style=" margin-bottom:-5px   "  class="head ">{{loading_title}}</h2>
                <span v-if="loading_percentage <  0 "  style="zoom:0.35;   margin-left: 25px;   ">
                    <MoonLoader class="moonloader" color="#000000" size="50px"></MoonLoader>
            </span>
            
            <div style="margin-bottom:30px"></div>
            <b-progress v-if="loading_percentage >= 0 "  :value="loading_percentage" style="height: 10px;"></b-progress>

            <div style="margin-bottom:10px"></div>
            <p style="font-variant-numeric: tabular-nums;margin-bottom: 0px;">{{loading_desc}}
            <span v-if="remaining_times"><br>{{remaining_times}}</span>
            </p>
        </div>

    </center>
</template>
<script>
import MoonLoader from 'vue-spinner/src/MoonLoader.vue'


export default {
    name: 'LoaderModal',
    props: ['loading_percentage' ,'loading_desc' , 'loading_title', 'remaining_times'],
    components: {MoonLoader},
    mounted() {

    },
    data() {
        return {};
    },
    methods: {

    },
}
</script>
<style>


.loader_box{
    padding: 20px;
    /*height: calc(160px);*/
    border-radius: 12px 12px 12px 12px;
}



</style>
<style scoped>
    .center {
      margin: 0;
      position: fixed;
      top: 50%;
      left: 50%;
      -ms-transform: translate(-50%, -50%);
      transform: translate(-50%, -50%);
    }

    .disabled{
        pointer-events:none;
        opacity: 0.5;
    }

   


</style>
