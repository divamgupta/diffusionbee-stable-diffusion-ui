<template>
    <div style=" width: 100%; height: 100%; padding:30px"> 
        <h2> Coming Soon </h2>
        
    </div>
</template>

<script>
const Training ={
    name: 'Training',
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


export default Training;
Training.title = "Training"
Training.icon = "file"
Training.img_icon = require("../assets/imgs/page_icon_imgs/training.png")
Training.home_category = "main"
Training.description = "Train a model on your own images using DreamBooth."
// add this to the always_on_pages to the PagesRouter

</script>
<style>
</style>
<style scoped>
</style>