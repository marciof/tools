if (window.addEventListener) {
    window.addEventListener('load', setUp, false);
}
else if (document.addEventListener) {
    document.addEventListener('load', setUp, false);
}
else if (window.attachEvent) {
    window.attachEvent('onload', setUp);
}
else {
    window.onload = setUp;
}


function getEmail() {
    return 'm.' + (function(x) { return 'fau' + x + 'ino'; })('st')
        + '@' + 'liamg'.split('').reverse().join('') + '.'
        + String.fromCharCode(109, 111, 99).split('').reverse().join('');
}


function setUp() {
    var anchors = document.getElementsByTagName('a');
    
    for (var i = 0; i < anchors.length; ++i) {
        var anchor = anchors[i];
        
        if (anchor.className && anchor.className.match(/Email/)) {
            anchor.href = 'mailto:' + getEmail();
            
            if (anchor.innerHTML == '') {
                anchor.innerHTML = getEmail();
            }
        }
    }
    
    var isLocal = (window.location.hostname == 'localhost');
    
    // Google Analytics statistics.
    if (!isLocal && (typeof urchinTracker == 'function')) {
        _uacct = 'UA-1151940-1';
        urchinTracker();
    }
}
