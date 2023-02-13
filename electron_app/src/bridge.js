import { ipcMain, dialog, app } from 'electron'

var win;
var python;

var py_buffer = "";
var is_app_closing = false;

var last_few_err = ""

var change_backend = false;

let script_path = process.env.PY_SCRIPT || "./src/fake_backend.py";

function start_bridge(bin_path = null) {

    console.log("starting briddddd")
    const fs = require('fs')

    if (bin_path && (fs.existsSync(bin_path))) {
        change_backend = true;
        if (python) python.kill();
        python = require('child_process').spawn(bin_path);
    } else if (fs.existsSync(script_path)) {
        change_backend = true;
        if (python) python.kill();
        console.log("using python, script path: " + script_path)
        python = require('child_process').spawn('python3', [script_path]);
    } else {
        change_backend = true;
        if (python) python.kill();
        const path = require('path');
        let backend_path = path.join(path.dirname(__dirname), 'core', 'diffusionbee_backend');
        python = require('child_process').spawn(backend_path);
    }
    
   
    python.stdin.setEncoding('utf-8');

    python.stdout.on('data', function(data) {
        console.log("Python response: ", data.toString('utf8'));
        change_backend = false;


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
        last_few_err = last_few_err + data.toString();
        last_few_err = last_few_err.slice(-300);
        if(win && !is_app_closing )
             win.webContents.send('to_renderer', 'adlg ' + data.toString('utf8') );
    });

    python.on('close', (code) => {
        if (change_backend) return;
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

        dialog.showMessageBox({ message: "Backend quit unexpectedly. " + last_few_err });
        if (win)
        {
            is_app_closing = true;
            app.exit(1);
        }
            

    });

}


function on_msg_recieve(msg) { // on new msg from python 

    if (msg.substring(0, 4) == "py2b") {
        on_msg_from_py(msg.substring(5))
    } else if (msg.substring(0, 4) == "adlg") {
        add_log(msg.substring(5))
    } else {
        alert("recieved unk message " + msg.toString())
    }

}


var use = "python"

ipcMain.on('to_python_sync', (event, arg) => {
    if (use != "python") {
        start_bridge();
        use = "python"
    }
    if (python) {
        event.returnValue = "ok";
        python.stdin.write("b2py " + arg.toString() + "\n")
        console.log(arg.toString())

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



ipcMain.on('to_swift_sync', (event, arg) => {
    if (use != "swift") {
        start_bridge("./src/Debug/swiftbackend_diffusionbee");
        use = "swift"
    }
    if (python) {
        event.returnValue = "ok";
        python.stdin.write("b2s " + arg.toString() + "\n")
        console.log(arg.toString())

    } else {
        console.log("Python not binded yet!");
        event.returnValue = "not_ok";
    }
})


ipcMain.on('to_swift_async', (event, arg) => {
    if (python) {
        python.stdin.write("b2s " + arg.toString() + "\n")
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