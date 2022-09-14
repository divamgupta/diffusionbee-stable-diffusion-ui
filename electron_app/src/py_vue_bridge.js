import Vue from 'vue'

import { native_alert } from './native_functions_vue_bridge.js'

var app_component_object

function update_state(msg) {
  if (app_component_object) {
    let keys = msg.split('___U_P_D_A_T_E___')[0]
    let value = msg.split('___U_P_D_A_T_E___')[1]

    keys = keys.split('.')

    let object_to_update = app_component_object.app_state

    for (let i = 0; i < keys.length - 1; i++) {
      object_to_update = object_to_update[keys[i]]
    }

    let final_key = keys[keys.length - 1]
    Vue.set(object_to_update, final_key, JSON.parse(value))
  } else {
    alert('Err : app stage object not set yet.')
  }
}

function bind_app_component(app_component) {
  // this should be called by the main vue component, to set bind the "app state" object to the bridge
  app_component_object
  app_component_object = app_component
}

function on_msg_from_py(msg) {
  if (msg.substring(0, 4) == 'utds') {
    // update the state of
    update_state(msg.substring(5))
  } else if (msg.substring(0, 4) == 'alrt') {
    // just alert
    native_alert(msg.substring(5))
  }
}

function add_log(msg) {
  if (app_component_object) {
    Vue.set(
      app_component_object.app_state,
      'logs',
      app_component_object.app_state.logs + '\n' + msg
    )
  }
}

function on_msg_receive(msg) {
  // on new msg from python

  if (msg.substring(0, 4) == 'py2b') {
    on_msg_from_py(msg.substring(5))
  } else if (msg.substring(0, 4) == 'adlg') {
    add_log(msg.substring(5))
  } else {
    alert('received unk message ' + msg.toString())
  }
}

window.bind_ipc_renderer_on(on_msg_receive)

function send_to_py(msg) {
  window.ipcRenderer.sendSync('to_python_sync', msg)
}

function send_to_py_async() {}

export { send_to_py, bind_app_component, send_to_py_async }
