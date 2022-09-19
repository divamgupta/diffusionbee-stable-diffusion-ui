// src/preload.js

import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('ipcRenderer', ipcRenderer)
contextBridge.exposeInMainWorld('ipcRenderer_on', ipcRenderer.on)

var bind_ipc_renderer_on_fn = undefined

function bind_ipc_renderer_on(fn) {
  bind_ipc_renderer_on_fn = fn
}

contextBridge.exposeInMainWorld('bind_ipc_renderer_on', bind_ipc_renderer_on)

ipcRenderer.on('to_renderer', (e, data) => {
  // the msg channel which is used for electron to send msges to browser / renderer
  if (bind_ipc_renderer_on_fn) bind_ipc_renderer_on_fn(data)
})
