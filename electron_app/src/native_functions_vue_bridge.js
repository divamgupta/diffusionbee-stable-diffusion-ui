

function native_confirm(message){
	return window.ipcRenderer.sendSync('native_confirm', message );
}

function native_alert(message){
	return window.ipcRenderer.sendSync('native_alert', message );
}

export { native_confirm , native_alert } 