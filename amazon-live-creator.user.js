// ==UserScript==
// @name Amazon Live Creator
// @icon https://www.amazon.com/favicon.ico
// @run-at document-start
// @match https://amazonlivetools.amazon.com/
// @require https://cdnjs.cloudflare.com/ajax/libs/react/16.10.2/umd/react.development.js
// @require https://cdnjs.cloudflare.com/ajax/libs/react-dom/16.10.2/umd/react-dom.development.js
// @require https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.15/lodash.js
// @require https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.js
// ==/UserScript==

'use strict';

/**
 * @param title {string}
 * @returns {Node}
 */
function cleanPage(title) {
    console.info('Cleaning up page, title:', title, '; document:', document);
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

const rootEl = cleanPage(GM_info.script.name);

require.config({
    paths: {
        ace: ['https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.6/'],
    },
});

const acePromise = new Promise((resolve, reject) => {
    require(['ace/ace'], () => {
        console.debug('ACE editor', window.ace);
        return resolve(window.ace);
    }, reject);
});

/**
 * @returns {boolean}
 */
function isReactElement(value) {
    const isPlainObject = _.isPlainObject(value);

    return !isPlainObject
        || (isPlainObject
            && ('$$typeof' in value)
            && _.isSymbol(value.$$typeof));
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
    console.debug('JSX tag:', tag, '; props:', props, '; children:', children);
    return React.createElement(tag, props, ...children);
}

// FIXME: handle network/HTTP/API errors
// FIXME: allow cancellation of in-flight requests?
class Api {
    constructor() {
        this.urlPathPrefix = '/api/v1/';
    }

    /**
     * @returns {Promise<Object>}
     */
    async listShows() {
        const response = await this.request('user/shows');
        const json = await response.json();

        console.info('API shows:', json);
        return json;
    }

    /**
     * @param path {string}
     * @returns {Promise<Response>}
     */
    async request(path) {
        const fullPath = this.urlPathPrefix + path;
        console.info('API request:', fullPath);

        const response = await fetch(new Request(fullPath));
        console.info('API response:', response);

        return response;
    }
}

const fieldset = jsx.bind(null, 'fieldset');
const legend = jsx.bind(null, 'legend');
const p = jsx.bind(null, 'p');
const div = jsx.bind(null, 'div');
const a = jsx.bind(null, 'a');
const form = jsx.bind(null, 'form');
const select = jsx.bind(null, 'select');
const option = jsx.bind(null, 'option');
const input = jsx.bind(null, 'input');

// FIXME: text as children?
const AceEditor = React.memo(({text, style}) => {
    const [ace, setAce] = React.useState(null);
    const editorRef = React.useRef(null);

    React.useEffect(() => void acePromise.then(setAce), []);

    React.useEffect(() => {
        if (ace) {
            const editor = ace.edit(editorRef.current);
            editor.setTheme("ace/theme/github");
            editor.session.setMode("ace/mode/json");
        }
    }, [ace]);

    return div({ref: editorRef, style: style}, text);
});

const JsonAceEditor = React.memo(({json}) => {
    return jsx(AceEditor, {
        text: JSON.stringify(json, undefined, 4),
        style: {
            width: '100%',
            height: '250px',
            border: '1px solid gray',
        },
    })
});

const LoginLink = React.memo(() =>
    p(a({href: 'https://www.amazon.com/gp/sign-in.html'},
        'Please login to your Amazon account first.')));

const Shows = React.memo(({shows}) => {
    return form(fieldset(
        legend('Shows'),
        p(select(...shows.shows.map(show =>
            option({value: show.id}, show.title)))),
        p(input({type: 'submit'})),
        jsx(JsonAceEditor, {json: shows})));
});

const App = React.memo(({api}) => {
    const [shows, setShows] = React.useState(null);
    React.useEffect(() => void api.listShows().then(setShows), [api]);

    if (shows === null) {
        return p('Loading...');
    }
    else if (shows.errors) {
        return jsx(LoginLink);
    }
    else {
        return jsx(Shows, {shows: shows});
    }
});

const api = new Api();

ReactDOM.render(jsx(App, {api: api}), rootEl);
