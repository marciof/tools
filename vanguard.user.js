// ==UserScript==
// @name Vanguard
// @match https://personal.vanguard.com/us/AuthLogin
// @run-at document-idle
// ==/UserScript==

document.querySelector('input[name="LoginForm:DEVICE"][value=false]').checked = true;
