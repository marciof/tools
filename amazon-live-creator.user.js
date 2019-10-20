// ==UserScript==
// @name Amazon Live Creator
// @icon https://www.amazon.com/favicon.ico
// @match https://amazonlivetools.amazon.com/
// @run-at document-start
// @grant GM_info
// @grant GM_getResourceText
// @grant GM_addStyle
// @resource bootstrap-css https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.3.1/css/bootstrap.min.css
// @require https://cdnjs.cloudflare.com/ajax/libs/react/16.10.2/umd/react.development.js
// @require https://cdnjs.cloudflare.com/ajax/libs/react-dom/16.10.2/umd/react-dom.development.js
// @require https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.15/lodash.js
// @require https://cdnjs.cloudflare.com/ajax/libs/classnames/2.2.6/index.min.js
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
rootEl.className = 'p-3';
GM_addStyle(GM_getResourceText('bootstrap-css'));

require.config({
    paths: {
        ace: ['https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.6/'],
    },
});

const acePromise = new Promise((resolve, reject) => {
    require(['ace/ace'], () => {
        const ace = unsafeWindow.ace;
        console.info('ACE editor', ace);
        resolve(ace);
    }, reject);
});

/**
 * @returns {boolean}
 * @see https://github.com/facebook/react/blob/master/packages/react/src/ReactElement.js `isValidElement`
 */
function isJsxElement(value) {
    const isPlainObject = _.isPlainObject(value);

    return !isPlainObject
        || (isPlainObject
            && ('$$typeof' in value)
            && _.isSymbol(value.$$typeof));
}

/**
 *
 * @param tag {string|React.Component}
 * @param [props] {Object}
 * @param children {Array<string|React.Element>}
 * @returns {React.Element}
 */
