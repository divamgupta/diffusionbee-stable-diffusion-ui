<template>
    <div>
        <div v-if="is_downloaded" >
             <!-- <p>Downloaded </p> -->
             <div @click="deletee" class="l_button button_colored">Delete</div>

        </div>

        <div v-else-if="is_downloading" class="l_button">
             <b-progress :value="app.assets_manager.downloading[asset_details.id].progress" style="height: 10px; width:200px"></b-progress>
             {{app.assets_manager.downloading[asset_details.id].progress || 0  }}%
        </div>

        <div v-else-if="is_error"  >
            <p style="color:red; margin-bottom:5px">  Error : {{app.assets_manager.downloading[asset_details.id].error}} </p>
            <div @click="downloadd" class="l_button button_colored">Download Again</div>
        </div>


        <div v-else class="l_button button_colored" @click="downloadd">Download</div>
        
    </div>
</template>
<script>
export default {
    name: 'Downloadutton',
    props: { app:Object , asset_details:Object },
    components: {},
    mounted() {

    },
    data() {
        return {};
    },
    methods: {
        downloadd(){
            this.app.assets_manager.download_asset(this.asset_details)
        }, 
        deletee(){
            this.app.assets_manager.delete_asset(this.asset_details.id)
        }
    },

    computed: {
        is_downloaded(){
            let asset_id = this.asset_details.id

            if(this.asset_details.is_locally_imported)
                return true;

            if(this.app.is_mounted && this.app.assets_manager.downloaded_assets[asset_id] && this.app.assets_manager.downloaded_assets[asset_id].status == 'done'){
                return true
            } else {
                return false
            }
        } , 
        is_downloading(){
            let asset_id = this.asset_details.id
            return (this.app.is_mounted && this.app.assets_manager.downloading[asset_id]&& this.app.assets_manager.downloading[asset_id].status == 'downloading')
        } , 
        is_error(){
            let asset_id = this.asset_details.id
            return (this.app.is_mounted && this.app.assets_manager.downloading[asset_id]&& this.app.assets_manager.downloading[asset_id].status == 'error')
        }
    }
}
</script>
<style>
</style>
<style scoped>
</style>