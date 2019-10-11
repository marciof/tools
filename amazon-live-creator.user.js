// ==UserScript==
// @name Amazon Live Creator
// @icon https://www.amazon.com/favicon.ico
// @run-at document-idle
// @match https://amazonlivetools.amazon.com/
// @require https://cdnjs.cloudflare.com/ajax/libs/react/16.10.2/umd/react.production.min.js
// @require https://cdnjs.cloudflare.com/ajax/libs/react-dom/16.10.2/umd/react-dom.production.min.js
// @require https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.15/lodash.min.js
// @require https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.min.js
// ==/UserScript==

'use strict';

require.config({
    paths: {
        ace: ['https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.6/'],
    },
});

/**
 * @param type {string|React.Component}
 * @param [props] {Object}
 * @param children {Array<React.Element>}
 * @returns {React.Element}
 */
function e(type, props, ...children) {
    if (!_.isPlainObject(props)) {
        children.unshift(props);
        props = null;
    }
    return React.createElement(type, props, ...children);
}

/**
 * @param title {string}
 * @param document {Document}
 * @returns {Node}
 */
function cleanPage(title, document) {
    document.title = title;

    const faviconLink = document.querySelector('link[rel*=icon]')
        || document.createElement('link');

    faviconLink.rel = 'icon';
    faviconLink.href = 'https://www.amazon.com/favicon.ico';
    document.head.appendChild(faviconLink);

    for (let i = document.body.childNodes.length - 1; i >= 0; --i) {
        document.body.removeChild(document.body.childNodes.item(i));
    }

    const rootEl = document.createElement('div');
    document.body.appendChild(rootEl);
    return rootEl;
}

// FIXME: handle logged out
// FIXME: handle network/HTTP errors
class Api {
    constructor() {
        this.apiPrefix = '/api/v1/';
    }

    /**
     * @returns {Promise<Object>}
     */
    async listShows() {
        const response = await fetch(new Request(this.apiPrefix + 'user/shows'));
        return response.json();
    }
}

const rootEl = cleanPage(GM_info.script.name, document);
const api = new Api();

const acePromise = new Promise((resolve, reject) => {
    require(['ace/ace'], () => resolve(window.ace), reject);
});

// FIXME: use stylesheet?
rootEl.style.height = '500px';
rootEl.style.width = '1000px';
rootEl.style.border = '1px solid gray';

// FIXME: show syntax errors in Ace
Promise.all([acePromise, api.listShows()]).then(([ace, shows]) => {
    rootEl.textContent = JSON.stringify(shows, undefined, 2);

    const editor = ace.edit(rootEl);
    editor.setTheme('ace/theme/github');
    editor.session.setMode('ace/mode/json');
});
