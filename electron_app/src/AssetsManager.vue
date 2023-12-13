<template>
    <div>
    </div>
</template>
<script>

import Vue from 'vue'

// import { contextBridge, ipcRenderer } from 'electron'

// contextBridge.exposeInMainWorld('ipcRenderer', ipcRenderer)
// contextBridge.exposeInMainWorld('ipcRenderer_on', ipcRenderer.on)


function download_file(url, dest, md5_hash , onProgress, onSuccess, onError) {
    const downloadId = Date.now().toString() + Math.random().toString().substr(2);
    window.bind_ipc_download_on(downloadId, function(m){
        // progresss
        onProgress(m);
    }, function(file_hash){
        // sucdesss 
        if(md5_hash == file_hash){
            onSuccess(file_hash)
        } else{
            onError("failed to match checksum")
        }
        window.unbind_ipc_download_on(downloadId)
        
    }, function(m){
        // error 
        window.unbind_ipc_download_on(downloadId)
        onError(m)
    } )
    window.ipcRenderer.send('download-file', url, dest, downloadId);
}


export default {
    name: 'AssetsManager.vue',
    props: {},
    components: {},
    mounted() {

    },
    data() {
        let downloaded_assets_storage = window.ipcRenderer.sendSync('load_data' , 'downloaded_assets.json'); // get from local storage
        let local_assets_storage = window.ipcRenderer.sendSync('load_data' , 'locally_loaded_assets.json'); // get from local storage

        return {
            downloaded_assets: downloaded_assets_storage ,
            local_assets: local_assets_storage , 
            downloading: {} , // id , status : done/downloading/error/not_downloaded , progress , hash, 
            //TODO : ignore the certificate but see the signature
        };
    },

    watch:{
         'downloaded_assets': {
            handler: function(new_value) {
                window.ipcRenderer.sendSync('save_data', new_value , 'downloaded_assets.json');
            },
            deep: true
        } , 

         'local_assets': {
            handler: function(new_value) {
                window.ipcRenderer.sendSync('save_data', new_value , 'locally_loaded_assets.json');
            },
            deep: true
        } , 

    },

    computed: {
        all_avail_assets(){
            return { // update the dict
              ...this.downloaded_assets ,
              ...this.local_assets
            }
        }
    },

    methods: {

        add_local_asset(asset_details, cb ){
            asset_details = JSON.parse(JSON.stringify(asset_details))
            let that = this;
            let asset_id = asset_details.id;
            let asset_filename = asset_details.filename;

            if(asset_details.post_process && asset_details.post_process == 'convert_sd_to_tdict' ){
                asset_details.post_process_params = asset_details.post_process_params || {}
                let model_name = asset_id + "_" + asset_filename
                window.ipcRenderer.invoke('add_custom_pytorch_models', asset_details.asset_path_raw,  model_name, asset_details.post_process_params ).then((result) => {
                    that.is_custom_model_loading = false
                    if(result.success){
                            
                            asset_details.model_meta_data = asset_details.model_meta_data || {}
                            asset_details.asset_path = result.model_path 

                            asset_details.model_meta_data  = { // update the dict
                              ...asset_details.model_meta_data ,
                              ...result.metadata
                            }

                          Vue.set( that.local_assets , asset_id , asset_details)
                          cb("success", asset_details)
                    } else {
                        cb("error" , result.error)
                    }
                })
            } else {
                 Vue.set( that.local_assets , asset_id , asset_details)
            }


        }, 

        get_downloaded_asset_path(asset_id){
            return (this.downloaded_assets[asset_id] || this.local_assets[asset_id] || {}).asset_path
        },

        get_downloaded_asset(asset_id){
            return (this.downloaded_assets[asset_id] || this.local_assets[asset_id] )
        },

        delete_asset(asset_id){
            
            let asset_details = this.downloaded_assets[asset_id] || this.local_assets[asset_id] || this.downloading[asset_id] 
            
            Vue.delete(this.downloaded_assets, asset_id );
            Vue.delete(this.downloading, asset_id );
            Vue.delete(this.local_assets, asset_id );

            window.ipcRenderer.sendSync('delete_file',  asset_details.asset_path );
        },

        download_asset(asset_details){
            asset_details = JSON.parse(JSON.stringify(asset_details))
            let that = this;
            let asset_id = asset_details.id;
            let asset_hash = asset_details.md5;
            let asset_filename = asset_details.filename;

            if(this.downloaded_assets[asset_id]){
                return;
            }
            if(this.downloading[asset_id] && this.downloading[asset_id].status == 'done' ){
                return;
            }

            // const path = require('path');
            let dir = window.ipcRenderer.sendSync('get_assets_dir') 
            // let dest_path = path.join(dir, asset_id + "_" + asset_filename)
            let dest_path =  dir + "/" +  asset_id + "_" + asset_filename
            asset_details.asset_path_raw = dest_path

            let convert_to_tdict = false;

            if(asset_details.post_process && asset_details.post_process == 'convert_sd_to_tdict' ){
                convert_to_tdict = true
            }

            function on_progress(progress){
                if(convert_to_tdict)
                    progress = Math.round(progress*0.9)
                console.log("downlaod progress "+ progress)
                Vue.set( that.downloading[asset_id] , 'progress' , progress)
            }

            function on_success(){

                if(convert_to_tdict){

                        asset_details.post_process_params = asset_details.post_process_params || {}
                        asset_details.post_process_params.delete_origional_always = true;
                        let model_name = asset_id + "_" + asset_filename
                        window.ipcRenderer.invoke('add_custom_pytorch_models', asset_details.asset_path_raw,  model_name, asset_details.post_process_params ).then((result) => {
                            that.is_custom_model_loading = false
                            if(result.success){
                                // todo update the metadata 
                                asset_details.model_meta_data = asset_details.model_meta_data || {}
                                asset_details.asset_path = result.model_path 

                                asset_details.model_meta_data  = { // update the dict
                                  ...asset_details.model_meta_data ,
                                  ...result.metadata
                                }

                                Vue.set( that.downloading[asset_id] , 'status' , 'done')
                                Vue.set( that.downloaded_assets , asset_id , asset_details)

                            } else {
                                Vue.set( that.downloading[asset_id] , 'status' , 'error')
                                Vue.set( that.downloading[asset_id] , 'error' , result.error.slice(-30)  )
                            }
                        })
                } else {
                    asset_details.asset_path = asset_details.asset_path_raw
                    Vue.set( that.downloading[asset_id] , 'status' , 'done')
                    Vue.set( that.downloaded_assets , asset_id , asset_details)
                }

            }

            function on_error(error ){
                Vue.set( that.downloading[asset_id] , 'status' , 'error')
                Vue.set( that.downloading[asset_id] , 'error' , error )
            }

            Vue.set( that.downloading  , asset_id , asset_details)
            Vue.set( that.downloading[asset_id] , 'status' , 'downloading')

            download_file( asset_details.url , dest_path , asset_hash  , on_progress , on_success ,  on_error )

        }
            
    },
}
</script>
<style>
</style>
<style scoped>
</style>