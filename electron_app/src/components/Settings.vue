<template>
    <div  class="animatable_content_box ">

        <div  v-if="!is_custom_model_loading">
            <h1>Settings</h1>
            <br>
            <h2>General Settings</h2>

            <br><hr>
            <div class="l_button button_colored" style="float:right" @click="add_model"  >Add New Model</div>
            <h2>Custom Models</h2>
            
            <!-- <br> -->
            <hr> 
            <div v-for="model in Object.values(this.app_state.app_data.custom_models)" :key="model.name">
                <div class="l_button" @click="delete_model(model.name)" style="float:right">Remove</div>
                <p> Name : {{model.name}} </p>
                <p> Path : {{model.orig_path}} </p>
                <hr> 
            </div>
        </div>
        <div v-else>
            <LoaderModal :loading_percentage="-1" loading_title="Importing model"></LoaderModal>
        </div>

    </div>
</template>
<script>
import LoaderModal from '../components_bare/LoaderModal.vue'
import Vue from 'vue'


export default {
    name: 'Settings',
    props: {
        app_state : Object , 
    },
    components: {LoaderModal},
    mounted() {

    },
    data() {
        return {
            is_custom_model_loading:false,
        };
    },
    methods: {
        delete_model(k){
            let model_path = this.app_state.app_data.custom_models[k].path;
            window.ipcRenderer.sendSync('delete_file',  model_path );
            Vue.delete( this.app_state.app_data.custom_models , k );
        },
        add_model(){
            let that = this;
            
            let pytorch_model_path = window.ipcRenderer.sendSync('file_dialog',  "ckpt_file" );
            if(!pytorch_model_path)
                return;

            if(pytorch_model_path == "NULL")
                return;

            let model_name = pytorch_model_path.replaceAll("\\" , "/").split("/");
            model_name = model_name[model_name.length - 1].split(".")[0]


            if(model_name.trim() == ""){
                alert("Put non empty model name");
                return;
            }

            if(that.app_state.app_data.custom_models[model_name]){
                alert("this model name "+ model_name +" already exists")
                return;
            }

            that.is_custom_model_loading = true
            window.ipcRenderer.invoke('add_custom_pytorch_models', pytorch_model_path , model_name ).then((result) => {
                that.is_custom_model_loading = false
                if(result.success){
                    Vue.set( that.app_state.app_data.custom_models , model_name ,  {"name":model_name , "path": result.model_path, "orig_path" : pytorch_model_path }  );
                } else {
                    alert("Error " + result.error )
                }
                
            })
        }
    },
}
</script>
<style>
</style>
<style scoped>
</style>