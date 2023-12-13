import { ipcMain, dialog, clipboard } from 'electron'
import { app , screen } from 'electron'
import settings from 'electron-settings';

const path = require('path');

var win;


function bind_window_native_functions(w) {
    console.log("browser object binded")
    win = w;
}


let is_windows = process.platform.startsWith('win');



console.log(require('os').freemem()/(1000000000) + " Is the free memory")
console.log(require('os').totalmem()/(1000000000) + " Is the total memory")


ipcMain.on('save_dialog', (event, ...args) => {

    const filename = args[0] ? args[0] : "Untitled"
    const ext = args[1] ? args[1] : "png"
   
    let trimmedFilename = filename.substring(0, 254) // filename size limit
     let save_path = dialog.showSaveDialogSync({
            title: 'Save Image',
            defaultPath: trimmedFilename,
            filters: [{
              name: 'Image',
              extensions: [ext]
            }]
          })

     event.returnValue = save_path;
} )

console.log(require('os').release() + " ohoho")



ipcMain.on('file_dialog', (event, arg) => {
    console.log("file dialog request recieved" + arg) // prints "ping"
    let properties;
    let options;

    if (arg == "folder") // single folder 
    {
        properties = ['openDirectory'];
        options = { properties: properties } ;
    }
    else if(arg == 'img_file') // single image file 
    {
        properties = ['openFile' ]
        options = { filters :[ {name: 'Images', extensions: ['jpg', 'jpeg', 'png', 'bmp']}] , properties: properties } ;
    }
    else if(arg == 'weights_file') // single image file 
    {
        properties = ['openFile' ]
        options = { filters :[ {name: 'Checkpoints', extensions: ['ckpt' , 'safetensors' ]}] , properties: properties } ;
    }
    else if(arg == 'img_files') // multi image files
    {
        properties = ['multiSelections' , 'openFile' ]
        options = { filters :[ {name: 'Images', extensions: ['jpg', 'jpeg', 'png', 'bmp']}] , properties: properties } ;
    }
    else if(arg == 'text_files') // multi image files
    {
        properties = ['multiSelections' , 'openFile' ]
        options = { filters :[ {name: 'Images', extensions: ['txt']}] , properties: properties } ;
    }
    else if(arg == 'audio_files') // multi image files
    {
        properties = ['multiSelections' , 'openFile' ]
        options = { filters :[ {name: 'Images', extensions: ['mp3', 'wav']}] , properties: properties } ;
    }
    else if(arg == 'video_files') // multi image files
    {
        properties = ['multiSelections' , 'openFile' ]
        options = { filters :[ {name: 'Images', extensions: ["mp4", "mov", "avi", "flv", "wmv", "mkv"]}] , properties: properties } ;
    }
    else if(arg == 'any_files') // multi image files
    {
        properties = ['multiSelections' , 'openFile' ]
        options = {  properties: properties } ;
    }
    else
    {
        properties = ['openFile'];
        options = { properties: properties } ;
    }

    // let options = {
    //     See place holder 1 in above image
    //     title : "Custom title bar", 
    //     message : "Custom title bar",

    //     buttonLabel : "Custom button",

    //     See place holder 4 in above image
    //     filters :[
    //      {name: 'Images', extensions: ['jpg', 'png', 'gif']},
    //      {name: 'Movies', extensions: ['mkv', 'avi', 'mp4']},
    //      {name: 'Custom File Type', extensions: ['as']},
    //      {name: 'All Files', extensions: ['*']}
    //     ],
    //     properties: properties
    // }

    // //Synchronous
    let filePaths = dialog.showOpenDialogSync(options)

    if (filePaths && filePaths.length > 0)
        event.returnValue = filePaths.join(";;;");
    else
        event.returnValue = "NULL";
})




ipcMain.on('open_url', (event, url) => {
    let website_domain = require('../package.json').website ; 
    url = url.replace("__domain__" , website_domain );
    require('electron').shell.openExternal(url);
    event.returnValue = '';
})



ipcMain.on('save_file', (event, arg) => {
    let p1 = arg.split("||")[0];
    let p2 = arg.split("||")[1];
    require('fs').copyFileSync(p1, p2);
    event.returnValue = '';
})


