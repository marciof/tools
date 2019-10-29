// ==UserScript==
// @name Amazon Live Creator
// @author Márcio
// @version 0.1
// @namespace https://github.com/marciof
// @icon https://www.amazon.com/favicon.ico
// @match https://amazonlivetools.amazon.com/
// @run-at document-start
// @grant GM_info
// @grant GM_addStyle
// ==/UserScript==

// FIXME: add RadioTable footer that knows whether it's empty or not
// FIXME: toggle button active status
// FIXME: split Load Broadcast into a combined two-button? Load / From server
// FIXME: handle empty broadcast/shows list table
// FIXME: don't show Live Data in a table, since it isn't tabular data?
// FIXME: open LazyComponent every time data changes
// FIXME: detect logged in, but no account
// FIXME: type check with eslint and typescript+jsdoc
// FIXME: use more lightweight video player? https://github.com/video-dev/hls.js
// FIXME: fix column widths on the Shows table to prevent content from "jumping"
// FIXME: handle broadcasts with no slate image (lazy load?) (default to show?)
// FIXME: handle errors in lazy loading
// FIXME: table spacing when there's <code/>? or <input/>?
// FIXME: handle videojs JS errors
// FIXME: update broadcast from JSON in Ace editor
// FIXME: use children in Ace editor?
// FIXME: make some JSON Ace editors read-only?
// FIXME: use <label>s instead of onclick+focus?
// FIXME: does Button with tooltip breaks focus?
// FIXME: don't select table row when clicking on links?

// TODO: refactor toggle JSON button
// TODO: use minified versions by default if faster, with dev mode option?
// TODO: refresh live data periodically?
// TODO: show broadcast slate image and video side by side?
// TODO: add a on-hover copy-to-clipboard icon next to IDs and ASINs?
// TODO: sortable tables? datatable
// TODO: searchable tables? datatable
// TODO: add alias for React.Suspense?
// TODO: use functions for initial state in useState?
// TODO: show skeleton by having fake data? cached/mocked while being verified?
// TODO: offline mode? https://www.html5rocks.com/en/mobile/workingoffthegrid/
// TODO: service workers for faster background API calls, downloading CSS/JS?

'use strict';
document.body.textContent = '';
document.title = GM_info.script.name;

/**
 * @param url {string}
 * @returns {Promise<HTMLLinkElement>}
 */
function loadCss(url) {
    return new Promise((resolve, reject) => {
        const linkEl = document.createElement('link');

        linkEl.addEventListener('load', () => {
            console.info('Loaded CSS', linkEl);
            resolve(linkEl);
        });

        linkEl.addEventListener('error', reject);
        linkEl.rel = 'stylesheet';
        linkEl.href = url;

        document.head.appendChild(linkEl);
    });
}

const CDN_BASE_URL = 'https://cdnjs.cloudflare.com/ajax/libs/';

const pageReady = loadCss(CDN_BASE_URL + 'twitter-bootstrap/4.3.1/css/bootstrap.css').then(() => {
    const loadingSpinnerEl = document.createElement('span');
    loadingSpinnerEl.className = 'spinner-border spinner-border-sm';

    const loadingBadgeEl = document.createElement('div');
    loadingBadgeEl.className = 'badge badge-pill badge-info';
    loadingBadgeEl.appendChild(loadingSpinnerEl);
    loadingBadgeEl.appendChild(document.createTextNode(' Loading...'));

    const rootEl = document.createElement('div');
    rootEl.className = 'm-3';
    rootEl.appendChild(loadingBadgeEl);

    document.body.appendChild(rootEl);
    GM_addStyle('.cursor-not-allowed {cursor: not-allowed;}');

    const faviconLink = document.querySelector('link[rel*=icon]')
        || document.createElement('link');

    faviconLink.rel = 'icon';
    faviconLink.href = 'https://www.amazon.com/favicon.ico';
    document.head.appendChild(faviconLink);
    return rootEl;
});

