// src/preload.js

import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('ipcRenderer', ipcRenderer)
contextBridge.exposeInMainWorld('ipcRenderer_on', ipcRenderer.on)

var bind_ipc_renderer_on_fn = undefined;
var bind_ipc_download_on_fns = {}

function bind_ipc_renderer_on(fn) {
    bind_ipc_renderer_on_fn = fn;
}

contextBridge.exposeInMainWorld('bind_ipc_renderer_on', bind_ipc_renderer_on)

ipcRenderer.on("to_renderer", (e, data) => { // the msg channel which is used for electron to send msges to browser / renderer
    if (bind_ipc_renderer_on_fn)
        bind_ipc_renderer_on_fn(data)
});


function bind_ipc_download_on( download_id,  fn_progress , fn_success, fn_error ) {
    console.log("gineded " + download_id)
    bind_ipc_download_on_fns[download_id] = {
        "progress" : fn_progress,
        "success" : fn_success,
        "error" : fn_error,
    }
}

contextBridge.exposeInMainWorld('bind_ipc_download_on', bind_ipc_download_on)


function unbind_ipc_download_on( download_id ){
    bind_ipc_download_on_fns[download_id] = undefined;
}



contextBridge.exposeInMainWorld('unbind_ipc_download_on', unbind_ipc_download_on)


ipcRenderer.on("to_download", (e, data) => { // the msg channel which is used for electron to send msges to browser / download
    if(!bind_ipc_download_on_fns[data.download_id]){
        console.log("no fn di "+ data.download_id)
        return 
    }
    if(!bind_ipc_download_on_fns[data.download_id][data.fn]){
        console.log("no fn d ")
        return
    }
    bind_ipc_download_on_fns[data.download_id][data.fn](data.msg)
});