ipcMain.on('copy_to_clipboard', (event, arg) => {
    clipboard.writeText(arg)
    event.returnValue = '';
})


ipcMain.on('get_from_clipboard', (event, arg) => {
    event.returnValue = clipboard.readText();
})


ipcMain.on('show_dialog_on_quit', (event, msg) => {
    if(win)
    {
        win.show_dialog_on_quit = true;
        win.dialog_on_msg = msg;
    }
    event.returnValue = 'ok';

})


ipcMain.on('dont_show_dialog_on_quit', (event, arg) => {
    if(win)
        win.show_dialog_on_quit = false;
    event.returnValue = 'ok';

})


ipcMain.on('get_instance_id', (event, arg) => {
    if (settings.hasSync('instance_id')){
        event.returnValue =  settings.getSync('instance_id')
        return;
    }
    let instance_id =  (Math.random() + 1).toString(36);
    settings.set('instance_id', instance_id);
    event.returnValue =   instance_id;

})


ipcMain.on('unfreeze_win', (event, arg) => {

    if (win) {
	win.savable=true;
        const primaryDisplay = screen.getPrimaryDisplay()
        const { width, height } = primaryDisplay.workAreaSize

        if (settings.hasSync('windowPosState')) {
            let windowState = settings.getSync('windowPosState');
            console.log("stateeee")
            console.log(windowState)

            if( windowState.x  >  0.8*width ||  windowState.y  >  0.8*height ||  windowState.x  < -0.2*width || windowState.y  < -0.2*height    ){
                win.setSize(850, 650, false);
            } else {
               win.setPosition( windowState.x  ,  windowState.y  , false);
               win.setMinimumSize(1070, 700);
                win.setSize(windowState.width, windowState.height , false); 
            }

            
        }
        else{
            win.setMinimumSize(1070, 700);
            win.setSize(850, 650, false);
        }

        win.setMinimumSize(1070, 700);
        // win.setResizable(true);
        win.setMaximizable(true);


        
        
    }

    event.returnValue = 'ok';

})



ipcMain.on('freeze_win', (event, arg) => {

    if (win) {
	win.savable=false;
	win.restore()
        win.setMinimumSize(770, 550)
        win.setSize(770, 550, false); 
        // win.setResizable(false);
        win.setMaximizable(false);

        const primaryDisplay = screen.getPrimaryDisplay()
        const { width, height } = primaryDisplay.workAreaSize;

        console.log( width +" " +  height)

        win.setPosition( parseInt((width-770)/2)  , parseInt((height-550)/2), false);

              

    }

    event.returnValue = 'ok';

})



ipcMain.on('show_about', (event, arg) => {

    if (win) {

        if(is_windows)
        {
            let about_content = require('../package.json').name + "\n" + "Version " + require('../package.json').version + " (" + require('../package.json').build_number + ")\n" + require('../package.json').description;
            const choice = require('electron').dialog.showMessageBoxSync(this, {
                buttons: ['Okay'],
                title: require('../package.json').name ,
                message: about_content
            });
        }
        else{
            app.showAboutPanel()
        }

        
    }

    event.returnValue = 'ok';

})




ipcMain.on('native_confirm', (event, arg) => {

    if (win) {
        
        const choice = require('electron').dialog.showMessageBoxSync(this, {
            type: 'question',
            buttons: ['Yes', 'No'],
            title: require('../package.json').name ,
            message: arg
        });
        if (choice === 1) {
            event.returnValue = false ;
        }
        else{
            event.returnValue = true ;
        }

    }
    else{
        event.returnValue = false ;
    }

})



ipcMain.on('close_window', (event, arg) => {

    if (win) {
        
        win.close()
        event.returnValue = true ;
    }
    else{
        event.returnValue = false ;
    }

})




ipcMain.on('native_alert', (event, arg) => {

    if (win) {
        
        const choice = require('electron').dialog.showMessageBoxSync(this, {
            buttons: ['Okay'],
            title: require('../package.json').name ,
            message: arg
        });
        
    }
    
    event.returnValue = true ;

})




