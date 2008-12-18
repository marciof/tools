function call() {
    try {
        alert(!!document.getElementById('Server').version);
    }
    catch (e) {
        alert(e);
    }
}

/*
      <div class="Panel">
        <h1>Could not load IM plug-in</h1>
        <div>Check the <a href="opera:plugins">available plug-ins</a>.</div>
      </div>
*/


/*var plugin;

document.addEventListener('load', function() {
    plugin = document.getElementById("Plugin");
}, false);*/

//setTimeout(call, 1000);
