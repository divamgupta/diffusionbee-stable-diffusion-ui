// src/preload.js

import { contextBridge, ipcRenderer, webFrame } from 'electron'

contextBridge.exposeInMainWorld('ipcRenderer', ipcRenderer)
contextBridge.exposeInMainWorld('ipcRenderer_on', ipcRenderer.on)

var bind_ipc_renderer_on_fn = undefined;


function bind_ipc_renderer_on(fn) {
    bind_ipc_renderer_on_fn = fn;
}

contextBridge.exposeInMainWorld('bind_ipc_renderer_on', bind_ipc_renderer_on)

ipcRenderer.on("to_renderer", (e, data) => { // the msg channel which is used for electron to send msges to browser / renderer
    if (bind_ipc_renderer_on_fn)
        bind_ipc_renderer_on_fn(data)
});

contextBridge.exposeInMainWorld('clear_cache', () => webFrame.clearCache());

// Expose ipcRenderer to the client ( not using it yet )
// contextBridge.exposeInMainWorld('ipcRenderer', {
//   send: (channel, data) => {
//     let validChannels = ['client_channel'] // <-- Array of all ipcRenderer Channels used in the client
//     if (validChannels.includes(channel)) {
//       ipcRenderer.send(channel, data)
//     }
//   },
//   receive: (channel, func) => {
//     let validChannels = ['electron_channel'] // <-- Array of all ipcMain Channels used in the electron
//     if (validChannels.includes(channel)) {
//       // Deliberately strip event as it includes `sender`
//       ipcRenderer.on(channel, (event, ...args) => func(...args))
//     }
//   }
// })