ipcMain.on('save_b64_image', (event, b64_str, save_to_tmp ) => {

    const path = require('path');
    const fs = require('fs');

    let base64Data = b64_str.replace(/^data:image\/png;base64,/, "");
    
    const homedir = require('os').homedir();
    let save_dir = path.join(homedir , ".diffusionbee")


    if (!fs.existsSync(save_dir)){
        fs.mkdirSync(save_dir, { recursive: true });
    }

    if(save_to_tmp){
        save_dir = "/tmp/"
    } else {
        save_dir = path.join(save_dir , "inp_images")
    }

    

    if (!fs.existsSync(save_dir)){
        fs.mkdirSync(save_dir, { recursive: true });
    }

    let p = require('path').join(save_dir,  Math.random().toString()+".png");

    require("fs").writeFileSync(p , base64Data, 'base64'); 
    
    event.returnValue = p ;

})



function save_json(data , fname ){
    const path = require('path');
    const fs = require('fs');
    const homedir = require('os').homedir();
    let save_dir = path.join(homedir , ".diffusionbee")


    if (!fs.existsSync(save_dir)){
        fs.mkdirSync(save_dir, { recursive: true });
    }

    let data_path = path.join(homedir , ".diffusionbee" , fname )
    fs.writeFileSync( data_path, JSON.stringify(data) );
}



function load_data(fname){
    const path = require('path');
    const fs = require('fs');
    const homedir = require('os').homedir();
    let data_path = path.join(homedir , ".diffusionbee" , fname );

    if (fs.existsSync(data_path)){
        let json_str = fs.readFileSync( data_path );
        try {
            return JSON.parse(json_str);
          } catch (error) {
            return {} ;
          }
    }
    else{
        return {} ;
    }       
}

ipcMain.on('save_data', (event, arg , fname ) => {
    if(fname)
        save_json(arg, fname)
    else
        save_json(arg, "data.json")
    event.returnValue = true ;
})


ipcMain.on('load_data', (event, fname) => {
    if(fname)
        event.returnValue = load_data(fname)
    else
        event.returnValue = load_data("data.json")
})


ipcMain.on('delete_file', (event, fpath) => {
    const fs = require('fs');
    try{
        fs.unlinkSync(fpath);
        console.log("deleted")
        event.returnValue = true;
    } catch {
        console.log("err in deleting")
        event.returnValue = false;
    }
    
})


function run_realesrgan(input_path , cb ){
    const path = require('path');
    let out_path = "/tmp/"+Math.random()+".png";
    const fs = require('fs');
    let bin_path =  process.env.REALESRGAN_BIN || path.join(path.dirname(__dirname), 'core' , 'realesrgan_ncnn_macos' );
    let weights_path = bin_path.replaceAll("realesrgan_ncnn_macos" , "models") + "/";
    let proc = require('child_process').spawn( bin_path  , ['-m' , weights_path , '-i' , input_path , '-o' , out_path ]);

    console.log([bin_path , '-m' , weights_path , '-i' , input_path , '-o' , out_path ])

    proc.stderr.on('data', (data) => {
        console.error(`sr stderr: ${data}`);
    });

    proc.stdout.on('data', (data) => {
        console.error(`sr stderr: ${data}`);
    });

    proc.on('close', (code) => {
        if (fs.existsSync(out_path)) {
            cb(out_path);
        }
        else
        {
            cb('');
        }
    });
}



