<template>
    <div :id="rand_id" class="gallery_pane"  >


        <div class="inner_pane" :style="inner_pane_style">
            <GalleryImage  v-for="img in image_data_with_extra" :key="img.job_id"  :image_url="img.image_url" :aux_img_url="img.aux_img_url" :description="img.description" :img_w="img_w" :img_h="img_h" :done_percentage="img.done_percentage" :menu_items="menu_items" :on_menu_item_click="on_menu_item_click" :on_image_click="on_image_click" :params="img.params"> </GalleryImage>
        </div>

    </div>

</template>
<script>

import GalleryImage from "./GalleryImage.vue"


export default {
    name: 'GalleryPane',
    props: {
        n_imgs: Number,
        img_w:Number, 
        img_h:Number,
        image_data: Array, 
        always_fixed_col_size : Number, 

        menu_items : Array,
        on_menu_item_click : Function, 
        on_image_click:Function,

    },
    components: {GalleryImage},
    mounted() {
        this.ro = new ResizeObserver(this.on_resize);
        this.ro.observe( document.getElementById(this.rand_id) );
        this.on_resize()
    },
    
    beforeDestroy(){
        this.ro.disconnect()
    },

    computed: {
        image_data_with_extra(){

            let extra = [];
            for(let i=0; i< this.n_imgs - this.image_data.length ; i ++ ){
                extra.push({})
            }

            return this.image_data.concat(extra)
        }
    },

    data() {
        let d =  {

            rand_id : Math.random().toString(),
            inner_pane_style: {},
             
        };

        

        // for(let i=0 ; i < this.n_imgs ; i++){
        //     d['imgs'].push(i)
        // }

        return d; 
    },

    watch: {
        'image_data': {
            handler: function() {
                this.on_resize()
            },
            deep: false
        } , 
    }, 

    methods: {
        on_resize(){


            // let pane_h = document.getElementById(this.rand_id).offsetHeight
            let pane_w = document.getElementById(this.rand_id).offsetWidth
            let th = parseInt(getComputedStyle(document.body).getPropertyValue('--titlebar-height'))
            let pane_h =  window.innerHeight - 30 - th;

            let parent_aspect_ratio = (pane_h / pane_w);

            let MAX_ALLOWED_IMG_W = 350
            let n_col_max = Math.ceil(pane_w/MAX_ALLOWED_IMG_W)
            let n_row_max = Math.ceil(pane_h/((MAX_ALLOWED_IMG_W * this.img_h)/this.img_w))

            if( this.always_fixed_col_size ||  this.n_imgs > n_col_max * n_row_max  ){
               let n_col = n_col_max

               if(this.always_fixed_col_size)
                n_col = Math.ceil(pane_w/this.always_fixed_col_size)

               let col_size = 100 / n_col
               let col_size_pad = (5 / n_col)
               let col_size_s =  "calc("+col_size+"% - "+col_size_pad+"px  ) "
               col_size_s = col_size_s.repeat(n_col)

               this.inner_pane_style = { "grid-template-columns" : col_size_s , "width" : "100%"}
               document.getElementById(this.rand_id).style.height = "auto"
               return;
            }
            else{
                document.getElementById(this.rand_id).style.height = "calc( 100vh - var(--titlebar-height) - 30px )"
            }


            let n_imgs = Math.min(this.n_imgs, n_col_max * n_row_max)
            let best_aspect = 100000
            let best_col_row = {}
            for(let n=1 ; n<=Math.min(10 , n_imgs, n_col_max); n++){
                let nr = Math.ceil(n_imgs / n )
                let this_aspect = ( this.img_h *  nr ) / (this.img_w *  n)
                if (Math.abs(parent_aspect_ratio - this_aspect ) < Math.abs(parent_aspect_ratio - best_aspect )){
                    best_aspect = this_aspect;
                    best_col_row = {'row' : nr , "col" : n }
                }

            }

            let n_row = best_col_row.row
            let n_col = best_col_row.col


            // if(this.n_imgs == 4 && (n_row*n_col >=6) )
            // {
            //     n_row = 2;
            //     n_col = 2;
            // }

            if(n_row * n_col > this.n_imgs){
                let extra_space = n_row * n_col - 1 - this.n_imgs;
                if(extra_space >= (n_row - 1) ){
                    n_col -= 1;
                }
            }


            let canv_h = this.img_h *  n_row
            let canv_w = this.img_w *  n_col


            let aspect_ratio_string = canv_w + "/" + canv_h

            let col_size = 100 / n_col
            let col_size_pad = 5 / n_col
            let col_size_s =  "calc("+col_size+"% - "+col_size_pad+"px  ) "
            col_size_s = col_size_s.repeat(n_col)

            let row_size = 100 / n_row
            let row_size_pad = 5 / n_row
            let row_size_s =  "calc("+row_size+"% - "+row_size_pad+"px  ) "
            row_size_s = row_size_s.repeat(n_row)




            if((pane_h / pane_w) > (canv_h / canv_w)){
                // width should be 100%
                this.inner_pane_style = {"width" : "100%", "aspect-ratio" : aspect_ratio_string, "grid-template-columns" : col_size_s, "grid-template-rows" : row_size_s}
            } else {
                this.inner_pane_style = {"height" : "calc( 100vh - var(--titlebar-height) - 40px )", "aspect-ratio" : aspect_ratio_string, "grid-template-columns" : col_size_s, "grid-template-rows" : row_size_s}     
            }
        }, 
    },
}
</script>
<style>
</style>
<style scoped>


.gallery_pane{
/*    height: calc( 100vh - var(--titlebar-height) - 30px );*/
    width: calc( 100% - 30px);
    background-color: rgba(0,0,0,0.06);
    margin: 15px; 
    display: grid;
    place-items: center;
    border-radius: 5px;
    position: relative;

}



.inner_pane{
/*    background-color: green;*/
    object-fit: contain;

    padding-left:5px;
    padding-top:5px;
    
    display: grid;
/*    grid-template-columns: calc(50% - 2.5px  ) calc(50% - 2.5px );*/
/*    grid-gap:10px;*/


}


img{
/*    max-height: calc( ( 100vh - var(--titlebar-height) - 30px ) /2 - 20px );*/
}


</style>