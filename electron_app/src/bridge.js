import { ipcMain, dialog, app } from 'electron'

var win;
var python;

var py_buffer = "";
var is_app_closing = false;


function start_bridge() {

    console.log("starting briddddd")
    const fs = require('fs')

    let script_path = process.env.PY_SCRIPT || "./src/fake_backend.py"; 

    if (fs.existsSync(script_path)) {
        python = require('child_process').spawn('python3', [script_path]);
    }
    else{
        const path = require('path');
        let backend_path =  path.join(path.dirname(__dirname), 'core' , 'diffusionbee_backend' );
        python = require('child_process').spawn( backend_path  );
    }
    
   
    python.stdin.setEncoding('utf-8');

    python.stdout.on('data', function(data) {
        console.log("Python response: ", data.toString('utf8'));


        if(! data.toString().includes("sdbk ")){
            if(win && !is_app_closing )
                win.webContents.send('to_renderer', 'adlg ' + data.toString('utf8'));
        }
           
        

        if (win) {

            py_buffer += data.toString('utf8');

            let splitted = py_buffer.split("\n")

            if( splitted.length > 1 ){
                for (var i = 0; i < splitted.length -1 ; i++) {
                    if (splitted[i].length > 0)
                        if(win && !is_app_closing )
                            win.webContents.send('to_renderer', 'py2b ' + splitted[i]);
                }
            }

            py_buffer = splitted[ splitted.length - 1  ];

        } else {
            console.log("window not binded yet, got from py : " + data.toString('utf8'))
        }

    });

    python.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
        if(win && !is_app_closing )
             win.webContents.send('to_renderer', 'adlg ' + data.toString('utf8') );
    });

    python.on('close', (code) => {
        // if( code != 0 )
        // {
        // 	dialog.showMessageBox("Backend quit unexpectedly")
        // }

        if(is_app_closing){
            if (win){
                 app.exit(1);
            }
            return;
        }

        dialog.showMessageBox({ message: "Backend quit unexpectedly" });
        if (win)
        {
            is_app_closing = true;
            app.exit(1);
        }
            

    });

}


ipcMain.on('to_python_sync', (event, arg) => {
    if (python) {
        event.returnValue = "ok";
        // console("sending to py from  main " + arg )
        python.stdin.write("b2py " + arg.toString() + "\n")

    } else {
        console.log("Python not binded yet!");
        event.returnValue = "not_ok";
    }


})


ipcMain.on('to_python_async', (event, arg) => {
    if (python) {
        python.stdin.write("b2py " + arg.toString() + "\n")

    }
})

app.on('window-all-closed', () => {
    if(python){
        is_app_closing = true;
        python.kill();
    }
 
})



function bind_window_bridge(w) {
    console.log("browser object binded")
    win = w;
}


export { start_bridge, bind_window_bridge }