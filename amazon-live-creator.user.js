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
     * @param id {string}
     * @returns {Promise<Object>}
     */
    readShow(id) {
        return this.request('show/' + id);
    }

    /**
     * @param id {string}
     * @returns {Promise<Object>}
     */
    listBroadcastsByShowId(id) {
        return this.request('shows/' + id + '/broadcasts/');
    }

    /**
     * @returns {Promise<Object>}
     */
    listShows() {
        return this.request('user/shows');
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

        const json = await response.json();
        console.info('API JSON response:', json);
        return json;
    }
}

const fieldset = jsx.bind(null, 'fieldset');
const legend = jsx.bind(null, 'legend');
const label = jsx.bind(null, 'label');
const p = jsx.bind(null, 'p');
const a = jsx.bind(null, 'a');
const b = jsx.bind(null, 'b');
const div = jsx.bind(null, 'div');
const form = jsx.bind(null, 'form');
const select = jsx.bind(null, 'select');
const option = jsx.bind(null, 'option');
const input = jsx.bind(null, 'input');

const memo = React.memo.bind(React);
const useState = React.useState.bind(React);
const useRef = React.useRef.bind(React);
const useEffect = React.useEffect.bind(React);
const Fragment = jsx.bind(null, React.Fragment);

const AceEditor = memo(({children, style}) => {
    const [ace, setAce] = useState(null);
    const editorRef = useRef(null);

    useEffect(() => void acePromise.then(setAce), []);

    useEffect(() => {
        if (ace) {
            const editor = ace.edit(editorRef.current);
            editor.setTheme("ace/theme/github");
            editor.session.setMode("ace/mode/json");
        }
    }, [ace]);

    return div({ref: editorRef, style: style}, children);
});

const JsonAceEditor = memo(({json}) => {
    return jsx(AceEditor,
        {
            style: {
                width: '100%',
                height: '250px',
                border: '1px solid gray',
            },
        },
        JSON.stringify(json, undefined, 4));
});

const Loading = memo(() => p('Loading...'));

const Shows = memo(({api, selectShowById}) => {
    const [shows, setShows] = useState(null);
    useEffect(() => void api.listShows().then(setShows), [api]);

    useEffect(() => {
        if (shows && shows.shows && (shows.shows.length === 1)) {
            selectShowById(shows.shows[0].id);
        }
    }, [shows]);

    let children;

    if (!shows) {
        children = jsx(Loading);
    }
    else if (shows.errors) {
        children = jsx(LoginLink);
    }
    else {
        children = Fragment(
            form(
                {
                    onSubmit(event) {
                        event.preventDefault();
                        selectShowById(event.target.elements.show.value);
                    },
                },
                p(select(
                    {name: 'show'},
                    ...shows.shows.map(show =>
                        option({value: show.id}, show.title)))),
                p(input({type: 'submit'}))),
            jsx(JsonAceEditor, {json: shows}));
    }

    return fieldset(legend('Shows'), children);
});

const Broadcasts = memo(({api, showId}) => {
    const [broadcasts, setBroadcasts] = useState(null);

    useEffect(
        () => void api.listBroadcastsByShowId(showId).then(setBroadcasts),
        [api, showId]);

    let children;

    if (!broadcasts) {
        children = jsx(Loading);
    }
    else {
        children = Fragment(
            form(
                {
                    onSubmit(event) {
                        event.preventDefault();
                    }
                },
                p(select(
                    {name: 'broadcast'},
                    ...broadcasts.broadcasts.map(broadcast =>
                        option({value: broadcast.id}, broadcast.title))))),
            jsx(JsonAceEditor, {json: broadcasts}));
    }

    return fieldset(legend('Broadcasts'), children);
});

const LoginLink = React.memo(() =>
    p(a({href: 'https://www.amazon.com/gp/sign-in.html'},
        'Please login to your Amazon account first.')));

const App = React.memo(({api}) => {
    const [showId, setShowId] = useState(null);

    return Fragment(
        jsx(Shows, {api: api, selectShowById: setShowId}),
        showId && jsx(Broadcasts, {api: api, showId: showId}),
    );
});

const api = new Api();

ReactDOM.render(jsx(App, {api: api}), rootEl);
