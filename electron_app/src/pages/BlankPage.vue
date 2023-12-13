<template>
</template>
<script>
const BlankPage ={
    name: 'BlankPage',
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

export default BlankPage;
BlankPage.title = "BlankPage"
BlankPage.icon = "file"
BlankPage.img_icon = require("../assets/imgs/page_icon_imgs/default.png")
BlankPage.home_category = undefined
BlankPage.description = "desc .. "
// add this to the always_on_pages to the PagesRouter

</script>
<style>
</style>
<style scoped>
</style>