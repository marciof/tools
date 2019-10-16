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

    const faviconLink
        = document.querySelector('link[rel*=icon]')
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
            + (!nextToken
                ? ''
                : '&nextToken=' + encodeURIComponent(nextToken)));
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

const VIDEO_SOURCES = {
    PHONE_CAMERA: 'Phone camera',
    THIRD_PARTY_ENCODER: 'Encoder',
};

const AceEditor = memo(({text, mode, style}) => {
    const [ace, setAce] = useState(null);
    const [editor, setEditor] = useState(null);
    const editorElRef = useRef(null);

    useEffect(() => void acePromise.then(setAce), []);

    useEffect(() => {
        if (ace) {
            const editor = ace.edit(editorElRef.current);
            editor.setTheme('ace/theme/github');
            editor.session.setMode(mode);
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

const JsonAceEditor = memo(({json, style}) => jsx(AceEditor, {
    text: JSON.stringify(json, undefined, 4),
    mode: 'ace/mode/json',
    style: {
        width: '100%',
        height: '200px',
        border: '1px solid lightgray',
        ...style,
    },
}));

const Loading = memo(() => p('Loading...'));

const BroadcastLivestreamLink = memo(({id, title}) => a(
    {
        href: 'https://www.amazon.com/live/broadcast/' + id,
        target: '_blank',
    },
    title));

const LoginLink = memo(() => p(a(
    {
        href: 'https://www.amazon.com/gp/sign-in.html',
        target: '_blank',
    },
    'Please login to your Amazon account first.')));

// FIXME: remove hardcoded API URL path
const BroadcastSlateImage = memo(({id}) => img({
    src: '/api/v1/broadcasts/' + encodeURIComponent(id) + '/image/slate',
    height: '100px',
}));

// FIXME: convert UTC to local?
// FIXME: make read-only?
const DateTime = memo(({dateTime}) => {
    const [date, zonedTime] = dateTime.split('T');
    const time = zonedTime.replace(/\.\d+Z$/, '');

    return Fragment(
        input({
            type: 'date',
            defaultValue: date,
        }),
        ' ',
        input({
            type: 'time',
            defaultValue: time,
        }));
});

const Shows = memo(({promise, onShowLiveData, onListShowBroadcasts}) => {
    const [shows, setShows] = useState(null);
    const [selectedShow, setSelectedShow] = useState(null);
    const [isJsonShown, setIsJsonShown] = useState(false);

    useEffect(() => void promise.then(setShows), [promise]);

    useEffect(() => {
        if (shows && shows.shows && (shows.shows.length > 0)) {
            let show = shows.shows[0];
            setSelectedShow(show);
            onShowLiveData(show.id);
            onListShowBroadcasts(show.id);
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
                        th({colSpan: 2}, 'ID'),
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
                                href: 'https://www.amazon.com/live/channel/'
                                    + show.id,
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
                            onListShowBroadcasts(selectedShow.id);
                        }
                    },
                    'List broadcasts'),
                button(
                    {
                        disabled: !selectedShow,
                        type: 'button',
                        onClick() {
                            onShowLiveData(selectedShow.id);
                        }
                    },
                    'Load live data'),
                button(
                    {
                        type: 'button',
                        disabled: !selectedShow,
                        onClick() {
                            setIsJsonShown(prevIsJsonShown => !prevIsJsonShown);
                        }
                    },
                    'Show/Hide JSON')),
            selectedShow && jsx(JsonAceEditor, {
                json: selectedShow,
                style: {
                    display: isJsonShown ? 'inherit' : 'none',
                },
            }));
    }

    return fieldset(legend('Shows'), children);
});

const Broadcasts = memo(props => {
    const {promise, morePromise, onLoadMore, onLoadBroadcast} = props;

    const [broadcasts, setBroadcasts] = useState(null);
    const [selectedBroadcast, setSelectedBroadcast] = useState(null);
    const [isLoadingMore, setIsLoadingMore] = useState(false);
    const [isJsonShown, setIsJsonShown] = useState(false);

    useEffect(() => {
        setBroadcasts(null);
        promise.then(setBroadcasts);
    }, [promise]);

    useEffect(() => {
        if (morePromise) {
            setIsLoadingMore(true);

            morePromise.then(moreBroadcasts => {
                setIsLoadingMore(false);

                setBroadcasts(prevBroadcasts => ({
                    broadcasts: prevBroadcasts.broadcasts.concat(
                        moreBroadcasts.broadcasts),
                    nextLink: moreBroadcasts.nextLink,
                }));
            });
        }
    }, [morePromise]);

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
                        th({colSpan: 2}, 'ID'),
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
                        td(jsx(DateTime, {
                            dateTime: broadcast.broadcastStartDateTime,
                        })),
                        td(broadcast.broadcastEndDateTime && jsx(DateTime, {
                            dateTime: broadcast.broadcastEndDateTime,
                        })))))),
            p(
                button(
                    {
                        type: 'button',
                        disabled: !selectedBroadcast,
                        onClick() {
                            onLoadBroadcast(selectedBroadcast.id);
                        }
                    },
                    'Load broadcast'),
                button(
                    {
                        disabled: !broadcasts.nextLink || isLoadingMore,
                        type: 'button',
                        onClick() {
                            onLoadMore(broadcasts.nextLink);
                        }
                    },
                    'Load more broadcasts'),
                button(
                    {
                        type: 'button',
                        disabled: !selectedBroadcast,
                        onClick() {
                            setIsJsonShown(prevIsJsonShown => !prevIsJsonShown);
                        }
                    },
                    'Show/Hide JSON')),
            selectedBroadcast && jsx(JsonAceEditor, {
                json: selectedBroadcast,
                style: {
                    display: isJsonShown ? 'inherit' : 'none',
                },
            }));
    }

    return fieldset(legend('Broadcasts'), children);
});