const requireJs = new Promise((resolve, reject) => {
    const scriptEl = document.createElement('script');

    scriptEl.addEventListener('load', () => {
        const {require, define} = unsafeWindow;
        console.info('Loaded require.js/define', require, define);
        resolve([require, define]);
    });

    scriptEl.addEventListener('error', reject);
    scriptEl.src = CDN_BASE_URL + 'require.js/2.3.6/require.js';
    document.head.appendChild(scriptEl);
});

const configuredRequireJs = requireJs.then(([require, define]) => {
    // Workaround video.js bug, https://github.com/videojs/video.js/issues/5680
    define('global/window', [], () => window);
    define('global/document', [], () => document);

    require.config({
        baseUrl: CDN_BASE_URL,
        map: {
            '*': {
                classNames: 'classnames',
                aceEditor: 'ace/ace',
                jQuery: 'jquery',
            },
        },
        shim: {
            bootstrapBundle: {
                deps: ['jQuery'],
            },
        },
        paths: {
            react: ['react/16.10.2/umd/react.development'],
            reactDom: ['react-dom/16.10.2/umd/react-dom.development'],
            lodash: ['lodash.js/4.17.15/lodash'],
            classnames: ['classnames/2.2.6/index'],
            moment: ['moment.js/2.24.0/moment'],
            momentDurationFormat: ['moment-duration-format/2.3.2/moment-duration-format'],
            videoJs: ['video.js/7.6.5/video'],
            ace: ['ace/1.4.6'],
            bootstrapBundle: ['twitter-bootstrap/4.3.1/js/bootstrap.bundle'],
            jquery: ['jquery/3.4.1/jquery'],
        },
    });

    return function loadModule(moduleName) {
        return new Promise((resolve, reject) => {
            require(
                [moduleName],
                module => {
                    console.info('Loaded module ' + moduleName, module);
                    resolve(module);
                },
                reject);
        });
    };
});

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
     * @param showId {string}
     * @returns {string}
     */
    getShowSlateImageUrl(showId) {
        return this.urlPathPrefix
            + 'show/'
            + encodeURIComponent(showId)
            + '/image/slate';
    }

    /**
     * @param broadcastId {string}
     * @returns {Promise<Object>}
     */
    readBroadcast(broadcastId) {
        return this.request(
            'broadcasts/' + encodeURIComponent(broadcastId));
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
     * @returns {Promise<Object>}
     */
    listAccounts() {
        return this.request('user/accounts');
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
            + (nextToken === undefined
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

Promise.all([pageReady, configuredRequireJs]).then(async ([rootEl, module]) => {
    const [React, ReactDOM, lodash, classNames] = await Promise.all([
        module('react'),
        module('reactDom'),
        module('lodash'),
        module('classNames')]);

    /**
     * @returns {boolean}
     * @see https://github.com/facebook/react/blob/master/packages/react/src/ReactElement.js `isValidElement`
     */
    function isJsxElement(value) {
        const isPlainObject = lodash.isPlainObject(value);

        return !isPlainObject
            || (isPlainObject
                && ('$$typeof' in value)
                && lodash.isSymbol(value.$$typeof));
    }

    /**
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

    const details = jsx.bind(null, 'details');
    const summary = jsx.bind(null, 'summary');
    const label = jsx.bind(null, 'label');
    const p = jsx.bind(null, 'p');
    const a = jsx.bind(null, 'a');
    const div = jsx.bind(null, 'div');
    const pre = jsx.bind(null, 'pre');
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
    const video = jsx.bind(null, 'video');

    const memo = React.memo.bind(React);
    const lazy = React.lazy.bind(React);
    const useState = React.useState.bind(React);
    const useCallback = React.useCallback.bind(React);
    const useEffect = React.useEffect.bind(React);
    const Fragment = jsx.bind(null, React.Fragment);

    const VIDEO_SOURCES = {
        PHONE_CAMERA: 'Phone camera',
        THIRD_PARTY_ENCODER: 'Encoder',
    };

    const EMPTY_BROADCAST_DATA = {
        id: '',
        title: '',
        videoSource: 'THIRD_PARTY_ENCODER',
    };

    function hasSelection() {
        const selection = window.getSelection();

        if (selection.rangeCount === 0) {
            return false;
        }

        const range = selection.getRangeAt(0);
        return !range.collapsed;
    }

    function useToggleState(isEnabledAtStart) {
        const [isEnabled, setIsEnabled] = useState(isEnabledAtStart);
        const toggleIsEnabled = useCallback(
            () => void setIsEnabled(prevIsEnabled => !prevIsEnabled));

        return [isEnabled, toggleIsEnabled];
    }

    function fakeModule(defaultExport) {
        return {
            default: defaultExport,
        };
    }

    const LoadingSpinner = memo(function LoadingSpinner(props) {
        const {before, after, ...restProps} = props;

        return span(restProps,
            (before !== undefined) ? Fragment(before, ' ') : null,
            span({className: 'spinner-border text-secondary spinner-border-sm'}),
            (after !== undefined) ? Fragment(' ', after) : null);
    });

    const LazyAceEditor = lazy(async () => {
        const aceEditor = await module('aceEditor');

        return fakeModule(memo(function LazyAceEditor({text, mode, style}) {
            const [editorEl, setEditorEl] = useState(null);
            const [editor, setEditor] = useState(null);
            const editorElRef = useCallback(setEditorEl);

            useEffect(() => {
                if (editorEl) {
                    const newEditor = aceEditor.edit(editorEl);
                    newEditor.setTheme('ace/theme/github');
                    newEditor.getSession().setMode(mode);
                    setEditor(newEditor);
                    return () => newEditor.destroy();
                }
                else {
                    setEditor(null);
                }
            }, [editorEl]);

            useEffect(() => {
                if (editor) {
                    editor.setValue(text, 1);
                }
            }, [editor, text]);

            return div({ref: editorElRef, style: style});
        }));
    });

    const AceEditor = memo(function AceEditor({style, text, ...props}) {
        return jsx(React.Suspense, {
            fallback: jsx(LoadingSpinner, {
                after: pre(text),
                style: {
                    overflow: 'auto',
                    display: 'block',
                    ...style,
                },
            }),
        }, jsx(LazyAceEditor, {style: style, text: text, ...props}));
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

    const LazyVideo = lazy(async () => {
        const [videoJs, ] = await Promise.all([
            module('videoJs'),
            loadCss(CDN_BASE_URL + 'video.js/7.6.5/video-js.css'),
        ]);

        return fakeModule(memo(function LazyVideo({src, height}) {
            const [videoEl, setVideoEl] = useState(null);
            const [player, setPlayer] = useState(null);
            const videoElRef = useCallback(setVideoEl);

            useEffect(() => {
                if (videoEl) {
                    const newPlayer = videoJs(videoEl);
                    setPlayer(newPlayer);
                    return () => newPlayer.dispose();
                }
                else {
                    setPlayer(null);
                }
            }, [videoEl]);

            useEffect(() => {
                if (player && src) {
                    const wasPaused = player.paused();
                    player.src(src);

                    if (!wasPaused) {
                        player.play();
                    }
                }
            }, [player, src]);

            return span(
                {
                    style: {
                        height: height,
                        display: 'block',
                        overflow: 'auto',
                    },
                },
                video({
                    ref: videoElRef,
                    height: height,
                    className: 'video-js',
                    controls: true,
                }));
        }));
    });

    const Video = memo(function Video({src}) {
        const height = '200px';

        return jsx(React.Suspense, {
            fallback: jsx(LoadingSpinner, {
                style: {
                    height: height,
                    overflow: 'auto',
                    display: 'block',
                },
            }),
        }, jsx(LazyVideo, {src: src, height: height}));
    });

    const BroadcastPageLink = memo(function BroadcastPageLink({id, text}) {
        return a({href: 'https://www.amazon.com/live/broadcast/' + id}, text);
    });

    const LazyTooltip = lazy(async () => {
        const [jQuery, ] = await Promise.all(
            [module('jQuery'), module('bootstrapBundle')]);

        return fakeModule(memo(function LazyTooltip(props) {
            const {title, type, children, ...restProps} = props;
            const [element, setElement] = useState(null);
            const [tooltipEl, setTooltipEl] = useState(null);

            useEffect(() => {
                if (element) {
                    setTooltipEl(jQuery(element));
                }
            }, [element]);

            useEffect(() => {
                if (tooltipEl && (title !== '')) {
                    tooltipEl.tooltip({
                        placement: 'right',
                        title: title,
                    });
                    return () => tooltipEl.tooltip('dispose');
                }
            }, [tooltipEl, title]);

            return jsx(type,
                {ref: useCallback(setElement), ...restProps},
                children);
        }));
    });

    const Tooltip = memo(function Tooltip(props) {
        const {title = '', type = 'span', children, ...restProps} = props;
        const actualTitle = lodash.isBoolean(title) ? '' : title;

        return jsx(React.Suspense, {
            fallback: jsx(type,
                {title: actualTitle, ...restProps}, children),
        }, jsx(LazyTooltip,
            {title: actualTitle, type: type, ...restProps}, children));
    });

    const LazyDateTime = lazy(async () => {
        const moment = await module('moment');

        return fakeModule(memo(function LazyDateTime({children}) {
            return jsx(Tooltip,
                {title: 'Original timestamp: ' + children},
                moment(children).calendar(null, {sameElse: 'llll'}));
        }));
    });

    const DateTime = memo(function DateTime({children}) {
        return jsx(React.Suspense, {
            fallback: jsx(LoadingSpinner, {before: children}),
        }, jsx(LazyDateTime, children));
    });

    const LazyDuration = lazy(async () => {
        const [moment, ] = await Promise.all(
            [module('moment'), module('momentDurationFormat')]);

        return fakeModule(memo(function LazyDuration({from, to}) {
            const duration = moment.duration(moment(to).diff(from));

            return jsx(Tooltip,
                {title: duration.humanize(), type: 'abbr'},
                duration.format());
        }));
    });

    const Duration = memo(function Duration(props) {
        return jsx(React.Suspense,
            {fallback: jsx(LoadingSpinner)},
            jsx(LazyDuration, props));
    });

    const Id = memo(function Id({children}) {
        return span({className: 'text-nowrap text-monospace'}, children);
    });

    const Button = memo(function Button(props) {
        const {
            title, children, disabled, style, className, ...restProps
        } = props;

        return jsx(Tooltip, {title: title},
            button({
                type: 'button',
                disabled: disabled,
                style: !disabled ? style : {
                    cursor: 'not-allowed',
                    opacity: 0.25,
                    ...style,
                },
                className: classNames('btn', className),
                ...restProps,
            }, children));
    });

    const ToggleButton = memo(function ToggleButton(props) {
        const {children, className, ...restProps} = props;

        return jsx(Button, {
            className: classNames('btn-info', className),
            'data-toggle': 'button',
            ...restProps,
        }, children);
    });

    const RadioTable = memo(function RadioTable(props) {
        const {headers, rows, onSelectedRowIndex, onEmpty} = props;
        const [selectedRowIndex, setSelectedRowIndex] = useState(null);

        useEffect(() => {
            if (selectedRowIndex === null) {
                if (rows.length === 1) {
                    setSelectedRowIndex(0);
                }
            }
            else if (selectedRowIndex >= rows.length) {
                setSelectedRowIndex(null);
            }
        }, [rows]);

        useEffect(() => {
            if (selectedRowIndex !== null) {
                onSelectedRowIndex(selectedRowIndex);
            }
        }, [selectedRowIndex]);

        if (rows.length === 0) {
            return onEmpty();
        }

        return div({className: 'table-responsive border mb-3'},
            table(
                {className: 'table table-sm table-hover mb-0'},
                thead(
                    {className: 'thead-light'},
                    tr(headers.map(({width, content}, index) =>
                        th({key: index, width: width},
                            content)))),
                tbody(rows.map((row, rowIndex) =>
                    tr(
                        {
                            key: rowIndex,
                            className: classNames(
                                {'table-primary': selectedRowIndex === rowIndex}),
                            onPointerDown() {
                                if (!hasSelection()) {
                                    setSelectedRowIndex(rowIndex);
                                }
                            },
                        },
                        row.map(({content, name}, cellIndex) =>
                            td({key: cellIndex}, (name === undefined)
                                ? content
                                : input({
                                    type: 'radio',
                                    name: name,
                                    checked: selectedRowIndex === rowIndex,
                                    onChange() {
                                        setSelectedRowIndex(rowIndex);
                                    },
                                }))))))));
    });

    const Accounts = memo(function Accounts({data, onListShows}) {
        const [selectedAccount, setSelectedAccount] = useState(null);
        const [isJsonShown, toggleIsJsonShown] = useToggleState(false);
        const SELECT_ACCOUNT_BUTTON_TITLE = 'Select an account';
        const isLoggedOut = lodash.isPlainObject(data)
            && data.errors.some(error => error.code === 'notLoggedIn');

        useEffect(() => {
            if (selectedAccount && (data.length === 1)) {
                onListShows(selectedAccount);
            }
        }, [selectedAccount, data]);

        if (isLoggedOut) {
            return p(a(
                {href: 'https://www.amazon.com/gp/sign-in.html'},
                'Login to your Amazon account first.'));
        }

        return Fragment(
            p(a(
                {href: 'https://www.amazon.com/gp/navigation/redirector.html?switchAccount=picker'},
                'Switch Amazon accounts.')),
            form(
                jsx(RadioTable, {
                    onEmpty() {
                        return p(a(
                            {href: 'https://apps.apple.com/app/id1265170914'},
                            'Create an Amazon Live Creator account first.'));
                    },
                    onSelectedRowIndex(rowIndex) {
                        setSelectedAccount(data[rowIndex]);
                    },
                    headers: [
                        {width: '1%'},
                        {content: 'Name'},
                        {width: '55%', content: 'ID'},
                        {width: '19%', content: 'Type'},
                    ],
                    rows: data.map(account => [
                        {name: 'account'},
                        {content: account.name},
                        {content: jsx(Id, account.id)},
                        {content: account.type},
                    ]),
                }),
                p(
                    jsx(Button, {
                        title: !!selectedAccount || SELECT_ACCOUNT_BUTTON_TITLE,
                        disabled: !selectedAccount,
                        className: 'btn-primary mr-3',
                        onPointerDown() {
                            onListShows(selectedAccount);
                        },
                    }, 'List shows'),
                    jsx(ToggleButton, {
                        title: !!selectedAccount || SELECT_ACCOUNT_BUTTON_TITLE,
                        disabled: !selectedAccount,
                        onPointerDown: toggleIsJsonShown,
                    }, 'Show/Hide JSON')),
                selectedAccount && jsx(JsonAceEditor, {
                    json: selectedAccount,
                    style: {display: isJsonShown ? null : 'none'},
                })));
    });

    const Shows = memo(function Shows(props) {
        const {data, onLoadLiveData, onListBroadcasts} = props;
        const [selectedShow, setSelectedShow] = useState(null);
        const [isJsonShown, toggleIsJsonShown] = useToggleState(false);
        const SELECT_SHOW_BUTTON_TITLE = 'Select a show';

        useEffect(() => {
            if (selectedShow && (data.shows.length === 1)) {
                onLoadLiveData(selectedShow);
                onListBroadcasts(selectedShow);
            }
        }, [selectedShow, data]);

        return form(
            jsx(RadioTable, {
                onEmpty() {
                    return p('No shows in this account.');
                },
                onSelectedRowIndex(rowIndex) {
                    setSelectedShow(data.shows[rowIndex]);
                },
                headers: [
                    {width: '1%'},
                    {content: 'Title'},
                    {width: '42%', content: 'ID'},
                    {width: '16%', content: 'Distribution'},
                    {width: '16%', content: 'Feature Group'},
                ],
                rows: data.shows.map(show => [
                    {name: 'show'},
                    {content: a({
                        href: 'https://www.amazon.com/live/channel/' + show.id,
                    }, show.title)},
                    {content: jsx(Id, show.id)},
                    {content: show.distribution},
                    {content: show.featureGroup},
                ]),
            }),
            p(
                jsx(Button, {
                    title: !!selectedShow || SELECT_SHOW_BUTTON_TITLE,
                    disabled: !selectedShow,
                    className: 'btn-primary mr-3',
                    onPointerDown() {
                        onListBroadcasts(selectedShow);
                    },
                }, 'List broadcasts'),
                jsx(Button, {
                    title: !!selectedShow || SELECT_SHOW_BUTTON_TITLE,
                    disabled: !selectedShow,
                    className: 'btn-primary mr-3',
                    onPointerDown() {
                        onLoadLiveData(selectedShow);
                    },
                }, 'Load live data'),
                jsx(ToggleButton, {
                    title: !!selectedShow || SELECT_SHOW_BUTTON_TITLE,
                    disabled: !selectedShow,
                    onPointerDown: toggleIsJsonShown,
                }, 'Show/Hide JSON')),
            selectedShow && jsx(JsonAceEditor, {
                json: selectedShow,
                style: {display: isJsonShown ? null : 'none'},
            }));
    });

    const Broadcasts = memo(function Broadcasts(props) {
        const {data, onLoadMore, onLoadBroadcast} = props;
        const [selectedBroadcast, setSelectedBroadcast] = useState(null);
        const [isLoadingMore, setIsLoadingMore] = useState(false);
        const [isJsonShown, toggleIsJsonShown] = useToggleState(false);
        const SELECT_BROADCAST_BUTTON_TITLE = 'Select a broadcast';
        const canLoadMoreBroadcasts = !!data.nextLink && !isLoadingMore;

        useEffect(() => void setIsLoadingMore(false), [data]);

        useEffect(() => {
            if (selectedBroadcast && (data.broadcasts.length === 1)) {
                onLoadBroadcast(selectedBroadcast);
            }
        }, [selectedBroadcast, data]);

        return form(
            jsx(RadioTable, {
                onEmpty() {
                    return p('No broadcasts in this show.');
                },
                onSelectedRowIndex(rowIndex) {
                    setSelectedBroadcast(data.broadcasts[rowIndex]);
                },
                headers: [
                    {width: '1%'},
                    {content: 'Title'},
                    {width: '25%', content: 'ID'},
                    {width: '9%', content: 'ASIN'},
                    {width: '6%', content: 'Distribution'},
                    {width: '6%', content: 'Duration'},
                    {
                        width: '14%',
                        content: jsx(Tooltip, {
                            title: 'Local time of "broadcastStartDateTime"',
                            type: 'abbr',
                        }, 'Started'),
                    },
                    {
                        width: '14%',
                        content: jsx(Tooltip, {
                            title: 'Local time of "broadcastEndDateTime"',
                            type: 'abbr',
                        }, 'Ended'),
                    },
                ],
                rows: data.broadcasts.map(broadcast => [
                    {name: 'broadcast'},
                    {content: jsx(BroadcastPageLink, {
                        id: broadcast.id,
                        text: broadcast.title,
                    })},
                    {content: jsx(Id, broadcast.id)},
                    {content: jsx(Id, broadcast.asin)},
                    {content: broadcast.distribution},
                    {content: broadcast.broadcastStartDateTime
                        && broadcast.broadcastEndDateTime
                        && jsx(Duration, {
                            from: broadcast.broadcastStartDateTime,
                            to: broadcast.broadcastEndDateTime,
                        })},
                    {content: broadcast.broadcastStartDateTime
                        && jsx(DateTime, broadcast.broadcastStartDateTime)},
                    {content: broadcast.broadcastEndDateTime
                        && jsx(DateTime, broadcast.broadcastEndDateTime)},
                ]),
            }),
            p(
                jsx(Button, {
                    title: !!selectedBroadcast || SELECT_BROADCAST_BUTTON_TITLE,
                    disabled: !selectedBroadcast,
                    className: 'btn-primary mr-3',
                    onPointerDown() {
                        onLoadBroadcast(selectedBroadcast.id);
                    },
                }, 'Load broadcast'),
                jsx(Button, {
                    disabled: !canLoadMoreBroadcasts,
                    className: 'btn-primary mr-3',
                    title: !data.nextLink ? 'No more broadcasts'
                        : isLoadingMore ? 'Loading more broadcasts'
                        : '',
                    onPointerDown() {
                        setIsLoadingMore(true);
                        onLoadMore(data.nextLink);
                    },
                }, 'Load more broadcasts'),
                jsx(ToggleButton, {
                    title: !!selectedBroadcast || SELECT_BROADCAST_BUTTON_TITLE,
                    disabled: !selectedBroadcast,
                    onPointerDown: toggleIsJsonShown,
                }, 'Show/Hide JSON')),
            selectedBroadcast && jsx(JsonAceEditor, {
                json: selectedBroadcast,
                style: {display: isJsonShown ? null : 'none'},
            }));
    });

    const LiveData = memo(function LiveData({data, onLoadBroadcast}) {
        const [isJsonShown, toggleIsJsonShown] = useToggleState(false);

        const {
            broadcastStartedId,
            lockedBroadcastId,
            lockedBroadcastState,
            lvsLastMessageSubject,
            lvsLastMessageEpochTime,
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
                            th('Status'),
                            th(jsx(Tooltip, {
                                title: 'Local time of "lvsLastMessageEpochTime"',
                                type: 'abbr',
                            }, 'Last change')))),
                    tbody(
                        tr(
                            td(broadcastId && jsx(Id, broadcastId)),
                            td(!broadcastId ? state : jsx(BroadcastPageLink, {
                                id: broadcastId,
                                text: state})),
                            td(data.showLiveData.status),
                            td(lvsLastMessageEpochTime
                                && jsx(DateTime, lvsLastMessageEpochTime * 1000))))))),
            p(
                jsx(Button, {
                    title: !!broadcastId || 'No broadcast with live data',
                    disabled: !broadcastId,
                    className: 'btn-primary mr-3',
                    onPointerDown() {
                        onLoadBroadcast(broadcastId);
                    },
                }, 'Load broadcast'),
                jsx(ToggleButton, {onPointerDown: toggleIsJsonShown},
                    'Show/Hide JSON')),
            jsx(JsonAceEditor, {
                json: data,
                style: {display: isJsonShown ? null : 'none'},
            }));
    });

    const Broadcast = memo(function Broadcast({data, getSlateImageUrl}) {
        const [broadcast, setBroadcast] = useState(data);
        const [isJsonShown, toggleIsJsonShown] = useToggleState(false);
        const canClear = (broadcast !== EMPTY_BROADCAST_DATA);

        useEffect(() => void setBroadcast(data), [data]);

        return form(
            broadcast.hlsUrl && p(jsx(Video, {src: broadcast.hlsUrl})),
            p(img({
                src: getSlateImageUrl(broadcast.id),
                height: '100px',
            })),
            p(input({
                type: 'file',
                name: 'slateImage',
                accept: 'image/*',
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
                },
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
            p(
                jsx(Button, {
                    title: canClear || 'Already cleared',
                    disabled: !canClear,
                    className: 'btn-primary mr-3',
                    onPointerDown() {
                        setBroadcast(EMPTY_BROADCAST_DATA);
                    },
                }, 'Clear'),
                jsx(ToggleButton, {onPointerDown: toggleIsJsonShown},
                    'Show/Hide JSON')),
            jsx(JsonAceEditor, {
                json: broadcast,
                style: {display: isJsonShown ? null : 'none'},
            }));
    });

    /**
     * @param Component {React.Component}
     * @returns {React.Component}
     */
    function lazyComponentSection(Component) {
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
                    ? jsx(LoadingSpinner)
                    : jsx(Component, {data, ...componentProps}));
        });
    }

    function concatBroadcasts(oldData, newData) {
        return {
            broadcasts: oldData.broadcasts.concat(newData.broadcasts),
            nextLink: newData.nextLink,
        };
    }

    function refreshBroadcasts(oldData, newData) {
        const numBroadcasts = Math.min(
            oldData.broadcasts.length, newData.broadcasts.length);

        const oldBroadcasts = oldData.broadcasts.slice(0, numBroadcasts);
        const newBroadcasts = newData.broadcasts.slice(0, numBroadcasts);

        if (lodash.isEqual(oldBroadcasts, newBroadcasts)) {
            return {
                broadcasts: oldBroadcasts.concat(
                    newData.broadcasts.slice(numBroadcasts)),
                nextLink: newData.nextLink,
            };
        }

        return newData;
    }

    const LazyAccounts = lazyComponentSection(Accounts);
    const LazyShows = lazyComponentSection(Shows);
    const LazyLiveData = lazyComponentSection(LiveData);
    const LazyBroadcasts = lazyComponentSection(Broadcasts);
    const LazyBroadcast = lazyComponentSection(Broadcast);

    const App = memo(function App({api}) {
        const [accountsPromise, ] = useState(api.listAccounts());
        const [showsPromise, setShowsPromise] = useState(null);
        const [liveDataPromise, setLiveDataPromise] = useState(null);
        const [broadcastPromise, setBroadcastPromise] = useState(null);
        const [broadcastsPromise, setBroadcastsPromise] = useState(null);
        const [broadcastsShowId, setBroadcastsShowId] = useState(null);
        const [isLoadingMoreBroadcasts, setIsLoadingMoreBroadcasts]
            = useState(false);

        return Fragment(
            jsx(LazyAccounts, {
                title: 'Accounts',
                promise: accountsPromise,
                onListShows(account) {
                    setShowsPromise(api.listShows());
                    setBroadcastPromise(Promise.resolve(EMPTY_BROADCAST_DATA));
                },
            }),
            showsPromise && jsx(LazyShows, {
                title: 'Shows',
                promise: showsPromise,
                onLoadLiveData(show) {
                    setLiveDataPromise(api.readShowLiveData(show.id));
                },
                onListBroadcasts(show) {
                    setIsLoadingMoreBroadcasts(false);
                    setBroadcastsShowId(show.id);
                    setBroadcastsPromise(api.listShowBroadcasts(show.id));
                },
            }),
            broadcastsShowId && broadcastsPromise && jsx(LazyBroadcasts, {
                title: 'Broadcasts',
                promise: broadcastsPromise,
                reducer: isLoadingMoreBroadcasts
                    ? concatBroadcasts
                    : refreshBroadcasts,
                onLoadMore(nextToken) {
                    setIsLoadingMoreBroadcasts(true);
                    setBroadcastsPromise(
                        api.listShowBroadcasts(broadcastsShowId, nextToken));
                },
                onLoadBroadcast(broadcastId) {
                    setBroadcastPromise(api.readBroadcast(broadcastId));
                },
            }),
            liveDataPromise && jsx(LazyLiveData, {
                title: 'Live Data',
                promise: liveDataPromise,
                onLoadBroadcast(broadcastId) {
                    setBroadcastPromise(api.readBroadcast(broadcastId));
                },
            }),
            broadcastPromise && jsx(LazyBroadcast, {
                title: 'Broadcast',
                promise: broadcastPromise,
                getSlateImageUrl(broadcastId) {
                    return api.getBroadcastSlateImageUrl(broadcastId);
                },
            }));
    });

    const shouldRun = /Violentmonkey/i.test(GM_info.scriptHandler)
        || confirm('Unsupported UserScript manager. Continue?');

    if (shouldRun) {
        ReactDOM.render(jsx(App, {api: new Api()}), rootEl);
    }
});
