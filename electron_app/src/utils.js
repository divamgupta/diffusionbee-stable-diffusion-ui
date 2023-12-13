
function compute_n_cols() {
    let w = window.innerWidth;
    let n_col;
    if (w < 576) { n_col = 2 } else if (w < 668) { n_col = 3 } else if (w < 892) { n_col = 4 } else if (w < 1100) { n_col = 5 } else if (w < 1600) { n_col = 6 } else if (w < 1900) { n_col = 7 } else if (w < 2100) { n_col = 8 } else if (w < 2400) { n_col = 9 }

    n_col -= 1;
    return n_col;
}

function compute_time_remaining(time_remaining) {
    if (time_remaining.asSeconds() < 1) return "";
    if (time_remaining.hours() > 0) return `(${time_remaining.hours()}h${time_remaining.minutes()}m left)`;
    else return `(${time_remaining.minutes()}m${time_remaining.seconds()}s left)`;
}

function simple_hash( strr ) {
    var hash = 0;
    for (var i = 0; i < strr.length; i++) {
        var char = strr.charCodeAt(i);
        hash = ((hash<<5)-hash)+char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return hash;
}


function resolve_asset_illustration(name) {
    let pre_assets_list_svg = [
      ];
    let pre_assets_list_png = [
        ];
    if (pre_assets_list_svg.includes(name))
        return require("@/assets/" + name + ".svg")
    else  if (pre_assets_list_png.includes(name))
        return require("@/assets/" + name + ".png")
    else if (name.startsWith("https://") || name.startsWith("http://"))
        return name;
    else
        return "file://" + name;
}




const escapeHtml = (unsafe) => {
    return unsafe.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;');
}


function open_popup( img_url , text ){
            
    let css = `
        <style>
        img {
    
                     width: 100%;
                      height:100%;
                      object-fit: contain;
                      user-drag: none;
          
            }
            @media (prefers-color-scheme: light) {
                body {
                    background-color: #f2f2f2;
                }
            }
            @media (prefers-color-scheme: dark) {
                body {
                    background-color: #303030;
                }
            }
            body{
                padding : 0;
                margin: 0;
                -webkit-user-select: none;
                    -webkit-app-region: drag;
                  
                      user-drag: none;
                        -webkit-user-drag: none;
                        user-select: none;
                        -moz-user-select: none;
                        -webkit-user-select: none;
                        -ms-user-select: none;
            }
            p{
                padding:40px;
            }

       </style>
    `
    let html = '<html><head>'+css+'</head><body>' ;

    if (img_url)
        html += '<img src="'+escapeHtml(img_url)+'"> ';
    
    if( text )
         html += '<p> '+ escapeHtml(text) +' </p>';
    
    html += '</body></html>'
    
    let uri = "data:text/html," + encodeURIComponent(html);
    uri;
    let if_frame= '';
    if(navigator.platform.toUpperCase().indexOf('MAC')>=0 ){
        if_frame = ",frame=false"
    }

    window.open(escapeHtml(uri), '_blank', 'top=100,left=100,nodeIntegration=no'+if_frame); // 
    

}


function addImageProcess(src){
    return new Promise((resolve, reject) => {
      let img = new Image()
      img.onload = () => resolve(img)
      img.onerror = reject
      img.src = src
    })
  }

// this will only be called when the user clicks to upload thier data for sharing. 
async function temp_upload_img(img_path) {
    let img_tag = await addImageProcess("file://" + img_path)
    let file = await fetch(img_tag.src);
    let blob = await file.blob()
    file =  await new File([blob], 'bee_file'+Math.random()+'.png', blob)

    try {
       let x = await fetch('https://bee.transfr.one/file.png', {
            method: 'PUT',
            body: file 
        });
        if(x.status != 200)
             throw 'Could not upload';
        x = await (await x.text()).toString().replaceAll("\n" , "");
        return x;
    } catch (error) {
        throw 'Could not upload';
    }
  
  }

// this will only be called when the user clicks to upload thier data for sharing. 
async function share_on_arthub(imgs , params,  prompt ) {
    let urls = [];

    for(let im of imgs)
        if(im != 'nsfw')
            urls.push( await temp_upload_img(im))

    console.log(urls.join(','))

    let share_url = "https://arthub.ai/upload?";

    params = JSON.parse(JSON.stringify(params))


    share_url += "description="+ prompt + "&";
    if(!params.model_version)
        params.model_version = ""
    params.model_version = "DiffusionBee" + params.model_version + (params.Model? "_"+params.Model : "") ;
    share_url += "params="+ JSON.stringify(params) + "&"
    share_url += "images="+ urls.join(',')
    window.ipcRenderer.sendSync('open_url', share_url );
}


function form_params_to_readable_dict(form_params){

    let r = {};
    let vals = {"seed" : "Seed" , "guidence_scale" : "Scale" , "num_steps":"Steps"  ,  "steps":"Steps"  ,  "guidance_scale": "Guidance Scale",
          "inp_img_strength" : "Image Strength" , "input_image_strength": "Image Strength"  , "img_width":"Img Width" , "img_height": "Img Height" , 
           "negative_prompt" : "Negative Prompt" , "model_version":"model_version", "scheduler":"Sampler" , 
           "selected_sd_model" : "Model", "controlnet_model" : "ControlNet" , "applet_name" : "Mode", 
           "small_mod_seed":"Small Modification Seed", "controlnet": "controlnet" , "controlnet_preprocess":"controlnet_preprocess" , "control_weight":"ControlNet Importance" , "is_clip_skip_2": "Clip Skip 2"}

    for(let k in vals)
        if( form_params[k])
            r[vals[k]] =  form_params[k];

    return r;
   
}


// convert the dict from the output of a form to readable text
function form_params_to_text(form_params){
    let t = ""
   let r = form_params_to_readable_dict(form_params)
    for(let k in r)
            t += " " +k  +  " : " + r[k] + " |";
    if(t.charAt(t.length - 1) == "|")
        t = t.slice(0, -1);
    return t;

}

function find_in_form_recursive(id , form_elements){
    for(let el of form_elements ){
        if(el.id == id){
            return el 
        }

        if(el.children){
            let ans =  find_in_form_recursive(id , el.children)
            if(ans)
                return ans
        }
    }
    return undefined
}


function migrate_history_only_once( current_new_history ){

    let v =  window.ipcRenderer.sendSync('load_data', 'migration_data.json');
    if(v.is_history_migrated){
        console.log("already migrated hisro")
         return {};
    }


    let app_data_v1 =  window.ipcRenderer.sendSync('load_data', 'data.json');
    let new_history = {}

    //todo make sure it only runs once 

    if(app_data_v1.history){
        let old_hisotry = app_data_v1.history
        console.log(old_hisotry)
        for(let k in old_hisotry){

            // let a = 2
            // if(a > 1)
            //     continue

            if(current_new_history[k])
                continue

    

            let new_item = {}
            let old_item = old_hisotry[k]
            let old_aux_img_url = undefined
            if(old_item.controlnet && old_item.controlnet_preprocess == "Yes" ){
                // remove first image 
                old_aux_img_url = old_item.imgs.shift();
            }

            new_item.group_id = k;
            new_item.img_height = old_item.img_h;
            new_item.img_width = old_item.img_w;
            new_item.key = k;
            new_item.num_imgs = old_item.imgs.length;
            new_item.prompt = old_item.prompt;
            new_item.params = {}
            new_item.params.applet_name = "txt2img"

            if(old_item.inp_img && !(old_item.controlnet) ){
                new_item.params.applet_name = "img2img"
                new_item.params.input_image_strength = old_item.inp_img_strength
                new_item.params.input_image_with_mask = old_item.inp_img
                new_item.params.input_img = old_item.inp_img
            }

            new_item.params.num_imgs = 1
            if(old_item.dif_steps)  
                new_item.params.num_steps = old_item.dif_steps
            new_item.params.img_height =  old_item.img_h;
            new_item.params.img_width =  old_item.img_w;
            new_item.params.is_adv_mode = true 
            new_item.params.job_state = "done"
            if( old_item.selected_sampler)
                new_item.params.scheduler = old_item.selected_sampler
            
            new_item.params.guidance_scale = old_item.guidence_scale 
            new_item.params.controlnet_model = old_item.controlnet
            if(old_item.controlnet){
                new_item.params.controlnet_input_image_path = old_item.inp_img

            }
            if(old_item.controlnet_preprocess == "Yes"){
                new_item.do_controlnet_preprocess = true
            }

            new_item.params.prompt = new_item.prompt

            new_item.params.seed = old_item.seed 
            new_item.params.selected_sd_model = old_item.model_version
            
            new_item.params.raw_form_options = JSON.parse(JSON.stringify(new_item.params))

            new_item.imgs = []
            for(let i=0; i< new_item.num_imgs ; i++ ){
                let img_item = {}
                img_item.description = new_item.prompt
                img_item.done_percentage = -1 
                img_item.image_url = old_item.imgs[i]
                img_item.params = JSON.parse(JSON.stringify(new_item.params))

                if(old_item.controlnet){
                    img_item.aux_img_url = old_aux_img_url
                }

                img_item.params.seed += 1234*i 
                img_item.params.raw_form_options = JSON.parse(JSON.stringify(img_item.params))
                new_item.imgs.push(img_item)
            }

            // add_to_history(k ,new_item  )
            console.log("migrated item")
            console.log(new_item)
            new_history[k] = new_item
        }
    }

    
    v.is_history_migrated = true;
    window.ipcRenderer.sendSync('save_data', v , "migration_data.json");


    return new_history;
}


export { compute_n_cols , compute_time_remaining , resolve_asset_illustration , simple_hash , open_popup, share_on_arthub, form_params_to_text, find_in_form_recursive, form_params_to_readable_dict, migrate_history_only_once}