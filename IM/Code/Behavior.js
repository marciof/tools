var _messages = {
    en: {
        PLUGIN_ERROR: 'Plug-in load error.',
        PLUGIN_INIT: 'Initializing plug-in...',
        SERVER_LABEL: 'Server:'
    }
};


var _plugin;
var _serverLabel, _serverStatus;


function getMessage(code) {
    return _messages[navigator.language][code];
}


function initializePlugin() {
    _plugin = document.getElementById('Server');
    _serverLabel = document.getElementById('ServerLabel');
    _serverStatus = document.getElementById('ServerStatus');
    
    _serverLabel.appendChild(document.createTextNode(getMessage('SERVER_LABEL')));
    
    if ('version' in _plugin) {
        setServerStatus('PLUGIN_INIT');
    }
    else {
        setServerStatus('PLUGIN_ERROR');
        return;
    }
}


function setServerStatus(code) {
    for (var i = 0; i < _serverStatus.childNodes; ++i) {
        _serverStatus.removeChild(_serverStatus.childNodes.item(i));
    }
    
    _serverStatus.appendChild(document.createTextNode(getMessage(code)));
}


document.addEventListener('load', initializePlugin, false);
