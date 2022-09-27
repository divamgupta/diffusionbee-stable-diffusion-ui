import Vue from 'vue';

class StableDiffusion {

    constructor(){
        Vue.set(this, 'is_backned_loaded' ,  true);
        this.is_input_ready = false;
        // this.is_backned_loaded = false;

    }

    state_msg(msg){
        let msg_code = msg.substring(0, 4);
        if(msg_code == "mdld"){
           
            Vue.set(this, 'is_backned_loaded' ,  false);
            alert(this.is_backned_loaded)
      
        }
    }

}


export {StableDiffusion}