function add_custom_pytorch_models(pytorch_model_path, model_name, convert_params , cb ){
    
    const path = require('path');
    const fs = require('fs');
    const homedir = require('os').homedir();
    let models_path = path.join(homedir , ".diffusionbee" , "imported_models");

    if (!fs.existsSync(models_path)){
        fs.mkdirSync(models_path, { recursive: true });
    }


    let script_path = process.env.PY_SCRIPT || "../backends/stable_diffusion/diffusionbee_backend.py"; 
    
    let out_path =  path.join(homedir , ".diffusionbee" , "imported_models" , model_name+".tdict" );
    let proc;
    if (fs.existsSync(script_path)) {
        proc = require('child_process').spawn( "python3"  , [ script_path ,  "convert_model" ,  pytorch_model_path , out_path ]);
    } else {
        let bin_path =  path.join(path.dirname(__dirname), 'core' , 'diffusionbee_backend' );
        proc = require('child_process').spawn( bin_path  , [ "convert_model" ,  pytorch_model_path , out_path ]);
    }
    

    
    let errors = ""
    let std_out_all = ""

    proc.stderr.on('data', (data) => {
        console.error(`sr stderr: ${data}`);
        errors += data
    });

    proc.stdout.on('data', (data) => {
        console.error(`sr sdtout: ${data}`);
        std_out_all += data
    });

    proc.on('close', (code) => {

        if(convert_params.delete_origional_always){
            try{
                fs.unlinkSync(pytorch_model_path);
            } catch {}
        }

        if(code != 0){
            cb({success:false , error:errors  })
            try{
                fs.unlinkSync(out_path);
            } catch {}
        }
        else{
            if(convert_params.delete_origional_on_success){
                try{
                    fs.unlinkSync(pytorch_model_path);
                } catch {}
            }

            let converted_model_data = {}
            for(let l of std_out_all.split("\n")){
                if(l.includes("__converted_model_data__")){
                    converted_model_data = JSON.parse(l.replace( "__converted_model_data__", "") )
                }
            }

            cb({success:true, model_path:out_path , metadata : converted_model_data })
        }
       
    });
}


ipcMain.handle('add_custom_pytorch_models', async (event, pytorch_model_path, model_name, convert_params ) => {
    const result = await new Promise(resolve => add_custom_pytorch_models( pytorch_model_path, model_name , convert_params , resolve));
    return result
})



ipcMain.handle('run_realesrgan', async (event, arg) => {
    const result = await new Promise(resolve => run_realesrgan( arg , resolve));
    return result
})

// ipcRenderer.invoke('run_realesrgan', '/Users/divamgupta/Downloads/333.png' ).then((result) => {
//     alert(result)
//   })



ipcMain.on('list_imported_models', (event, arg) => {
    const path = require('path');
    const fs = require('fs');
    const homedir = require('os').homedir();
    let models_path = path.join(homedir , ".diffusionbee" , "imported_models");

    if (!fs.existsSync(models_path)){
        fs.mkdirSync(models_path, { recursive: true });
    }

    event.returnValue = fs.readdirSync(models_path, {withFileTypes: true}).filter(item => !item.isDirectory()).map(item => item.name).filter(item => item.endsWith('.tdict'))

})





ipcMain.on('get_assets_dir', (event, arg) => {
    const path = require('path');
    const fs = require('fs');
    const homedir = require('os').homedir();
    let assets_path = path.join(homedir , ".diffusionbee" , "downloaded_assets");

    if (!fs.existsSync(assets_path)) {
        fs.mkdirSync(assets_path, { recursive: true });
    }

    event.returnValue = assets_path;
});



ipcMain.on('download-file', (event, url, dest, downloadId) => {
  
  const fs = require('fs');
  const path = require('path');

  const file = fs.createWriteStream(dest);
  const request = require('request');

  const crypto = require('crypto');

  let hash = crypto.createHash('md5');

  request.get({
      url,
      followRedirect: true,
      rejectUnauthorized: false, // ignore SSL certificate errors,
      timeout: 20000 , //20s
    })
    .on('response', response => {
      const totalBytes = parseInt(response.headers['content-length'], 10);
      let downloadedBytes = 0;

      response.on('data', chunk => {
        downloadedBytes += chunk.length;
        hash.update(chunk);
        const progress = Math.round((downloadedBytes / totalBytes) * 100);
        try { 
           event.sender.send(`to_download`, {fn:'progress' , download_id: downloadId , msg:progress });
        } catch (err) {
            console.log(err)
        }
        
      });

      response.pipe(file);

    })
    .on('error', err => {
      fs.unlink(dest, () => {});

        try {
           event.sender.send(`to_download`, {fn:'error' , download_id: downloadId , msg:err.message  });
        } catch (err) {
           console.log(err)
        }
        
      
    })
    .on('end', () => {

        const hashValue = hash.digest('hex');
        
        try {
           event.sender.send(`to_download`, {fn:'success' , download_id: downloadId , msg: hashValue  });
        } catch (err) {
           console.log(err)
        }
        
    });
});


console.log("native functions imported")


export { bind_window_native_functions }