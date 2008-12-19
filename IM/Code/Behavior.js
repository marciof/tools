var _messages = {
    en: {
        PLUGIN_ERROR: 'Plug-in load error.',
        PLUGIN_INIT: 'Initializing plug-in...',
        SERVER_LABEL: 'Server:'
    }
};

var _locale, _plugin;
var _serverLabel, _serverStatus;


function initialize() {
    var language = navigator.language;
    
    if (!(navigator.language in _messages)) {
        language = 'en';
    }
    
    _locale = _messages[language];
    _plugin = document.getElementById('Server');
    _serverLabel = document.getElementById('ServerLabel');
    _serverStatus = document.getElementById('ServerStatus');
    
    setText(_serverLabel, _locale.SERVER_LABEL);
    
    if ('version' in _plugin) {
        setText(_serverStatus, _locale.PLUGIN_INIT);
    }
    else {
        setText(_serverStatus, _locale.PLUGIN_ERROR);
        return;
    }
}


function setText(node, text) {
    while (_serverStatus.childNodes.length > 0) {
        node.removeChild(node.childNodes.item(0));
    }
    
    node.appendChild(document.createTextNode(text));
}


// Don't use the DOMContentLoaded event, or the plug-in won't be detected.
window.addEventListener('load', initialize, false);
