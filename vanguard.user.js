// ==UserScript==
// @name Vanguard
// @include https://personal.vanguard.com/*/AuthLogin
// @include https://logon.vanguard.com/*
// @run-at document-idle
// ==/UserScript==

let intervalId = setInterval(function disableRemember() {
    const selectors = [
        'input[name="LoginForm:DEVICE"][value=false]',
        'label[for=NO]',
    ];

    for (let i = 0; i < selectors.length; ++i) {
        const element = document.querySelector(selectors[i]);

        if (element) {
            element.checked = true;
            element.click();
            clearInterval(intervalId);
            console.log('Found form');
            return;
        }
    }

    console.warn('Form not yet found');
}, 500);