const ShowLiveData = memo(({promise, onLoadBroadcast}) => {
    const [liveData, setLiveData] = useState(null);
    const [broadcastId, setBroadcastId] = useState(null);
    const [isJsonShown, setIsJsonShown] = useState(false);

    useEffect(() => {
        setLiveData(null);
        promise.then(setLiveData);
    }, [promise]);

    useEffect(() => {
        if (liveData) {
            const {
                broadcastStartedId,
                lockedBroadcastId,
            } = liveData.showLiveData.value;

            setBroadcastId(broadcastStartedId || lockedBroadcastId);
        }
    }, [liveData]);

    let children;

    if (!liveData) {
        children = jsx(Loading);
    }
    else {
        const {
            lockedBroadcastState,
            lvsLastMessageSubject,
        } = liveData.showLiveData.value;

        const state = lockedBroadcastState || lvsLastMessageSubject;

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
                        td(broadcastId && code(broadcastId)),
                        td(broadcastId
                            ? jsx(BroadcastLivestreamLink, {
                                id: broadcastId,
                                title: state})
                            : state),
                        td(liveData.showLiveData.status)))),
            p(
                button(
                    {
                        type: 'button',
                        disabled: !broadcastId,
                        onClick() {
                            onLoadBroadcast(broadcastId);
                        },
                    },
                    'Load broadcast'),
                button(
                    {
                        type: 'button',
                        onClick() {
                            setIsJsonShown(prevIsJsonShown => !prevIsJsonShown);
                        }
                    },
                    'Show/Hide JSON')),
            jsx(JsonAceEditor, {
                json: liveData,
                style: {
                    display: isJsonShown ? 'inherit' : 'none',
                },
            }));
    }

    return fieldset(legend('Live Data'), children);
});

const Broadcast = memo(({promise}) => {
    const [broadcast, setBroadcast] = useState(null);
    const [isJsonShown, setIsJsonShown] = useState(false);

    useEffect(() => {
        setBroadcast(null);
        promise.then(setBroadcast);
    }, [promise]);

    let children;

    if (!broadcast) {
        children = jsx(Loading);
    }
    else {
        children = form(
            p(jsx(BroadcastSlateImage, {id: broadcast.id})),
            p(label('Title: ', input({
                type: 'text',
                value: broadcast.title,
                onChange(event) {
                    const title = event.target.value;

                    setBroadcast(prevBroadcast => ({
                        ...prevBroadcast,
                        title: title,
                    }));
                }
            }))),
            p('Video source: ',
                Object.entries(VIDEO_SOURCES).map(([value, text]) =>
                    label({key: value}, input({
                        type: 'radio',
                        name: 'videoSource',
                        value: value,
                        checked: broadcast.videoSource === value,
                        onChange() {
                            setBroadcast(prevBroadcast => ({
                                ...prevBroadcast,
                                videoSource: value,
                            }));
                        },
                    }), text))),
            p(button(
                {
                    type: 'button',
                    onClick() {
                        setIsJsonShown(prevIsJsonShown => !prevIsJsonShown);
                    }
                },
                'Show/Hide JSON')),
            jsx(JsonAceEditor, {
                json: broadcast,
                style: {
                    display: isJsonShown ? 'inherit' : 'none',
                }
            }));
    }

    return fieldset(legend('Broadcast'), children);
});

const App = memo(({api}) => {
    const [showsPromise,] = useState(() => api.listShows());
    const [liveDataPromise, setLiveDataPromise] = useState(null);

    const [broadcastsShowId, setBroadcastsShowId] = useState(null);
    const [broadcastsPromise, setBroadcastsPromise] = useState(null);
    const [moreBroadcastsPromise, setMoreBroadcastsPromise] = useState(null);

    const [broadcastPromise, setBroadcastPromise] = useState(null);

    return Fragment(
        jsx(Shows, {
            promise: showsPromise,
            onShowLiveData(showId) {
                setLiveDataPromise(api.readShowLiveData(showId));
            },
            onListShowBroadcasts(showId) {
                setBroadcastsShowId(showId);
                setBroadcastsPromise(api.listShowBroadcasts(showId));
            },
        }),
        liveDataPromise && jsx(ShowLiveData, {
            promise: liveDataPromise,
            onLoadBroadcast(broadcastId) {
                setBroadcastPromise(api.readBroadcast(broadcastId));
            },
        }),
        broadcastsShowId && broadcastsPromise && jsx(Broadcasts, {
            promise: broadcastsPromise,
            morePromise: moreBroadcastsPromise,
            onLoadMore(nextToken) {
                setMoreBroadcastsPromise(
                    api.listShowBroadcasts(broadcastsShowId, nextToken));
            },
            onLoadBroadcast(broadcastId) {
                setBroadcastPromise(api.readBroadcast(broadcastId));
            },
        }),
        broadcastPromise && jsx(Broadcast, {
            promise: broadcastPromise,
        }));
});

const shouldRun = /Violentmonkey/i.test(GM_info.scriptHandler)
    || confirm('Unsupported UserScript manager. Continue?');

if (shouldRun) {
    // FIXME: use error boundary with error message?
    // FIXME: use functions for initial state in useState?
    ReactDOM.render(jsx(App, {api: new Api()}), rootEl);
}
