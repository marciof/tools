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
        const ace = unsafeWindow.ace;
        console.info('ACE editor', ace);
        return resolve(ace);
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
    return React.createElement(tag, props, ...children);
}

class Api {
    constructor() {
        this.urlPathPrefix = '/api/v1/';
    }

    /**
     * @param id {string}
     * @returns {string}
     */
    getBroadcastSlateImageUrl(id) {
        return this.urlPathPrefix
            + 'broadcasts/'
            + encodeURIComponent(id)
            + '/image/slate';
    }

    /**
     * @param id {string}
     * @returns {Promise<Object>}
     */
    readBroadcast(id) {
        return this.request('broadcasts/' + encodeURIComponent(id));
    }

    /**
     * @param id {string}
     * @returns {Promise<Object>}
     */
    readShowLiveData(id) {
        return this.request(
            'poller?fields=showLiveData&showId=' + encodeURIComponent(id));
    }

    /**
     * @param id {string}
     * @param [nextToken] {string}
     * @returns {Promise<Object>}
     */
    listShowBroadcasts(id, nextToken) {
        return this.request(
            'shows/'
            + encodeURIComponent(id)
            + '/broadcasts/?direction=all&ascending=true&maxResults=10'
            + (!nextToken ? '' : '&nextToken=' + encodeURIComponent(nextToken)));
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

        return response.json();
    }
}

const fieldset = jsx.bind(null, 'fieldset');
const legend = jsx.bind(null, 'legend');
const label = jsx.bind(null, 'label');
const p = jsx.bind(null, 'p');
const a = jsx.bind(null, 'a');
const b = jsx.bind(null, 'b');
const div = jsx.bind(null, 'div');
const img = jsx.bind(null, 'img');
const form = jsx.bind(null, 'form');
const code = jsx.bind(null, 'code');
const input = jsx.bind(null, 'input');
const button = jsx.bind(null, 'button');
const table = jsx.bind(null, 'table');
const thead = jsx.bind(null, 'thead');
const tbody = jsx.bind(null, 'tbody');
const tr = jsx.bind(null, 'tr');
const th = jsx.bind(null, 'th');
const td = jsx.bind(null, 'td');

const memo = React.memo.bind(React);
const useState = React.useState.bind(React);
const useRef = React.useRef.bind(React);
const useEffect = React.useEffect.bind(React);
const Fragment = jsx.bind(null, React.Fragment);

const AceEditor = memo(({text, style}) => {
    const [ace, setAce] = useState(null);
    const [editor, setEditor] = useState(null);
    const editorElRef = useRef(null);

    useEffect(() => void acePromise.then(setAce), []);

    useEffect(() => {
        if (ace) {
            const editor = ace.edit(editorElRef.current);
            editor.setTheme("ace/theme/github");
            editor.session.setMode("ace/mode/json");
            setEditor(editor);
        }
    }, [ace]);

    useEffect(() => {
        if (editor) {
            editor.setValue(text, 1);
        }
    }, [editor, text]);

    return div({ref: editorElRef, style: style});
});

const JsonAceEditor = memo(({json}) => {
    return jsx(AceEditor, {
        style: {
            width: '100%',
            height: '200px',
            border: '1px solid lightgray',
        },
        text: JSON.stringify(json, undefined, 4)
    });
});

const Loading = memo(() => p('Loading...'));

const BroadcastLivestreamLink = memo(({id, title}) => {
    return a(
        {
            href: 'https://www.amazon.com/live/broadcast/' + id,
            target: '_blank',
        },
        title);
});

const LoginLink = React.memo(() =>
    p(a({
            href: 'https://www.amazon.com/gp/sign-in.html',
            target: '_blank',
        },
        'Please login to your Amazon account first.')));

