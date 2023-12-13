<template>

    <div class="main_container">

        <div v-for="category in categories" :key="category[0]"> 
            <h2> {{category[1]}} </h2>
            <div class="icon_container">
                <div v-for="item in all_icons(category[0]) " 
                    :key="item.id" 
                    v-bind:style="{ 'background-image': 'url(' +( item.img_icon || default_img )+ ')' }"
                    @click="app.functions.switch_page(item.id)" 
                    class="select_app"> 
                    <div class="select_app_desc"> 
                        <h2>  {{item.text}}</h2> 
                        <p> {{item.description}} </p>
                        <div class="l_button button_colored" style="margin-top: 10px;"> Open </div>
                    </div> 
                </div>
            
            </div>

            <br> 
        </div>
        <hr>
       

    </div>

    
</template>
<script>
const Home ={
    name: 'Home',
    props: {app:Object, },
    components: {},
    mounted() {

    },
    data() {
        return {

            categories: [
                ["main" , "All AI Tools"],
                ["pages" , "Pages"],
                ["misc" , "Miscellaneous"],
            ]
        };
    },
    methods: {
        all_icons(category){
            let ret = []
            let items = (this.app.all_pages_ready ) ?  this.app.$refs.router.all_applet_items : [];
            for(let item of items){
                if(item.home_category == category)
                    ret.push(item)
            }
            return ret;
        }, 
    },
    computed: {
        

        default_img(){
            return require("../assets/imgs/page_icon_imgs/default1.png")
        }
    }
}

export default Home;
Home.title = "Home"
Home.icon = "home"
Home.home_category = undefined
Home.sidebar_show = "always"
// add this to the always_on_pages to the PagesRouter

</script>
<style>
</style>
<style scoped>

.main_container{
    padding: 20px;
    width: 100%;
    height: 100%;
    overflow: auto;
}

.icon_container{
    display: flex;
   flex-wrap: wrap;
}

.select_app{
    width:280px;
    height: 230px;
    margin: 5px;
    background-size: contain;
    background-color: var(--sidebar-color);
    position: relative;
}

@media only screen and (max-width: 1730px) {
  .select_app {
    width : calc(20% - 10px)
  }
}



@media only screen and (max-width: 1430px) {
  .select_app {
    width : calc(25% - 10px)
  }
}


@media only screen and (max-width: 1200px) {
  .select_app {
    width : calc(33% - 10px)
  }
}




.select_app_desc{
    background-color: var(--sidebar-color); ;
    padding: 15px;
    position: absolute;
    bottom: 0;
    width: 100%;
}

.select_app_desc > p{
    margin-bottom: 3px;
}


</style>