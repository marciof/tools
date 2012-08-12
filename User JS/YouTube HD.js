// ==UserScript==
// @include http://*.youtube.com/watch?*
// @include https://*.youtube.com/watch?*
// ==/UserScript==


if (!/\bhd\b/.test(location.search)) {
    /*
    Handle all possible cases:
        www
        www#
        www#y
        www?
        www?#
        www?#y
        www?x
        www?x#
        www?x#y
    */
    location.replace(location.toString().replace(/\?|(#)|$/, '?hd=1&$1'));
}
