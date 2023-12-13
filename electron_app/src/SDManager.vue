<template>
    <div></div>
</template>
<script>

import Vue from 'vue'

export default {
    name: 'SDManager',
    props: {
        app : Object, 
    },
    components: {},
    mounted() {

    },
    data() {
        return {
            queue : {
                groups_todo : [],
                current_group : undefined,
            } , 
            group_gallery_mapping : {} , 
            worker_state : "idle",
            stable_diffusion: null,
            current_job_index : undefined , 
            current_group_id : undefined 
        };
    },

    computed:{
        is_ready(){
            return this.stable_diffusion.is_input_avail
        },
        is_stopping(){
            return this.stable_diffusion.is_stopping
        },
    },

    methods: {

        // call this 
        add_job(gen_options, raw_form_options ,gallery_component){
            gen_options = JSON.parse(JSON.stringify(gen_options))
            let group_options = {group_id : Math.random().toString() , jobs:[] }
            let n = gen_options.num_imgs
            for(let i=0 ; i < n  ; i ++ ){
                raw_form_options = JSON.parse(JSON.stringify(raw_form_options))
                gen_options = JSON.parse(JSON.stringify(gen_options))
                gen_options['job_id'] = Math.random().toString();
                gen_options['image_no'] = i 
                gen_options['job_state'] = "todo";
                gen_options['num_imgs'] = 1 

                if((!gen_options['seed']) || gen_options['seed'] < 0 ){
                    gen_options['seed'] = Math.floor(Math.random()*1000000)
                }

                raw_form_options['seed'] = gen_options['seed']
                raw_form_options['small_mod_seed'] = gen_options['small_mod_seed']
                raw_form_options['num_imgs'] = gen_options['num_imgs']
                gen_options.raw_form_options = raw_form_options

                
                group_options.jobs.push(gen_options)
                gen_options = JSON.parse(JSON.stringify(gen_options))

                if(gen_options['small_mod_seed'])
                    gen_options['small_mod_seed'] += 1
                else
                    gen_options['seed'] += 1234

            }
            this.add_job_group( group_options , gallery_component )

        }, 

        add_job_group(gen_options , gallery_component ){
            gen_options = JSON.parse(JSON.stringify(gen_options))
            console.log("adding job group ")
            console.log(gen_options)
            this.queue.groups_todo.push(gen_options);
            this.group_gallery_mapping[gen_options.group_id] = gallery_component;
            let imgs = []
            for(let i=0 ; i <gen_options.jobs.length ; i++ ){
                imgs.push({})
            }
            gallery_component.add_group({group_id: gen_options.group_id , num_imgs : gen_options.jobs.length, imgs: imgs , img_width:gen_options.jobs[0].img_width , img_height: gen_options.jobs[0].img_height})
            gallery_component.scroll_to_top()
            if(this.stable_diffusion.is_input_avail){
                this.get_and_do_job()
            }
        },

        finish_current_job(){
            // if the whole group is finished
            let is_group_done = true;

            for(let job of this.queue.current_group.jobs  ){
                if(job.job_state != "done")
                    is_group_done = false
            }
            if(is_group_done){
                // so that there are no empty loading items in gallry 
                let current_group_id = this.current_group_id
                let gallery = this.group_gallery_mapping[this.current_group_id]
                let gallery_group = gallery.get_group( this.current_group_id )
                let n_done = 0
                for(let img of gallery_group.imgs){
                    if(img.image_url)
                        n_done += 1
                }
                gallery_group.num_imgs = n_done;
                gallery_group.imgs = gallery_group.imgs.slice(0,n_done)

                gallery.update_group( gallery_group  )

                this.current_group_id = undefined;
                this.queue.current_group = undefined;

                 

                // also update the hisroty
                this.app.functions.add_to_history(current_group_id  , gallery_group )

            }

            this.current_job_index = undefined;

        },

        do_job(job){
            let that = this;
            console.log("dong job");
            console.log(job.prompt)
            if(!this.stable_diffusion.is_input_avail){
                alert("ERROR, stable_diffusion not available. ")
                return
            }

            if(!this.stable_diffusion){
                alert("ERROR, stable_diffusion not found. ")
                return
            }

            

            let callbacks = {
                on_img(img){

                    let img_path = img.generated_img_path
                    let aug_img_path = img.aux_output_image_path

                    console.log("on img " + that.current_group_id + " " + that.current_job_index)
                    if(that.current_group_id == undefined){
                        console.log("whoops 1")
                        return;
                    }

                    if(that.current_job_index == undefined){
                        console.log("whoops 2")
                        return
                    }

                    that.queue.current_group.jobs[that.current_job_index].generated_img = img_path ;
                    that.queue.current_group.jobs[that.current_job_index].aux_output_img = aug_img_path ;
                    that.queue.current_group.jobs[that.current_job_index].job_state = "done"
                    console.log("an image done "+ that.queue.current_group.jobs[that.current_job_index].job_state )
                    let gallery = that.group_gallery_mapping[that.current_group_id]
                    let gallery_group = gallery.get_group( that.current_group_id )
                    let el_to_update = gallery_group.imgs[ that.queue.current_group.jobs[that.current_job_index].image_no ]
                    el_to_update.image_url = img_path ;
                    el_to_update.aux_img_url = aug_img_path ;
                    el_to_update.description = job.prompt.slice(0, 250 ) ;
                    el_to_update.params = JSON.parse(JSON.stringify(job)) ;

                    gallery.update_group( gallery_group  )
                    that.finish_current_job()

                },
                on_progress(p ){
                    
                    if(that.current_group_id == undefined)
                        return;

                    if(that.current_job_index == undefined)
                        return

                    that.queue.current_group.jobs[that.current_job_index].done_percentage = p ;
                    that.done_percentage = p;
                    
                    let gallery = that.group_gallery_mapping[that.current_group_id]
                    let gallery_group = gallery.get_group( that.current_group_id )
                    let el_to_update = gallery_group.imgs[ that.queue.current_group.jobs[that.current_job_index].image_no ]
                    el_to_update.done_percentage = p ;
                    gallery.update_group( gallery_group  )

                },
                on_err(err){
                    console.log("errorrr ")
                    that.queue.current_group.jobs[that.current_job_index].generated_img = "ERROR" ;
                    that.queue.current_group.jobs[that.current_job_index].job_state = "done";
                    that.backend_error = err;

                    let gallery = that.group_gallery_mapping[that.current_group_id]
                    let gallery_group = gallery.get_group( that.current_group_id )
                    let el_to_update = gallery_group.imgs[ that.queue.current_group.jobs[that.current_job_index].image_no ]
                    console.log("errorrr 0")

                    el_to_update.image_url = "ERROR" ;
                    el_to_update.description = err ;


                    that.finish_current_job()

                },
            }

            for(let i=0; i <  that.queue.current_group.jobs.length; i++ ){
                if(that.queue.current_group.jobs[i].job_id == job.job_id){
                     this.current_job_index = i ;
                }
            }
            console.log("got in dex " + this.current_job_index )

            this.stable_diffusion.text_to_img(job, callbacks, 'txt2img');

        },

        get_and_do_job(){
            console.log("checking ")
            if(this.queue.current_group != undefined){
                console.log("current_group not undefined ")
                let job_todo = undefined;
                for(let job of this.queue.current_group.jobs){
                    if(job.job_state == "todo" || job.job_state == "doing"){
                        job_todo = job
                        this.current_group_id = this.queue.current_group.group_id;
                        break
                    }
                }

                if(job_todo == undefined){
                    console.log("job_todo undefined ")
                    // all jobs of that groups are done 
                    this.queue.current_group = undefined;
                    return this.get_and_do_job()
                } else {
                    console.log("got a new job " + job_todo.job_id + " "  + job_todo.job_state + " " + job_todo.prompt )
                    this.do_job(job_todo)
                    return
                }

            } else if(this.queue.groups_todo.length > 0 ){
                this.queue.current_group = this.queue.groups_todo.shift()
                console.log("found  a new group " + this.queue.current_group.group_id)
                return this.get_and_do_job()
            } else {
                console.log("i think no other jobs are there for now")
            }
        },


        stop_all(){
            if(this.queue.current_group != undefined &&    this.current_job_index != undefined){
                console.log("jjj1")
                for(let job of this.queue.current_group.jobs  ){
                    job.job_state = "done"
                }
                console.log("jjj")
                this.finish_current_job()
            }

            for(let group of this.queue.groups_todo){
                let gallery = this.group_gallery_mapping[group.group_id];
                gallery.delete_group(group.group_id)
            }
            Vue.set(this.queue , 'groups_todo' , [] ) 

            this.stable_diffusion.interupt();

        },
    },

     watch: {
        'stable_diffusion.is_input_avail': {
            handler: function(new_value) {
                if(new_value == true){
                    console.log("invoking")
                    this.get_and_do_job()
                    
                }
            },
            deep: true
        } , 
    }
}
</script>
<style>
</style>
<style scoped>
</style>