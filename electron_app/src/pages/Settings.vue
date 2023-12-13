<template>
    <div style="width:100%; height:100%; overflow: auto; padding: 20px;">
        
     <h1>Settings</h1>
        <br>
       <h2>General Settings</h2>
        <br>
        <div class="setting_box">
        <div class="settings_left">
        <h3>Notification sound</h3>
        <p>To play a notification sound when generation of an image is completed</p>
        </div>
        
        <div style="float:right;margin-right: 9px;align-self: center;" >
            <label class="switch">
                <input type="checkbox" v-model="app.app_state.app_data.settings.notification_sound" checked>
                <span class="toggle round"></span>
            </label>
        </div>
        </div>
        <hr>


    </div>
</template>
<script>
const Settings ={
    name: 'Settings',
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

export default Settings;
Settings.title = "Settings"
Settings.icon = "tools"
Settings.img_icon = require("../assets/imgs/page_icon_imgs/settings.png")
Settings.home_category = "pages"
Settings.hide_in_sidebar = true

// add this to the always_on_pages to the PagesRouter

</script>
<style>
</style>
<style scoped>

.setting_box{
    display: flex;
    flex-direction: row;
}

.settings_left{
    flex: 1 1 auto;
}

.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 30px;
}

.switch input { 
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  -webkit-transition: .4s;
  transition: .4s;
}

.toggle:before {
  position: absolute;
  content: "";
  height: 22px;
  width: 23px;
  left: 5px;
  bottom: 4px;
  background-color: white;
  -webkit-transition: .4s;
  transition: .4s;
}

input:checked + .toggle {
  background-color: #3E7BFA;
}


input:checked + .toggle:before {
  transform: translateX(27px);
}

.toggle.round {
  border-radius: 34px;
}

.toggle.round:before {
  border-radius: 50%;
}



</style>