<template>
    <div style="width: 100%; height :100% ; overflow:auto; padding:10px">
        <h2> Logs </h2>
        <p style="white-space: pre-line"> 
            {{app.app_state.logs}}
        </p>
    </div>
    
</template>
<script>
const Logs = {
    name: 'Logs',
    props: {app:Object, },
    components: {},
    mounted() {

    },
    data() {
        return {};
    },
    methods: {

    },
}

export default Logs;
Logs.title = "Logs"
Logs.icon = "file"
Logs.img_icon = require("../assets/imgs/page_icon_imgs/default.png")
Logs.home_category = undefined
Logs.hide_in_sidebar = true
Logs.sidebar_show = "never"
// add this to the always_on_pages to the PagesRouter

</script>
<style>
</style>
<style scoped>
</style>