function jsx(tag, props, ...children) {
    if (isJsxElement(props)) {
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
     * @param broadcastId {string}
     * @returns {string}
     */
    getBroadcastSlateImageUrl(broadcastId) {
        return this.urlPathPrefix
            + 'broadcasts/'
            + encodeURIComponent(broadcastId)
            + '/image/slate';
    }

    /**
     * @param broadcastId {string}
     * @returns {Promise<Object>}
     */
    readBroadcast(broadcastId) {
        return this.request('broadcasts/' + encodeURIComponent(broadcastId));
    }

    /**
     * @param showId {string}
     * @returns {Promise<Object>}
     */
    readShowLiveData(showId) {
        return this.request(
            'poller?fields=showLiveData&showId=' + encodeURIComponent(showId));
    }

    /**
     * @param showId {string}
     * @param [nextToken] {string}
     * @returns {Promise<Object>}
     */
    listShowBroadcasts(showId, nextToken) {
        return this.request(
            'shows/'
            + encodeURIComponent(showId)
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

const details = jsx.bind(null, 'details');
const summary = jsx.bind(null, 'summary');
const label = jsx.bind(null, 'label');
const p = jsx.bind(null, 'p');
const a = jsx.bind(null, 'a');
const b = jsx.bind(null, 'b');
const div = jsx.bind(null, 'div');
const span = jsx.bind(null, 'span');
const img = jsx.bind(null, 'img');
const form = jsx.bind(null, 'form');
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
const useCallback = React.useCallback.bind(React);
const useRef = React.useRef.bind(React);
const useEffect = React.useEffect.bind(React);
const Fragment = jsx.bind(null, React.Fragment);

const VIDEO_SOURCES = {
    PHONE_CAMERA: 'Phone camera',
    THIRD_PARTY_ENCODER: 'Encoder',
};

function useToggleState(isEnabledAtStart) {
    const [isEnabled, setIsEnabled] = useState(isEnabledAtStart);
    const toggleIsEnabled = useCallback(
        () => void setIsEnabled(prevIsEnabled => !prevIsEnabled));

    return [isEnabled, toggleIsEnabled];
}

const AceEditor = memo(function AceEditor({text, mode, style}) {
    const [ace, setAce] = useState(null);
    const [editor, setEditor] = useState(null);
    const editorElRef = useRef(null);

    useEffect(() => void acePromise.then(setAce));

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

const JsonAceEditor = memo(function JsonAceEditor({json, style}) {
    return jsx(AceEditor, {
        text: JSON.stringify(json, undefined, 4),
        mode: 'ace/mode/json',
        style: {
            width: '100%',
            height: '200px',
            border: '1px solid lightgray',
            ...style,
        },
    });
});

const BroadcastPageLink = memo(function BroadcastPageLink({id, title}) {
    return a({href: 'https://www.amazon.com/live/broadcast/' + id}, title);
});

const LoginLink = memo(function LoginLink() {
    return p(a(
        {href: 'https://www.amazon.com/gp/sign-in.html'},
        'Please login to your Amazon account first.'));
});

// FIXME: convert UTC to local?
// FIXME: make read-only?
const DateTime = memo(function DateTime({dateTime}) {
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

const Id = memo(function Id({id}) {
    return span({className: 'text-nowrap text-monospace'}, id);
});

const Shows = memo(function Shows({data, onLoadLiveData, onListBroadcasts}) {
    const [selectedShow, setSelectedShow] = useState(null);
    const [isJsonShown, toggleIsJsonShown] = useToggleState(false);

    useEffect(() => {
        if (data && data.shows && (data.shows.length > 0)) {
            let show = data.shows[0];
            setSelectedShow(show);
            onLoadLiveData(show.id);
            onListBroadcasts(show.id);
        }
    }, [data]);

    if (data.errors) {
        return jsx(LoginLink);
    }

    return form(
        div({className: 'card mb-3'}, div({className: 'table-responsive'},
            table(
                {className: 'table table-striped table-sm table-hover table-borderless mb-0'},
                thead(
                    tr(
                        th({colSpan: 2}, 'ID'),
                        th('Title'),
                        th('Distribution'),
                        th('Feature Group'))),
                tbody(data.shows.map(show =>
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
                            jsx(Id, {id: show.id}))),
                        td(a({
                            href: 'https://www.amazon.com/live/channel/' + show.id,
                        }, show.title)),
                        td(show.distribution),
                        td(show.featureGroup))))))),
        p(
            button({
                disabled: !selectedShow,
                type: 'button',
                className: 'btn btn-primary mr-3',
                onClick() {
                    onListBroadcasts(selectedShow.id);
                }
            }, 'List broadcasts'),
            button({
                disabled: !selectedShow,
                type: 'button',
                className: 'btn btn-primary mr-3',
                onClick() {
                    onLoadLiveData(selectedShow.id);
                }
            }, 'Load live data'),
            button({
                type: 'button',
                disabled: !selectedShow,
                className: 'btn btn-info',
                onClick: toggleIsJsonShown,
            }, 'Show/Hide JSON')),
        selectedShow && jsx(JsonAceEditor, {
            json: selectedShow,
            style: {display: isJsonShown ? 'inherit' : 'none'},
        }));
});

const Broadcasts = memo(function Broadcasts(props) {
    const {data, onLoadMore, onLoadBroadcast} = props;
    const [selectedBroadcast, setSelectedBroadcast] = useState(null);
    const [isLoadingMore, setIsLoadingMore] = useState(false);
    const [isJsonShown, toggleIsJsonShown] = useToggleState(false);

    useEffect(() => void setIsLoadingMore(false), [data]);

    return form(
        div({className: 'card mb-3'}, div({className: 'table-responsive'},
            table(
                {className: 'table table-striped table-sm table-hover table-borderless mb-0'},
                thead(
                    tr(
                        th({colSpan: 2}, 'ID'),
                        th('Title'),
                        th('ASIN'),
                        th('Distribution'),
                        th('Stage'),
                        th('Started'),
                        th('Ended'))),
                tbody(data.broadcasts.map(broadcast =>
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
                            jsx(Id, {id: broadcast.id}))),
                        td(jsx(BroadcastPageLink, {
                            id: broadcast.id,
                            title: broadcast.title,
                        })),
                        td(jsx(Id, {id: broadcast.asin})),
                        td(broadcast.distribution),
                        td(broadcast.stage),
                        td(broadcast.broadcastStartDateTime && jsx(DateTime, {
                            dateTime: broadcast.broadcastStartDateTime,
                        })),
                        td(broadcast.broadcastEndDateTime && jsx(DateTime, {
                            dateTime: broadcast.broadcastEndDateTime,
                        })))))))),
        p(
            button({
                type: 'button',
                disabled: !selectedBroadcast,
                className: 'btn btn-primary mr-3',
                onClick() {
                    onLoadBroadcast(selectedBroadcast.id);
                }
            }, 'Load broadcast'),
            button(
                {
                    disabled: !data.nextLink || isLoadingMore,
                    type: 'button',
                    className: 'btn btn-secondary mr-3',
                    onClick() {
                        setIsLoadingMore(true);
                        onLoadMore(data.nextLink);
                    }
                },
                'Load more broadcasts',
                isLoadingMore && Fragment(
                    ' ', span({className: 'spinner-border spinner-border-sm'}))),
            button({
                type: 'button',
                disabled: !selectedBroadcast,
                className: 'btn btn-info',
                onClick: toggleIsJsonShown,
            }, 'Show/Hide JSON')),
        selectedBroadcast && jsx(JsonAceEditor, {
            json: selectedBroadcast,
            style: {display: isJsonShown ? 'inherit' : 'none'},
        }));
});

const LiveData = memo(function LiveData({data, onLoadBroadcast}) {
    const [isJsonShown, toggleIsJsonShown] = useToggleState(false);

    const {
        broadcastStartedId,
        lockedBroadcastId,
        lockedBroadcastState,
        lvsLastMessageSubject,
    } = data.showLiveData.value;

    const broadcastId = broadcastStartedId || lockedBroadcastId;
    const state = lockedBroadcastState || lvsLastMessageSubject;

    return form(
        div({className: 'card mb-3'}, div({className: 'table-responsive'},
            table(
                {className: 'table table-striped table-sm table-hover table-borderless mb-0'},
                thead(
                    tr(
                        th('ID'),
                        th('State'),
                        th('Status'))),
                tbody(
                    tr(
                        td(broadcastId && jsx(Id, {id: broadcastId})),
                        td(!broadcastId ? state : jsx(BroadcastPageLink, {
                            id: broadcastId,
                            title: state})),
                        td(data.showLiveData.status)))))),
        p(
            button({
                type: 'button',
                disabled: !broadcastId,
                className: 'btn btn-primary mr-3',
                onClick() {
                    onLoadBroadcast(broadcastId);
                },
            }, 'Load broadcast'),
            button({
                type: 'button',
                className: 'btn btn-info',
                onClick: toggleIsJsonShown,
            }, 'Show/Hide JSON')),
        jsx(JsonAceEditor, {
            json: data,
            style: {display: isJsonShown ? 'inherit' : 'none'},
        }));
});

const Broadcast = memo(function Broadcast({data, getSlateImageUrl}) {
    const [broadcast, setBroadcast] = useState(data);
    const [isJsonShown, toggleIsJsonShown] = useToggleState(false);

    useEffect(() => void setBroadcast(data), [data]);

    return form(
        p(img({
            src: getSlateImageUrl(broadcast.id),
            height: '100px',
        })),
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
        p(button({
            type: 'button',
            className: 'btn btn-info',
            onClick: toggleIsJsonShown,
        }, 'Show/Hide JSON')),
        jsx(JsonAceEditor, {
            json: broadcast,
            style: {display: isJsonShown ? 'inherit' : 'none'}
        }));
});

/**
 * @param Component {React.Component}
 * @returns {React.Component}
 */
function lazy(Component) {
    return memo(function LazyComponent(props) {
        const {title, promise, reducer, ...componentProps} = props;
        const [data, setData] = useState(null);
        const [isLoading, setIsLoading] = useState(true);

        useEffect(() => {
            setIsLoading(true);
            promise.then(newData => {
                setData(data && reducer ? reducer(data, newData) : newData);
                setIsLoading(false);
            });
        }, [promise]);

        return details(
            {className: 'mb-4', open: true},
            summary(
                {className: 'font-weight-bold h4'},
                title, ' ',
                span(
                    {className: classNames(
                        'badge', 'badge-secondary', 'badge-pill',
                        {invisible: !isLoading || !data})},
                    'refreshing...')),
            !data
                ? p(
                    span({className: 'spinner-border spinner-border-sm'}),
                    ' Loading...')
                : jsx(Component, {data, ...componentProps}));
    });
}

function concatBroadcasts(oldData, newData) {
    return {
        broadcasts: oldData.broadcasts.concat(newData.broadcasts),
        nextLink: newData.nextLink,
    };
}

const LazyShows = lazy(Shows);
const LazyLiveData = lazy(LiveData);
const LazyBroadcasts = lazy(Broadcasts);
const LazyBroadcast = lazy(Broadcast);

const App = memo(function App({api}) {
    const [showsPromise,] = useState(() => api.listShows());
    const [liveDataPromise, setLiveDataPromise] = useState(null);
    const [isLoadingMoreBroadcasts, setIsLoadingMoreBroadcasts] = useState(false);
    const [broadcastsShowId, setBroadcastsShowId] = useState(null);
    const [broadcastsPromise, setBroadcastsPromise] = useState(null);
    const [broadcastPromise, setBroadcastPromise] = useState(null);

    return Fragment(
        jsx(LazyShows, {
            title: 'Shows',
            promise: showsPromise,
            onLoadLiveData(showId) {
                setLiveDataPromise(api.readShowLiveData(showId));
            },
            onListBroadcasts(showId) {
                setIsLoadingMoreBroadcasts(false);
                setBroadcastsShowId(showId);
                setBroadcastsPromise(api.listShowBroadcasts(showId));
            },
        }),
        liveDataPromise && jsx(LazyLiveData, {
            title: 'Live Data',
            promise: liveDataPromise,
            onLoadBroadcast(broadcastId) {
                setBroadcastPromise(api.readBroadcast(broadcastId));
            },
        }),
        broadcastsShowId && broadcastsPromise && jsx(LazyBroadcasts, {
            title: 'Broadcasts',
            promise: broadcastsPromise,
            reducer: isLoadingMoreBroadcasts ? concatBroadcasts : null,
            onLoadMore(nextToken) {
                setIsLoadingMoreBroadcasts(true);
                setBroadcastsPromise(
                    api.listShowBroadcasts(broadcastsShowId, nextToken));
            },
            onLoadBroadcast(broadcastId) {
                setBroadcastPromise(api.readBroadcast(broadcastId));
            },
        }),
        broadcastPromise && jsx(LazyBroadcast, {
            title: 'Broadcast',
            promise: broadcastPromise,
            getSlateImageUrl(broadcastId) {
                return api.getBroadcastSlateImageUrl(broadcastId);
            }
        }));
});

const shouldRun = /Violentmonkey/i.test(GM_info.scriptHandler)
    || confirm('Unsupported UserScript manager. Continue?');

// FIXME: use error boundary with error message?
// FIXME: use functions for initial state in useState?
// FIXME: spinner in buttons as well as disabled while loading?
// FIXME: table spacing when there's <code/>? or <input/>?
// FIXME: use callback for perf?
if (shouldRun) {
    ReactDOM.render(jsx(App, {api: new Api()}), rootEl);
}
