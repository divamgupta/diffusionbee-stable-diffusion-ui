<template>
    <div style="width: 100%; height :100% ; overflow:auto; padding:30px">
        <div class="model_dialog"> 
            <h2 style="white-space: pre-line"> 
                To contact us, please send an email at :
                <br><br>
                diffusionbee@proton.me
            </h2> <br>            
            <p>We will get back to you as soon as possible</p>
        </div>
       
    </div>
    
</template>

<script>
const ContactUs = {
    name: 'ContactUs',
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

export default ContactUs;
ContactUs.title = "Contact Us"
ContactUs.icon = "file"
ContactUs.img_icon = require("../assets/imgs/page_icon_imgs/default.png")
ContactUs.home_category = undefined
ContactUs.hide_in_sidebar = true
ContactUs.sidebar_show = "never"
// add this to the always_on_pages to the PagesRouter

</script>
<style>
</style>

<style scoped>
.model_dialog{
    position: fixed;
    width: 250px ;
    height:170px;
    background: var(--options-input-bg );
    left: calc( 50% -  var(--sidebar-width ) /2 + 175px );
    top:50%;
     transform: translateY(-50%) translateX(-50%);
    z-index: 1000;
    padding:20px;
}

</style>