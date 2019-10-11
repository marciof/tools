// ==UserScript==
// @name Amazon Live Creator
// @icon https://www.amazon.com/favicon.ico
// @run-at document-idle
// @match https://amazonlivetools.amazon.com/
// @require https://cdnjs.cloudflare.com/ajax/libs/react/16.10.2/umd/react.development.js
// @require https://cdnjs.cloudflare.com/ajax/libs/react-dom/16.10.2/umd/react-dom.development.js
// @require https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.15/lodash.js
// @require https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.js
// ==/UserScript==

'use strict';

require.config({
    paths: {
        ace: ['https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.6/'],
    },
});

const e = React.createElement;

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

const Shows = React.memo(props => {
    return e('section', null,
        e('h1', null, 'Shows'),
        e('form', null,
            e('label', null,
                e('select', null,
                    e('option', null, 'blah'))),
            e('input', {type: 'submit'})));
});

const rootEl = cleanPage(GM_info.script.name, document);
const api = new Api();

const acePromise = new Promise((resolve, reject) => {
    require(['ace/ace'], () => resolve(window.ace), reject);
});

api.listShows().then(shows => {
    console.error(shows);
});

ReactDOM.render(e(Shows), rootEl);
