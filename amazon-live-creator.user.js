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

// FIXME: type check with eslint and typescript+jsdoc
// FIXME: radio button on row selection, use <label>s instead of onclick+focus?
// FIXME: table spacing when there's <code/>? or <input/>? radio adds spacing?
// FIXME: handle errors in lazy loading, network, use error boundaries
// FIXME: use more lightweight video player? https://github.com/video-dev/hls.js
// FIXME: handle videojs JS errors
// FIXME: sortable tables? searchable? datatable
// FIXME: service workers for performance? new Worker(URL.createObjectURL(new Blob([
// FIXME: use minified versions by default if faster?

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

const customStyles = new Promise(resolve => {
    GM_addStyle(`
        details[open] summary ~ * {
            animation: appear 0.3s ease-in-out;
        }

        @keyframes appear {
            0% {
                opacity: 0;
                margin-top: -3px;
            }
            100% {
                opacity: 1;
                margin-top: 0;
            }
        }

        .fadeIn {
            animation: fadeIn 0.6s ease-in-out forwards;
        }

        .fadeOut {
            animation: fadeOut 0.2s ease-in-out forwards;
        }

        @keyframes fadeIn {
            0% {
                opacity: 0;
                visibility: hidden;
            }

            100% {
                opacity: 1;
                visibility: visible;
            }
        }

        @keyframes fadeOut {
            0% {
                opacity: 1;
                visibility: visible;
            }
            100% {
                opacity: 0;
                visibility: hidden;
            }
        }
    `);

    resolve();
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

Promise.all([pageReady, configuredRequireJs, customStyles]).then(async args => {
    const [rootEl, module] = args;

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
    const dl = jsx.bind(null, 'dl');
    const dt = jsx.bind(null, 'dt');
    const dd = jsx.bind(null, 'dd');
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
    const Suspense = React.Suspense;

    const EMPTY_ACCOUNTS_DATA = {
        errors: [
            {code: 'notLoggedIn'},
        ],
    };

    const EMPTY_SHOWS_DATA = {
        shows: [],
    };

    const EMPTY_LIVE_DATA = {
        showLiveData: {
            value: {},
        },
    };

    const EMPTY_BROADCASTS_DATA = {
        broadcasts: [],
        nextLink: null,
    };

    const EMPTY_BROADCAST_DATA = {
        id: '',
        title: '',
        videoSource: 'THIRD_PARTY_ENCODER',
    };

    const VIDEO_SOURCES = {
        PHONE_CAMERA: 'Phone camera',
        THIRD_PARTY_ENCODER: 'Encoder',
    };

    function concatBroadcastData(oldData, newData) {
        return {
            broadcasts: oldData.broadcasts.concat(newData.broadcasts),
            nextLink: newData.nextLink,
        };
    }

    function refreshBroadcastData(oldData, newData) {
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
            () => void setIsEnabled(prevIsEnabled => !prevIsEnabled),
            []);

        return [isEnabled, toggleIsEnabled];
    }

    function fakeModule(defaultExport) {
        return {
            default: defaultExport,
        };
    }

    function getAceEditorValidValue(editor) {
        const annotations = editor.getSession().getAnnotations();

        for (let i = 0; i < annotations.length; ++i) {
            if (annotations[i].type === 'error') {
                return null;
            }
        }

        return editor.getValue();
    }

    const LoadingSpinner = memo(function LoadingSpinner(props) {
        const {before, after, ...restProps} = props;

        return span(
            restProps,
            (before !== undefined) ? Fragment(before, ' ') : null,
            span({className: 'spinner-border text-secondary spinner-border-sm'}),
            (after !== undefined) ? Fragment(' ', after) : null);
    });

    const LazyAceEditor = lazy(async () => {
        const aceEditor = await module('aceEditor');

        return fakeModule(memo(function LazyAceEditor(props) {
            const {children, mode, style, isReadOnly, onChange} = props;
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
                    // Changing the editor's value also changes cursor position
                    // and selection ranges.
                    const {row, column} = editor.getCursorPosition();
                    const range = editor.getSelectionRange();

                    editor.setValue(children);
                    editor.gotoLine(row + 1, column);
                    editor.getSelection().setSelectionRange(range);
                }
            }, [editor, children]);

            useEffect(() => {
                if (editor && (isReadOnly !== undefined)) {
                    editor.setReadOnly(isReadOnly);
                }
            }, [editor, isReadOnly]);

            useEffect(() => {
                if (editor && onChange) {
                    const listener = () => {
                        const value = getAceEditorValidValue(editor);
                        if (value !== null) {
                            onChange(value);
                        }
                    };

                    // Listen to the tokenizer so that it has a chance to
                    // parse and validate input (no need for throttling or
                    // debouncing).
                    editor.getSession().on('tokenizerUpdate', listener);

                    return () => editor.getSession().off(
                        'tokenizerUpdate', listener);
                }
            }, [editor, onChange]);

            return div({ref: editorElRef, style: style});
        }));
    });

    const AceEditor = memo(function AceEditor({style, children, ...props}) {
        return jsx(Suspense, {
            fallback: jsx(LoadingSpinner, {
                after: pre(children),
                style: {
                    overflow: 'auto',
                    display: 'block',
                    ...style,
                },
            }),
        }, jsx(LazyAceEditor, {style: style, ...props}, children));
    });

    const JsonAceEditor = memo(function JsonAceEditor(props) {
        const {json, style, onChange, ...restProps} = props;

        return jsx(AceEditor, {
            mode: 'ace/mode/json',
            style: {
                width: '100%',
                height: '200px',
                border: '1px solid lightgray',
                ...style,
            },
            onChange: !onChange ? null : function(validValue) {
                if (validValue.trim().length > 0) {
                    onChange(validValue);
                }
            },
            ...restProps,
        }, JSON.stringify(json, undefined, 4));
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

        return jsx(Suspense, {
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
        return a(
            {href: 'https://www.amazon.com/live/broadcast/' + id},
            text === undefined ? id : text);
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

        return jsx(Suspense, {
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
        return jsx(Suspense, {
            fallback: jsx(LoadingSpinner, {before: children}),
        }, jsx(LazyDateTime, children));
    });

    const LazyDuration = lazy(async () => {
        const [moment, ] = await Promise.all(
            [module('moment'), module('momentDurationFormat')]);

        return fakeModule(memo(function LazyDuration({from, to}) {
            const duration = moment.duration(moment(to).diff(from));

            return jsx(Tooltip,
                {title: duration.humanize()},
                duration.format());
        }));
    });

    const Duration = memo(function Duration(props) {
        return jsx(Suspense,
            {fallback: jsx(LoadingSpinner)},
            jsx(LazyDuration, props));
    });

    const Id = memo(function Id({children}) {
        return span({className: 'text-nowrap text-monospace'}, children);
    });

    const NotAvailableNotice = memo(function NotAvailableNotice() {
        return jsx(Tooltip, {
            title: 'Not available',
            type: 'abbr',
        }, 'N/A');
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
        const {
            children, alternativeChildren, className, onToggle, ...restProps
        } = props;

        const [isToggled, toggle] = useToggleState(false);

        useEffect(() => void onToggle(isToggled), [isToggled]);

        return jsx(Button, {
            className: classNames('btn-outline-info', className),
            'data-toggle': 'button',
            onClick: toggle,
            ...restProps,
        }, (alternativeChildren !== undefined) && isToggled
            ? alternativeChildren
            : children);
    });

    const ToggleJsonButton = memo(function ToggleJsonButton(props) {
        const {disabled, title, ...restProps} = props;

        return jsx(ToggleButton, {
            title: disabled ? title : false,
            disabled: disabled,
            alternativeChildren: 'Hide JSON',
            ...restProps,
        }, 'View JSON');
    });

    const RadioTable = memo(function RadioTable(props) {
        const {headers, rows, emptyNotice, onSelectedRowIndex} = props;
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

        return div({className: 'table-responsive border-bottom mb-3'},
            table(
                {
                    className: classNames('table table-sm mb-0', {
                        'table-hover': rows.length > 0,
                    }),
                },
                thead(
                    {className: 'thead-light'},
                    tr(headers.map(({width, content}, index) =>
                        th({key: index, width: width},
                            content)))),
                tbody(rows.length === 0
                    ? tr(td(
                        {
                            colSpan: headers.length,
                            className: classNames('text-center', {
                                'text-muted': (emptyNotice === undefined),
                            }),
                            style: emptyNotice === undefined
                                ? {cursor: 'not-allowed'}
                                : null,
                        },
                        emptyNotice !== undefined
                            ? emptyNotice
                            : jsx(NotAvailableNotice)))
                    : rows.map((row, rowIndex) => tr(
                        {
                            key: rowIndex,
                            className: classNames(
                                {'table-primary': selectedRowIndex === rowIndex}),
                            onClick() {
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
        const [isJsonShown, setIsJsonShown] = useState(null);
        const SELECT_ACCOUNT_BUTTON_TITLE = 'Select an account';
        const isLoggedOut = lodash.isPlainObject(data)
            && data.errors.some(error => error.code === 'notLoggedIn');

        useEffect(() => {
            if (selectedAccount && (data.length === 1)) {
                onListShows(selectedAccount);
            }
        }, [selectedAccount, data]);

        return Fragment(
            p(a(
                {href: 'https://www.amazon.com/gp/navigation/redirector.html?switchAccount=picker'},
                'Switch Amazon accounts.')),
            form(
                jsx(RadioTable, {
                    onSelectedRowIndex(rowIndex) {
                        setSelectedAccount(data[rowIndex]);
                    },
                    emptyNotice: isLoggedOut
                        ? a(
                            {href: 'https://www.amazon.com/gp/sign-in.html'},
                            'Login to your Amazon account.')
                        : a(
                            {href: 'https://apps.apple.com/app/id1265170914'},
                            'Create an Amazon Live Creator account.'),
                    headers: [
                        {width: '1%'},
                        {content: 'Name'},
                        {width: '55%', content: 'ID'},
                        {width: '19%', content: 'Type'},
                    ],
                    rows: isLoggedOut ? [] : data.map(account => [
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
                        className: 'btn-outline-primary mr-3',
                        onClick() {
                            onListShows(selectedAccount);
                        },
                    }, 'List shows'),
                    jsx(ToggleJsonButton, {
                        title: SELECT_ACCOUNT_BUTTON_TITLE,
                        disabled: !selectedAccount,
                        onToggle: setIsJsonShown,
                    })),
                selectedAccount && jsx(JsonAceEditor, {
                    json: selectedAccount,
                    isReadOnly: true,
                    style: {display: isJsonShown ? null : 'none'},
                })));
    });

    const Shows = memo(function Shows(props) {
        const {data, onLoadLiveData, onListBroadcasts} = props;
        const [selectedShow, setSelectedShow] = useState(null);
        const [isJsonShown, setIsJsonShown] = useState(null);
        const SELECT_SHOW_BUTTON_TITLE = 'Select a show';

        useEffect(() => {
            if (selectedShow && (data.shows.length === 1)) {
                onLoadLiveData(selectedShow);
                onListBroadcasts(selectedShow);
            }
        }, [selectedShow, data]);

        return form(
            jsx(RadioTable, {
                onSelectedRowIndex(rowIndex) {
                    setSelectedShow(data.shows[rowIndex]);
                },
                emptyNotice: 'Select an account.',
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
                    className: 'btn-outline-primary mr-3',
                    onClick() {
                        onListBroadcasts(selectedShow);
                    },
                }, 'List broadcasts'),
                jsx(Button, {
                    title: !!selectedShow || SELECT_SHOW_BUTTON_TITLE,
                    disabled: !selectedShow,
                    className: 'btn-outline-primary mr-3',
                    onClick() {
                        onLoadLiveData(selectedShow);
                    },
                }, 'Load live data'),
                jsx(ToggleJsonButton, {
                    title: SELECT_SHOW_BUTTON_TITLE,
                    disabled: !selectedShow,
                    onToggle: setIsJsonShown,
                })),
            selectedShow && jsx(JsonAceEditor, {
                json: selectedShow,
                isReadOnly: true,
                style: {display: isJsonShown ? null : 'none'},
            }));
    });

    const Broadcasts = memo(function Broadcasts(props) {
        const {data, onLoadMore, onLoadBroadcast} = props;
        const [selectedBroadcast, setSelectedBroadcast] = useState(null);
        const [isLoadingMore, setIsLoadingMore] = useState(false);
        const [isJsonShown, setIsJsonShown] = useState(null);
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
                onSelectedRowIndex(rowIndex) {
                    setSelectedBroadcast(data.broadcasts[rowIndex]);
                },
                emptyNotice: 'Select a show.',
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
                    className: 'btn-outline-primary mr-3',
                    onClick() {
                        onLoadBroadcast(selectedBroadcast.id);
                    },
                }, 'Load broadcast'),
                jsx(Button, {
                    disabled: !canLoadMoreBroadcasts,
                    className: 'btn-outline-primary mr-3',
                    title: !data.nextLink ? 'No more broadcasts'
                        : isLoadingMore ? 'Loading more broadcasts'
                        : '',
                    onClick() {
                        setIsLoadingMore(true);
                        onLoadMore(data.nextLink);
                    },
                }, 'Load more broadcasts'),
                jsx(ToggleJsonButton, {
                    title: SELECT_BROADCAST_BUTTON_TITLE,
                    disabled: !selectedBroadcast,
                    onToggle: setIsJsonShown,
                })),
            selectedBroadcast && jsx(JsonAceEditor, {
                json: selectedBroadcast,
                isReadOnly: true,
                style: {display: isJsonShown ? null : 'none'},
            }));
    });

    const LiveData = memo(function LiveData({data, onLoadBroadcast}) {
        const [isJsonShown, setIsJsonShown] = useState(null);

        const {
            broadcastStartedId,
            lockedBroadcastId,
            lockedBroadcastState,
            lvsLastMessageSubject,
            lvsLastMessageEpochTime,
        } = data.showLiveData.value;

        const broadcastId = broadcastStartedId || lockedBroadcastId;
        const state = lockedBroadcastState || lvsLastMessageSubject;
        const status = data.showLiveData.status;

        return form(
            dl(
                dt(jsx(Tooltip, {
                    title: 'Value of "broadcastStartedId" or "lockedBroadcastId"',
                    type: 'abbr',
                }, 'Broadcast ID')),
                dd({className: 'ml-4'}, broadcastId
                    ? jsx(BroadcastPageLink, {id: broadcastId})
                    : jsx(NotAvailableNotice)),

                dt(jsx(Tooltip, {
                    title: 'Value of "lockedBroadcastState" or "lvsLastMessageSubject"',
                    type: 'abbr',
                }, 'State')),
                dd({className: 'ml-4'}, state !== undefined
                    ? state
                    : jsx(NotAvailableNotice)),

                dt('Status'),
                dd({className: 'ml-4'}, status !== undefined
                    ? status
                    : jsx(NotAvailableNotice)),

                dt(jsx(Tooltip, {
                    title: 'Local time of "lvsLastMessageEpochTime"',
                    type: 'abbr',
                }, 'Last change')),

                dd({className: 'ml-4'}, lvsLastMessageEpochTime
                    ? jsx(DateTime, lvsLastMessageEpochTime * 1000)
                    : jsx(NotAvailableNotice))),
            p(
                jsx(Button, {
                    title: !!broadcastId || 'No broadcast with live data',
                    disabled: !broadcastId,
                    className: 'btn-outline-primary mr-3',
                    onClick() {
                        onLoadBroadcast(broadcastId);
                    },
                }, 'Load broadcast'),
                jsx(ToggleJsonButton, {onToggle: setIsJsonShown})),
            jsx(JsonAceEditor, {
                json: data,
                isReadOnly: true,
                style: {display: isJsonShown ? null : 'none'},
            }));
    });

    const Broadcast = memo(function Broadcast({data, getSlateImageUrl}) {
        const [broadcast, setBroadcast] = useState(data);
        const [isJsonShown, setIsJsonShown] = useState(null);
        const canReset = (broadcast !== data);

        useEffect(() => void setBroadcast(data), [data]);

        return form(
            p(jsx(Video, {src: broadcast.hlsUrl})),
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
                value: broadcast.title || '',
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
                    title: canReset || 'Already reset',
                    disabled: !canReset,
                    className: 'btn-outline-primary mr-3',
                    onClick() {
                        setBroadcast(data);
                    },
                }, 'Reset'),
                jsx(ToggleJsonButton, {onToggle: setIsJsonShown})),
            jsx(JsonAceEditor, {
                json: broadcast,
                style: {display: isJsonShown ? null : 'none'},
                onChange(validValue) {
                    const newBroadcast = JSON.parse(validValue);

                    setBroadcast(prevBroadcast =>
                        lodash.isEqual(prevBroadcast, newBroadcast)
                            ? prevBroadcast
                            : newBroadcast);
                },
            }));
    });

    /**
     * @param Component {React.Component}
     * @returns {React.Component}
     */
    function lazySectionComponent(Component) {
        return memo(function LazySection(props) {
            const {title, promise, defaultData, ...componentProps} = props;
            const [isLoading, setIsLoading] = useState(false);
            const [data, setData] = useState(defaultData);

            useEffect(() => {
                if (promise) {
                    setIsLoading(true);

                    // Set data state separately to prevent race conditions.
                    promise.then(newData => {
                        setIsLoading(false);
                        return newData;
                    });
                }
            }, [promise]);

            useEffect(() => {
                if (promise && !isLoading) {
                    promise.then(setData);
                }
            }, [promise, isLoading]);

            return details(
                {className: 'mb-4', open: data !== defaultData},
                summary(
                    {className: 'mb-2'},
                    span({className: 'font-weight-bold h5'}, title),
                    jsx(LoadingSpinner, {
                        className: classNames({fadeOut: !isLoading}),
                        before: true,
                    })),
                jsx(Component, {data, ...componentProps}));
        });
    }

    const LazyAccounts = lazySectionComponent(Accounts);
    const LazyShows = lazySectionComponent(Shows);
    const LazyLiveData = lazySectionComponent(LiveData);
    const LazyBroadcasts = lazySectionComponent(Broadcasts);
    const LazyBroadcast = lazySectionComponent(Broadcast);

    const App = memo(function App({api}) {
        const [accountsPromise, setAccountsPromise] = useState(null);
        const [showsPromise, setShowsPromise] = useState(null);
        const [liveDataPromise, setLiveDataPromise] = useState(null);
        const [broadcastsPromise, setBroadcastsPromise] = useState(null);
        const [broadcastsShowId, setBroadcastsShowId] = useState(null);
        const [broadcastPromise, setBroadcastPromise] = useState(null);

        useEffect(() => void setAccountsPromise(api.listAccounts()), [api]);

        return Fragment(
            jsx(LazyAccounts, {
                title: 'Accounts',
                promise: accountsPromise,
                defaultData: EMPTY_ACCOUNTS_DATA,
                onListShows(account) {
                    setShowsPromise(api.listShows());
                    setBroadcastPromise(Promise.resolve(
                        // Clone broadcast so it doesn't compare as equal.
                        lodash.clone(EMPTY_BROADCAST_DATA)));
                },
            }),
            jsx(LazyShows, {
                title: 'Shows',
                promise: showsPromise,
                defaultData: EMPTY_SHOWS_DATA,
                onLoadLiveData(show) {
                    setLiveDataPromise(api.readShowLiveData(show.id));
                },
                onListBroadcasts(show) {
                    setBroadcastsShowId(show.id);
                    setBroadcastsPromise(oldBroadcastsPromise =>
                        Promise.all([
                            oldBroadcastsPromise || EMPTY_BROADCASTS_DATA,
                            api.listShowBroadcasts(show.id),
                        ])
                        .then(([oldData, newData]) => refreshBroadcastData(oldData, newData)));
                },
            }),
            jsx(LazyLiveData, {
                title: 'Live Data',
                promise: liveDataPromise,
                defaultData: EMPTY_LIVE_DATA,
                onLoadBroadcast(broadcastId) {
                    setBroadcastPromise(api.readBroadcast(broadcastId));
                },
            }),
            jsx(LazyBroadcasts, {
                title: 'Broadcasts',
                promise: broadcastsPromise,
                defaultData: EMPTY_BROADCASTS_DATA,
                onLoadMore(nextToken) {
                    setBroadcastsPromise(oldBroadcastsPromise =>
                        Promise.all([
                            oldBroadcastsPromise,
                            api.listShowBroadcasts(broadcastsShowId, nextToken),
                        ])
                        .then(([oldData, newData]) => concatBroadcastData(oldData, newData)));
                },
                onLoadBroadcast(broadcastId) {
                    setBroadcastPromise(api.readBroadcast(broadcastId));
                },
            }),
            jsx(LazyBroadcast, {
                title: 'Broadcast',
                promise: broadcastPromise,
                defaultData: EMPTY_BROADCAST_DATA,
                getSlateImageUrl(broadcastId) {
                    return api.getBroadcastSlateImageUrl(broadcastId);
                },
            }));
    });

    const shouldRun = /Violentmonkey/i.test(GM_info.scriptHandler)
        || confirm('Unsupported UserScript manager (Violentmonkey not detected).\nContinue anyway?');

    if (shouldRun) {
        ReactDOM.render(jsx(App, {api: new Api()}), rootEl);
    }
});
