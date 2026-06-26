// ==UserScript==
// @name Bypass Google Redirect Notice
// @namespace https://violentmonkey.github.io
// @version 0.1
// @author marciof
// @match https://www.google.com/url?*
// @icon https://www.google.com/s2/favicons?sz=64&domain=google.com
// @grant unsafeWindow
// @run-at document-end
// ==/UserScript==

(function() {
    'use strict';
    const window = unsafeWindow;
    const link = window.document.links.item(0);
    if (link && link.href) {
        console.info('Redirect link found:', link.href);
        window.location.replace(link.href);
    }
    else {
        console.error('Redirect link not found.');
    }
})();
