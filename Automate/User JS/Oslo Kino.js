// ==UserScript==
// @include http://program.filmweb.no/OsloKino/OsloKino.aspx
// ==/UserScript==


document.addEventListener('DOMContentLoaded', function () {
    var theaters = document.getElementById('ddlTheaters');
    
    if (theaters.value === '') {
        for (var i = 0; i < theaters.length; ++i) {
            var theater = theaters.item(i);
            
            if (theater.textContent === 'Colosseum') {
                theater.selected = true;
                theaters.onchange();
                break;
            }
        }
    }
}, false);
