<template>
    <div class="generation_gallery_div" :id="div_id">

        <div v-if="groups_with_non_zero_imgs.length == 0 " style="width:30% ; height: 30% ; margin-left:35%; top:50% ; transform: translateY(50%);">
            <!-- <img src="../assets/imgs/blank_illus4_dark.png" style="opacity:0.3; width: 100%; height: 100%;  object-fit: contain;">  -->

            <picture >
                <source srcset="../assets/imgs/blank_illus4_dark.png" media="(prefers-color-scheme: dark)">
                <img  style="opacity:0.3; width: 100%; height: 100%;  object-fit: contain;" src="../assets/imgs/blank_illus4.png">
            </picture>

            <center style="opacity: 0.5">
                <h2 style="margin-top: 20px;"> No images to display </h2>
                <p > Enter a prompt to generate images using AI.</p>
            </center>
            
        </div>


        <GalleryPane v-else v-for="group in groups_with_non_zero_imgs"  :key="group.group_id" :n_imgs="group.num_imgs" :img_w="group.img_width" :img_h="group.img_height" :image_data="group.imgs" :menu_items="menu_items" :on_menu_item_click="on_image_menu_item_click" :on_image_click="on_image_click"> </GalleryPane>
    </div>
</template>
<script>

import GalleryPane from "../components_bare/GalleryPane.vue"
import Vue from 'vue'
import {image_manu_functions} from "./image_menu_functions.js"
import {open_popup} from "../utils"

export default {
    name: 'GenerationGallery',
    props: {
        app: Object,
        n_to_keep: Number,
        menu_items_skip: Array,
    },
    components: {GalleryPane},
    mounted() {

    },
    data() {

        let menu_items = []
        for(let fn of Object.keys(image_manu_functions)){
            if( !((this.menu_items_skip || []).includes(fn)))
                menu_items.push({id: fn , text: image_manu_functions[fn].text })
        }

        return {
            groups : [],
            menu_items :menu_items,
            div_id: Math.random().toString(),
        };
    },
    computed: {
        groups_with_non_zero_imgs(){
            let ret = []
            for(let group of this.groups){
                if(group.num_imgs > 0 )
                    ret.push(group)
            }
            return ret;
        }
    },
    methods: {

        scroll_to_top(){
            document.getElementById(this.div_id).parentNode.scrollTo({ top: 0, behavior: 'smooth' });
        },

        on_image_menu_item_click(menu_item_id , image_item_data){
            image_manu_functions[menu_item_id](this.app , image_item_data )
        },

        on_image_click(image_item_data){
            open_popup('file://' + image_item_data.image_url)
        },

        add_group(group){
            this.groups.unshift(group);

            this.clear_old_groups( this.n_to_keep || 10)

        }, 

        clear_old_groups(n_to_keep){

            n_to_keep = n_to_keep||0

            let idx_to_rm = []
            let n_finish = 0

            // delete groups beyond last 10 finished and the ones with zero imgs 
            for(let i = 0 ; i < this.groups.length ; i++){
                let group = this.groups[i]
                let is_group_finished = true 
                
                for(let im of group.imgs){
                    if(!im.image_url){
                        is_group_finished = false
                    }
                }

                if(is_group_finished && group.imgs.length > 0 ){
                    n_finish += 1
                }

                if(group.imgs.length == 0)
                    idx_to_rm.push(i)
                else if(n_finish > n_to_keep)
                    idx_to_rm.push(i)

            }


            for (let i = idx_to_rm.length -1; i >= 0; i--)
                this.groups.splice(idx_to_rm[i],1);
        },

        delete_group(group_id){
            for(let i=0; i <   this.groups.length ; i++){
                if(this.groups[i].group_id == group_id){
                    this.groups.splice(i, 1);
                    break
                }
            }
        } , 

        update_group(new_group_data){
            for(let i=0 ; i < this.groups.length ; i++ ){
                if(this.groups[i].group_id == new_group_data.group_id){
                    new_group_data = JSON.parse(JSON.stringify(new_group_data))
                    Vue.set(this.groups , i , new_group_data ) 
                }
            }
        },

        get_group(group_id){
            for(let i=0 ; i < this.groups.length ; i++ ){
                if(this.groups[i].group_id == group_id){
                    return this.groups[i]
                }
            }
        }, 

        clear_all(){
            Vue.set(this, "groups" , [])
        }

    },
}
</script>
<style>
</style>
<style scoped>
    

</style>