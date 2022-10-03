import { ipcMain, dialog } from 'electron'
import { app , screen } from 'electron'
import settings from 'electron-settings';

var win;


function bind_window_native_functions(w) {
    console.log("browser object binded")
    win = w;
}


let is_windows = process.platform.startsWith('win');



console.log(require('os').freemem()/(1000000000) + " Is the free memory")
console.log(require('os').totalmem()/(1000000000) + " Is the total memory")


ipcMain.on('save_dialog', (event, ...args) => {

    const seed = args[1] ? args[1] : "0"
    const prompt = args[0] ? args[0] : "Untitled"
    let filename = ''
    if (seed === '0') {
        filename = prompt
    } else {
        filename = seed + '-' + prompt
    }
    let trimmedFilename = filename.substring(0, 254) // filename size limit
     let save_path = dialog.showSaveDialogSync({
            title: 'Save Image',
            defaultPath: trimmedFilename,
            filters: [{
              name: 'Image',
              extensions: ['png']
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
    else if(arg == 'img_files') // multi image files
    {
        properties = ['multiSelections' , 'openFile' ]
        options = { filters :[ {name: 'Images', extensions: ['jpg', 'png', 'bmp']}] , properties: properties } ;
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
                win.setSize(windowState.width, windowState.height , false); 
            }

            
        }
        else{
            win.setSize(850, 650, false);
        }


        win.setResizable(true);
        win.setMaximizable(true);


        
        
    }

    event.returnValue = 'ok';

})



ipcMain.on('freeze_win', (event, arg) => {

    if (win) {
	win.savable=false;
	win.restore()
        win.setSize(770, 550, false); 
        win.setResizable(false);
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




ipcMain.on('save_b64_image', (event, arg) => {

    let base64Data = arg.replace(/^data:image\/jpeg;base64,/, "");
    let temp_dir = require("os").tmpdir();

    let p = require('path').join(temp_dir,  Math.random().toString()+".jpg");

    require("fs").writeFileSync(p , base64Data, 'base64'); 
    
    event.returnValue = p ;

})


ipcMain.on('save_data', (event, arg) => {
    const path = require('path');
    const fs = require('fs');
    const homedir = require('os').homedir();
    let save_dir = path.join(homedir , ".diffusionbee")


    if (!fs.existsSync(save_dir)){
        fs.mkdirSync(save_dir, { recursive: true });
    }

    let data_path = path.join(homedir , ".diffusionbee" , "data.json")
    fs.writeFileSync( data_path, JSON.stringify(arg) );
    event.returnValue = true ;

})


ipcMain.on('load_data', (event, arg) => {
    const path = require('path');
    const fs = require('fs');
    const homedir = require('os').homedir();
    let data_path = path.join(homedir , ".diffusionbee" , "data.json");

    if (fs.existsSync(data_path)){
        event.returnValue = JSON.parse(fs.readFileSync( data_path ));
    }
    else{
        event.returnValue = {} ;
    }       

})




console.log("native functions imported")


export { bind_window_native_functions }
