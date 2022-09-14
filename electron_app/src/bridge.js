import { ipcMain, dialog, app } from 'electron'

var win
var python

var py_buffer = ''
var is_app_closing = false

function start_bridge() {
  console.log('starting briddddd')
  const fs = require('fs')

  if (fs.existsSync('../stable-diffusion/txt2img.py')) {
    python = require('child_process').spawn('python3', [
      '../stable-diffusion/txt2img.py',
    ])
  } else {
    const path = require('path')
    let backend_path = path.join(path.dirname(__dirname), 'core', 'txt2img')
    python = require('child_process').spawn(backend_path)
  }

  python.stdin.setEncoding('utf-8')

  python.stdout.on('data', function (data) {
    console.log('Python response: ', data.toString('utf8'))

    if (!data.toString().includes('___U_P_D_A_T_E___'))
      win.webContents.send('to_renderer', 'adlg ' + data.toString('utf8'))

    if (win) {
      py_buffer += data.toString('utf8')

      let splitted = py_buffer.split('\n')

      if (splitted.length > 1) {
        for (var i = 0; i < splitted.length - 1; i++) {
          if (splitted[i].length > 0)
            win.webContents.send('to_renderer', 'py2b ' + splitted[i])
        }
      }

      py_buffer = splitted[splitted.length - 1]
    } else {
      console.log(
        'window not bound yet, got from py : ' + data.toString('utf8')
      )
    }
  })

  python.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`)
    win.webContents.send('to_renderer', 'adlg ' + data.toString('utf8'))
  })

  python.on('close', (code) => {
    // if( code != 0 )
    // {
    // 	dialog.showMessageBox("Backend quit unexpectedly")
    // }

    if (is_app_closing) {
      if (win) app.exit(1)
      return
    }

    dialog.showMessageBox({ message: 'Backend quit unexpectedly' })
    if (win) app.exit(1)
  })
}

ipcMain.on('to_python_sync', (event, arg) => {
  if (python) {
    event.returnValue = 'ok'
    // console("sending to py from  main " + arg )
    python.stdin.write('b2py ' + arg.toString() + '\n')
  } else {
    console.log('Python not bound yet!')
    event.returnValue = 'not_ok'
  }
})

ipcMain.on('to_python_async', (event, arg) => {
  if (python) {
    python.stdin.write('b2py ' + arg.toString() + '\n')
  }
})

app.on('window-all-closed', () => {
  if (python) {
    is_app_closing = true
    python.kill()
  }
})

function bind_window_bridge(w) {
  console.log('browser object bound')
  win = w
}

export { start_bridge, bind_window_bridge }