const Shows = memo(({api, onSelectedShowId}) => {
    const [shows, setShows] = useState(null);
    const [selectedShow, setSelectedShow] = useState(null);

    useEffect(() => void api.listShows().then(setShows), [api]);

    useEffect(() => {
        if (shows && shows.shows && (shows.shows.length === 1)) {
            let show = shows.shows[0];
            setSelectedShow(show);
            onSelectedShowId(show.id);
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
        children = form(
            table(
                {border: 1},
                thead(
                    tr(
                        th(),
                        th('ID'),
                        th('Title'),
                        th('Distribution'),
                        th('Feature Group'))),
                tbody(shows.shows.map(show =>
                    tr(
                        {key: show.id},
                        td(input({
                            type: 'radio',
                            id: 'show-' + show.id,
                            name: 'showId',
                            value: show.id,
                            checked: selectedShow === show,
                            onChange() {
                                setSelectedShow(show);
                            },
                        })),
                        td(label(
                            {htmlFor: 'show-' + show.id},
                            code(show.id))),
                        td(a(
                            {
                                href: 'https://www.amazon.com/live/channel/' + show.id,
                                target: '_blank',
                            },
                            show.title)),
                        td(show.distribution),
                        td(show.featureGroup))))),
            p(
                button(
                    {
                        disabled: !selectedShow,
                        type: 'button',
                        onClick() {
                            onSelectedShowId(selectedShow.id);
                        }
                    },
                    'Load selected show'),
                button(
                    {
                        type: 'button',
                        disabled: true,
                    },
                    'Show selected JSON')));
    }

    return fieldset(legend('Shows'), children);
});

const Broadcasts = memo(({api, showId, onSelectedBroadcastId}) => {
    const [broadcasts, setBroadcasts] = useState(null);
    const [selectedBroadcast, setSelectedBroadcast] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(
        () => void api.listShowBroadcasts(showId).then(setBroadcasts),
        [api, showId]);

    useEffect(() => void setIsLoading(false), [broadcasts]);

    let children;

    if (!broadcasts) {
        children = jsx(Loading);
    }
    else {
        children = form(
            table(
                {border: 1},
                thead(
                    tr(
                        th(),
                        th('ID'),
                        th('Title'),
                        th('ASIN'),
                        th('Started'),
                        th('Ended'))),
                tbody(broadcasts.broadcasts.map(broadcast =>
                    tr(
                        {key: broadcast.id},
                        td(input({
                            type: 'radio',
                            id: 'broadcast-' + broadcast.id,
                            name: 'broadcastId',
                            value: broadcast.id,
                            checked: selectedBroadcast === broadcast,
                            onChange(event) {
                                setSelectedBroadcast(broadcast);
                            }
                        })),
                        td(label(
                            {htmlFor: 'broadcast-' + broadcast.id},
                            code(broadcast.id))),
                        td(jsx(BroadcastLivestreamLink, {
                            id: broadcast.id,
                            title: broadcast.title,
                        })),
                        td(broadcast.asin),
                        td(broadcast.broadcastStartDateTime),
                        td(broadcast.broadcastEndDateTime))))),
            p(
                button(
                    {
                        type: 'button',
                        disabled: !selectedBroadcast,
                        onClick() {
                            onSelectedBroadcastId(selectedBroadcast.id);
                        }
                    },
                    'Load selected broadcast'),
                broadcasts.nextLink && button(
                    {
                        disabled: isLoading,
                        type: 'button',
                        onClick() {
                            setIsLoading(true);
                            api.listShowBroadcasts(showId, broadcasts.nextLink)
                                .then(moreBroadcasts => {
                                    setBroadcasts({
                                        nextLink: moreBroadcasts.nextLink,
                                        broadcasts: broadcasts.broadcasts.concat(moreBroadcasts.broadcasts),
                                    });
                                });
                        }
                    },
                    'Load more broadcasts'),
                button(
                    {
                        type: 'button',
                        disabled: true,
                    },
                    'Show selected JSON')));
    }

    return fieldset(legend('Broadcasts'), children);
});

const ShowLiveData = memo(({api, id, onSelectedBroadcastId}) => {
    const [liveData, setLiveData] = useState(null);
    const [broadcastId, setBroadcastId] = useState(null);

    useEffect(
        () => void api.readShowLiveData(id).then(setLiveData),
        [api, id]);

    useEffect(() => {
        if (liveData) {
            const {
                broadcastStartedId,
                lockedBroadcastId,
            } = liveData.showLiveData.value;

            setBroadcastId(broadcastStartedId || lockedBroadcastId);
        }
    }, [liveData]);

    useEffect(() => {
        if (broadcastId) {
            onSelectedBroadcastId(broadcastId);
        }
    }, [broadcastId]);

    let children;

    if (!liveData) {
        children = jsx(Loading);
    }
    else {
        const {
            lockedBroadcastState,
            lvsLastMessageSubject,
        } = liveData.showLiveData.value;

        const state = lockedBroadcastState || lvsLastMessageSubject || 'N/A';

        children = form(
            table(
                {border: 1},
                thead(
                    tr(
                        th('ID'),
                        th('State'),
                        th('Status'))),
                tbody(
                    tr(
                        td(broadcastId ? code(broadcastId) : 'N/A'),
                        td(broadcastId
                            ? jsx(BroadcastLivestreamLink, {
                                id: broadcastId,
                                title: state})
                            : state),
                        td(liveData.showLiveData.status)))),
            p(
                broadcastId && button(
                    {
                        type: 'button',
                        onClick() {
                            onSelectedBroadcastId(broadcastId);
                        },
                    },
                    'Load broadcast'),
                button(
                    {
                        type: 'button',
                        disabled: true,
                    },
                    'Refresh live data'),
                button(
                    {
                        type: 'button',
                        disabled: true,
                    },
                    'Show JSON')));
    }

    return fieldset(legend('Live Data'), children);
});

const Broadcast = memo(({api, id}) => {
    const [broadcast, setBroadcast] = useState(null);
    useEffect(() => void api.readBroadcast(id).then(setBroadcast), [api, id]);

    let children;

    if (!broadcast) {
        children = jsx(Loading);
    }
    else {
        children = Fragment(
            p(img({
                src: api.getBroadcastSlateImageUrl(id),
                height: '100px',
            })),
            p(button(
                {
                    type: 'button',
                    disabled: true,
                },
                'Show JSON')),
            jsx(JsonAceEditor, {json: broadcast}));
    }

    return fieldset(legend('Broadcast'), children);
});

const App = React.memo(({api}) => {
    const [showId, setShowId] = useState(null);
    const [broadcastId, setBroadcastId] = useState(null);

    return Fragment(
        jsx(Shows, {
            api: api,
            onSelectedShowId: setShowId,
        }),
        showId && Fragment(
            jsx(Broadcasts, {
                api: api,
                showId: showId,
                onSelectedBroadcastId: setBroadcastId,
            }),
            jsx(ShowLiveData, {
                api: api,
                id: showId,
                onSelectedBroadcastId: setBroadcastId,
            }),
            broadcastId && jsx(Broadcast, {
                api: api,
                id: broadcastId,
            })));
});

const api = new Api();
const shouldRun = /Violentmonkey/i.test(GM_info.scriptHandler)
    || confirm('Unsupported UserScript manager. Continue?');

if (shouldRun) {
    ReactDOM.render(jsx(App, {api: api}), rootEl);
}
