<template>
    <center>
        
        <div class="center loader_box">
            
            <h2 style=" margin-bottom:-5px   "  class="head ">{{loading_title}}</h2>
                <span v-if="loading_percentage <  0 "  style="zoom:0.35;   margin-left: 25px;   ">
                    <MoonLoader color="#000000" size="50px"></MoonLoader>
            </span>
            
            <div style="margin-bottom:30px"></div>
            <b-progress v-if="loading_percentage >= 0 "  :value="loading_percentage" style="height: 10px;"></b-progress>

            <div style="margin-bottom:10px"></div>
            <p>{{loading_desc}}</p>
        </div>

    </center>
</template>
<script>
import MoonLoader from 'vue-spinner/src/MoonLoader.vue'


export default {
    name: 'LoaderModal',
    props: ['loading_percentage' ,'loading_desc' , 'loading_title'],
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
</style>
<style scoped>
    .center {
      margin: 0;
      position: absolute;
      top: 50%;
      left: 50%;
      -ms-transform: translate(-50%, -50%);
      transform: translate(-50%, -50%);
    }

    .disabled{
        pointer-events:none;
        opacity: 0.5;
    }

    .loader_box{
       padding: 20px;
        background-color: rgba(255,255,255,0.9);
        /*height: calc(160px);*/
        border-radius: 12px 12px 12px 12px;
    }

</style>