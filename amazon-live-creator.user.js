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

/**
 * @param title {string}
 * @param document {Document}
 * @returns {Node}
 */
function cleanPage(title, document) {
    console.log('Cleaning up page, title:', title, '; document:', document);
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

/**
 * @returns {boolean}
 */
function isReactElement(value) {
    return _.isPlainObject(value)
        && ('$$typeof' in value)
        && _.isSymbol(value.$$typeof);
}

/**
 *
 * @param tag {string}
 * @param [props] {Object}
 * @param children {Array<string|React.Element>}
 * @returns {React.Element}
 */
function jsx(tag, props, ...children) {
    if (isReactElement(props)) {
        children.unshift(props);
        props = null;
    }
    console.info('JSX tag:', tag, '; props:', props, '; children:', children);
    return React.createElement(tag, props, ...children);
}

// FIXME: handle logged out
// FIXME: handle network/HTTP errors
// FIXME: allow cancellation of in-flight requests?
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

const fieldset = jsx.bind(null, 'fieldset');
const legend = jsx.bind(null, 'legend');
const p = jsx.bind(null, 'p');
const a = jsx.bind(null, 'a');
const form = jsx.bind(null, 'form');
const select = jsx.bind(null, 'select');
const option = jsx.bind(null, 'option');
const input = jsx.bind(null, 'input');

const LoginLink = React.memo(() =>
    p(a({href: 'https://www.amazon.com/gp/sign-in.html'},
        'Please login to your Amazon account first.')));

const Shows = React.memo(props => {
    return form(fieldset(
        legend('Shows'),
        p(select(
            option('blah'))),
        p(input({type: 'submit'}))));
});

const App = React.memo(props => {
    const {api} = props;
    const [shows, setShows] = React.useState(undefined);

    React.useEffect(() => {
        api.listShows().then(shows => setShows(shows));
    }, [api]);

    if ((shows === undefined) || shows.errors) {
        return jsx(LoginLink);
    }
    return jsx(Shows);
});

const rootEl = cleanPage(GM_info.script.name, document);
const api = new Api();

const acePromise = new Promise((resolve, reject) => {
    require(['ace/ace'], () => resolve(window.ace), reject);
});

ReactDOM.render(jsx(App, {api: api}), rootEl);
