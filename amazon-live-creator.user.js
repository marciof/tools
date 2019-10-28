// ==UserScript==
// @name Amazon Live Creator
// @version 0.1
// @namespace https://github.com/marciof
// @icon https://www.amazon.com/favicon.ico
// @match https://amazonlivetools.amazon.com/
// @run-at document-start
// @grant GM_info
// @grant GM_addStyle
// ==/UserScript==

// FIXME: use minified versions by default if faster, with dev mode option?
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
// FIXME: make some JSON Ace editors read-only?
// FIXME: use <label>s instead of onclick+focus?
// FIXME: does Button with tooltip breaks focus?
// FIXME: don't select table row when clicking on links?

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
        const {before, after, style} = props;

        return span(
            {style: style},
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
                    player.src(src);
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

    const LoginLink = memo(function LoginLink() {
        return p(a(
            {href: 'https://www.amazon.com/gp/sign-in.html'},
            'Please login to your Amazon account first.'));
    });

    const LazyTooltip = lazy(async () => {
        const [jQuery, ] = await Promise.all(
            [module('jQuery'), module('bootstrapBundle')]);

        return fakeModule(memo(function LazyTooltip({title, type, children}) {
            const [element, setElement] = useState(null);
            const [tooltipEl, setTooltipEl] = useState(null);

            useEffect(() => {
                if (element) {
                    setTooltipEl(jQuery(element));
                }
            }, [element]);

            useEffect(() => {
                if (tooltipEl && (title !== '') && !lodash.isBoolean(title)) {
                    tooltipEl.tooltip({
                        placement: 'right',
                        title: title,
                    });
                    return () => tooltipEl.tooltip('dispose');
                }
            }, [tooltipEl, title]);

            return jsx(type, {ref: useCallback(setElement)}, children);
        }));
    });

    const Tooltip = memo(function Tooltip({title = '', children, type = 'span'}) {
        return jsx(React.Suspense,
            {fallback: jsx(type, {title: title}, children)},
            jsx(LazyTooltip, {title: title, type: type}, children));
    });

    const LazyDateTime = lazy(async () => {
        const moment = await module('moment');

        return fakeModule(memo(function LazyDateTime({dateTime}) {
            return jsx(Tooltip,
                {title: 'Original timestamp: ' + dateTime},
                moment(dateTime).calendar(null, {sameElse: 'llll'}));
        }));
    });

    const DateTime = memo(function DateTime({dateTime}) {
        return jsx(React.Suspense,
            {fallback: jsx(LoadingSpinner, {before: dateTime})},
            jsx(LazyDateTime, {dateTime}));
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

    const Id = memo(function Id({id}) {
        return span({className: 'text-nowrap text-monospace'}, id);
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
        const {headers, rows, onSelectedRowIndex} = props;
        const [selectedRowIndex, setSelectedRowIndex] = useState(null);

        useEffect(() => {
            if (selectedRowIndex === null) {
                if (rows.length === 1) {
                    setSelectedRowIndex(0);
                    onSelectedRowIndex(0);
                }
            }
            else if (selectedRowIndex >= rows.length) {
                setSelectedRowIndex(null);
                onSelectedRowIndex(null);
            }
        }, [rows]);

        return div({className: 'card mb-3'},
            div({className: 'table-responsive'},
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
                                        onSelectedRowIndex(rowIndex);
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
                                            onSelectedRowIndex(rowIndex);
                                        },
                                    })))))))));
    });

    const Shows = memo(function Shows(props) {
        const {data, onLoadLiveData, onListBroadcasts} = props;

        const [selectedShow, setSelectedShow] = useState(null);
        const [isJsonShown, toggleIsJsonShown] = useToggleState(false);
        const SELECT_SHOW_BUTTON_TITLE = 'Select a show';

        useEffect(() => {
            if (selectedShow) {
                onLoadLiveData(selectedShow.id);
                onListBroadcasts(selectedShow.id);
            }
        }, [selectedShow]);

        if (data.errors) {
            return jsx(LoginLink);
        }

        return form(
            jsx(RadioTable, {
                onSelectedRowIndex(rowIndex) {
                    setSelectedShow(rowIndex !== null
                        ? data.shows[rowIndex]
                        : null);
                },
                headers: [
                    {},
                    {content: 'Title'},
                    {content: 'ID'},
                    {content: 'Distribution'},
                    {content: 'Feature Group'},
                ],
                rows: data.shows.map(show => [
                    {name: 'show'},
                    {content: a({
                        href: 'https://www.amazon.com/live/channel/' + show.id,
                    }, show.title)},
                    {content: jsx(Id, {id: show.id})},
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
                        onListBroadcasts(selectedShow.id);
                    },
                }, 'List broadcasts'),
                jsx(Button, {
                    title: !!selectedShow || SELECT_SHOW_BUTTON_TITLE,
                    disabled: !selectedShow,
                    className: 'btn-primary mr-3',
                    onPointerDown() {
                        onLoadLiveData(selectedShow.id);
                    },
                }, 'Load live data'),
                jsx(ToggleButton, {
                    disabled: !selectedShow,
                    title: !!selectedShow || SELECT_SHOW_BUTTON_TITLE,
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

        return form(
            jsx(RadioTable, {
                onSelectedRowIndex(rowIndex) {
                    setSelectedBroadcast(rowIndex !== null
                        ? data.broadcasts[rowIndex]
                        : null);
                },
                headers: [
                    {width: '1%'},
                    {content: 'Title'},
                    {width: '22%', content: 'ID'},
                    {width: '7%', content: 'ASIN'},
                    {width: '5%', content: 'Distribution'},
                    {width: '5%', content: 'Duration'},
                    {
                        width: '15%',
                        content: jsx(Tooltip, {
                            title: 'Local time of "broadcastStartDateTime"',
                            type: 'abbr',
                        }, 'Started'),
                    },
                    {
                        width: '15%',
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
                    {content: jsx(Id, {id: broadcast.id})},
                    {content: jsx(Id, {id: broadcast.asin})},
                    {content: broadcast.distribution},
                    {content: broadcast.broadcastStartDateTime
                        && broadcast.broadcastEndDateTime
                        && jsx(Duration, {
                            from: broadcast.broadcastStartDateTime,
                            to: broadcast.broadcastEndDateTime,
                        })},
                    {content: broadcast.broadcastStartDateTime
                        && jsx(DateTime, {
                            dateTime: broadcast.broadcastStartDateTime,
                    })},
                    {content: broadcast.broadcastEndDateTime
                        && jsx(DateTime, {
                            dateTime: broadcast.broadcastEndDateTime,
                    })},
                ]),
            }),
            p(
                jsx(Button, {
                    title: !selectedBroadcast ? SELECT_BROADCAST_BUTTON_TITLE : '',
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
                    disabled: !selectedBroadcast,
                    title: !!selectedBroadcast || SELECT_BROADCAST_BUTTON_TITLE,
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
                            td(broadcastId && jsx(Id, {id: broadcastId})),
                            td(!broadcastId ? state : jsx(BroadcastPageLink, {
                                id: broadcastId,
                                text: state})),
                            td(data.showLiveData.status),
                            td(lvsLastMessageEpochTime && jsx(DateTime, {
                                dateTime: lvsLastMessageEpochTime * 1000,
                            }))))))),
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
    function lazyComponent(Component) {
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

    const LazyShows = lazyComponent(Shows);
    const LazyLiveData = lazyComponent(LiveData);
    const LazyBroadcasts = lazyComponent(Broadcasts);
    const LazyBroadcast = lazyComponent(Broadcast);

    const App = memo(function App({api}) {
        const [showsPromise,] = useState(() => api.listShows());
        const [liveDataPromise, setLiveDataPromise] = useState(null);
        const [broadcastPromise, setBroadcastPromise] = useState(
            Promise.resolve(EMPTY_BROADCAST_DATA));

        const [isLoadingMoreBroadcasts, setIsLoadingMoreBroadcasts] = useState(
            false);
        const [broadcastsShowId, setBroadcastsShowId] = useState(null);
        const [broadcastsPromise, setBroadcastsPromise] = useState(null);

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
            jsx(LazyBroadcast, {
                title: 'Broadcast',
                promise: broadcastPromise,
                getSlateImageUrl(broadcastId) {
                    return api.getBroadcastSlateImageUrl(broadcastId);
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
            }));
    });

    const shouldRun = /Violentmonkey/i.test(GM_info.scriptHandler)
        || confirm('Unsupported UserScript manager. Continue?');

    if (shouldRun) {
        ReactDOM.render(jsx(App, {api: new Api()}), rootEl);
    }
});
