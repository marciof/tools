#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Transforms RSS/Atom feeds to have downloadable enclosures.

# Standard:
from collections import OrderedDict
from functools import partial
import html
from http import HTTPStatus
import io
import logging
import mimetypes
import re
import textwrap
from urllib.parse import urlencode, quote as urlquote
import xml.etree.ElementTree as ElementTree
# TODO: use typing

# External:
import defusedxml.ElementTree as DefusedElementTree # v0.6.0
from feedgen.feed import FeedGenerator # v0.9.0
import feedparser # v5.2.1
from flask import Flask, Response, request, redirect # v1.1.2
import requests # v2.12.4
from unidecode import unidecode # v1.1.1
import youtube_dl # v2020.3.24


app_name = 'Feed Enclosure Proxy'

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger = logging.getLogger(app_name)
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)


def transform_url_attrib_element_url(element, transform_url):
    element.attrib['url'] = transform_url(element.attrib['url'])


def transform_url_text_element_url(element, transform_url):
    element.text = transform_url(element.text)


ENCLOSURE_TAG_TO_TRANSFORM_ELEMENT_URL = {
    'enclosure': transform_url_attrib_element_url,
    '{http://search.yahoo.com/mrss/}content': transform_url_attrib_element_url,
    '{http://rssnamespace.org/feedburner/ext/1.0}origEnclosureLink': transform_url_text_element_url,
}


class YoutubeDlUrlInterceptingLogger:
    """
    https://github.com/ytdl-org/youtube-dl/tree/master#embedding-youtube-dl
    """

    def __init__(self):
        self.urls = []

    def debug(self, msg):
        if re.search(r'^\w+://', msg):
            self.urls.append(msg)
        else:
            logger.debug('youtube-dl debug while intercepting URLs: %s', msg)

    def warning(self, msg):
        logger.warning('youtube-dl warning while intercepting URLs: %s', msg)

    def error(self, msg):
        logger.error('youtube-dl error while intercepting URLs: %s', msg)


# TODO: higher-res IGN Daily Fix videos, <https://github.com/ytdl-org/youtube-dl/tree/master#adding-support-for-a-new-site>
def extract_ign_daily_fix_video_url(url):
    if re.search(r'://assets\d*\.ign\.com/videos/', url):
        high_res_url = re.sub(
            r'(?<=/) \d+ (/[a-f0-9]+-) \d+ (-\d+\.)',
            r'1920\g<1>3906000\2',
            url,
            flags = re.IGNORECASE + re.VERBOSE)

        response = requests.head(high_res_url)

        if response.ok:
            return high_res_url

    return None


# TODO: merge high-res YouTube video+audio on the fly while streaming?
def extract_video_url(url):
    """
    https://github.com/ytdl-org/youtube-dl/tree/master#embedding-youtube-dl
    """

    extracted_url = extract_ign_daily_fix_video_url(url)

    if extracted_url is None:
        (content_type, encoding) = mimetypes.guess_type(url)

        if (content_type is not None) and content_type.startswith('video/'):
            logger.info('Skip extracting video with MIME type "%s" from URL <%s>',
                content_type, url)
            return url

        youtube_dl_logger = YoutubeDlUrlInterceptingLogger()

        youtube_dl_options = {
            'format': 'best',
            'forceurl': True,
            'simulate': True,
            'logger': youtube_dl_logger,
        }

        with youtube_dl.YoutubeDL(youtube_dl_options) as ydl:
            ydl.download([url])

        [extracted_url] = youtube_dl_logger.urls

    logger.info('Extracted from URL <%s> video URL <%s>', url, extracted_url)
    return extracted_url


def transform_feed_enclosure_urls(feed_xml, transform_url):
    """
    http://www.rssboard.org/media-rss#media-content
    """

    feed_xml_io = io.StringIO(feed_xml)
    events = {'start', 'end', 'start-ns'}
    feed_root = None

    for (event, element) in DefusedElementTree.iterparse(feed_xml_io, events):
        if event == 'start-ns':
            (ns_prefix, ns_uri) = element
            ElementTree.register_namespace(ns_prefix, ns_uri)
        elif event == 'start':
            if feed_root is None:
                feed_root = element
        elif event == 'end':
            if element.tag in ENCLOSURE_TAG_TO_TRANSFORM_ELEMENT_URL:
                ENCLOSURE_TAG_TO_TRANSFORM_ELEMENT_URL[element.tag](
                    element, transform_url)

    return DefusedElementTree.tostring(feed_root, encoding = 'unicode')


def download_feed(feed_url):
    logger.info('Downloading feed from URL <%s>', feed_url)
    feed_response = requests.get(feed_url)
    feed_response.raise_for_status()
    return feed_response.text


def rebuild_parsed_feed_entry(feed_entry, new_feed):
    new_feed_entry = new_feed.add_entry()
    new_feed_entry.title(feed_entry.title)

    if 'id' in feed_entry:
        new_feed_entry.id(feed_entry.id)
    if 'link' in feed_entry:
        new_feed_entry.link({'href': feed_entry.link})
    if 'published' in feed_entry:
        new_feed_entry.published(feed_entry.published)
    if 'updated' in feed_entry:
        new_feed_entry.updated(feed_entry.updated)
    if 'summary' in feed_entry:
        new_feed_entry.summary(feed_entry.summary)
    if 'description' in feed_entry:
        new_feed_entry.description(feed_entry.description)

    if ('content' in feed_entry) and (len(feed_entry.content) > 0):
        first_content = feed_entry.content[0]
        new_feed_entry.content(
            content = first_content['value'],
            type = first_content['type'])

    return (new_feed_entry, lambda url, type:
        new_feed_entry.enclosure(url = url, type = type))


def rebuild_parsed_feed(feed):
    new_feed = FeedGenerator()

    if 'id' in feed.feed:
        new_feed.id(feed.feed.id)
    if 'title' in feed.feed:
        new_feed.title(feed.feed.title)
    if 'link' in feed.feed:
        new_feed.link({'href': feed.feed.link})
    if 'published' in feed.feed:
        new_feed.pubDate(feed.feed.published)

    if 'description' in feed.feed:
        new_feed.description(feed.feed.description)
    else:
        # `feedgen` requires a non-empty feed description.
        new_feed.description('-')

    return (new_feed, partial(rebuild_parsed_feed_entry, new_feed = new_feed))


def list_parsed_feed_entry_enclosures(feed_entry):
    enclosure_type_by_url = OrderedDict()

    if 'feedburner_origenclosurelink' in feed_entry:
        url = feed_entry.feedburner_origenclosurelink
        (content_type, encoding) = mimetypes.guess_type(url)
        enclosure_type_by_url[url] = content_type

    for enclosure in feed_entry.enclosures:
        enclosure_type_by_url[enclosure['href']] = enclosure['type']

    for media in feed_entry.media_content:
        enclosure_type_by_url[media['url']] = media['type']

    yield from enclosure_type_by_url.items()


def make_enclosure_proxy_url(url, title = None, stream = False):
    if title is None:
        title_path = ''
    else:
        safe_title = unidecode(re.sub(r"[^\w',()-]+", ' ', title).strip())
        title_path = '/' + urlquote(safe_title, safe = "',()-")

    stream_qs_param = 'stream&' if stream else ''
    query_string = '?' + stream_qs_param + urlencode({'url': url})
    return request.host_url + 'enclosure' + title_path + query_string


def prepare_doc_for_display(doc):
    return textwrap.dedent(doc.strip('\n'))


def make_error_response_from_view(view_fn):
    return Response(prepare_doc_for_display(view_fn.__doc__),
        status = HTTPStatus.BAD_REQUEST,
        mimetype = 'text/plain')


def get_bool_request_qs_param(name):
    value = request.args.get(name)

    if value is None:
        return False
    elif value == '':
        return True
    else:
        return None


app = Flask(app_name, static_folder = None)

@app.route('/')
def index():
    """
    Site map.
    """

    rules = []

    for rule in sorted(app.url_map.iter_rules(), key = lambda rule: str(rule)):
        view_function = app.view_functions[rule.endpoint]

        rules.append('<dt><a href="%s">%s</a></dt><dd style="white-space: pre-wrap">%s</dd>' % (
            html.escape(str(rule)),
            html.escape(str(rule)),
            html.escape(prepare_doc_for_display(view_function.__doc__))
        ))

    return '<title>%s</title><body><dl>%s</dl></body>' % (app_name, '\n'.join(rules))


@app.route('/feed')
def proxy_feed():
    """
    Modifies a feed to proxy enclosures.
    - `url`: feed URL
    - `stream`: if present, pass parameter as-is to each enclosure
    - `rss`: if present, converts the feed to RSS
    """

    url = request.args.get('url')
    do_stream = get_bool_request_qs_param('stream')
    do_rss = get_bool_request_qs_param('rss')

    if None in (url, do_stream, do_rss):
        return make_error_response_from_view(app.view_functions[request.endpoint])

    def add_new_feed_entry_no_op(entry):
        return (None, lambda url, type: None)

    feed_xml = download_feed(url)
    feed = feedparser.parse(feed_xml)
    feed_entry_by_enclosure_url = dict()
    (new_feed, add_new_feed_entry) = (None, add_new_feed_entry_no_op)

    if do_rss:
        logger.info('Rebuilding feed as RSS in URL <%s>', url)
        (new_feed, add_new_feed_entry) = rebuild_parsed_feed(feed)

    for entry in feed.entries:
        (new_feed_entry, add_enclosure) = add_new_feed_entry(entry)

        # Reverse from least to most preferred, since `feedgen` will only keep
        # the last one for RSS feeds.
        for (enclosure_url, enclosure_type) in reversed(list(list_parsed_feed_entry_enclosures(entry))):
            add_enclosure(enclosure_url, enclosure_type)
            feed_entry_by_enclosure_url[enclosure_url] = entry

    if new_feed:
        feed_xml = new_feed.rss_str().decode()

    proxied_feed_xml = transform_feed_enclosure_urls(feed_xml,
        transform_url = lambda url: make_enclosure_proxy_url(url,
            title = feed_entry_by_enclosure_url[url].title,
            stream = do_stream))

    return Response(proxied_feed_xml, mimetype = 'text/xml')


@app.route('/enclosure/<title>')
def proxy_titled_enclosure(title):
    """
    Redirects an enclosure to its direct download URL, named "title".
    - `url`: enclosure URL
    - `stream`: if present, streams the enclosure instead of redirecting
    - `download`: if present, downloads the enclosure instead of redirecting
    """

    url = request.args.get('url')
    do_stream = get_bool_request_qs_param('stream')
    do_download = get_bool_request_qs_param('download')

    if None in (url, do_stream, do_download):
        return make_error_response_from_view(app.view_functions[request.endpoint])

    if (not do_stream) and (not do_download):
        return redirect(extract_video_url(url))
    elif do_stream and do_download:
        return make_error_response_from_view(app.view_functions[request.endpoint])

    range_header = request.headers.get('Range')

    enclosure = requests.get(extract_video_url(url),
        stream = True,
        headers = {'Range': range_header} if range_header else None)

    content_type = enclosure.headers['Content-Type']

    response_headers = {
        header: enclosure.headers[header]
            for header in {'Accept-Ranges', 'Content-Range', 'Content-Length'}
            if header in enclosure.headers
    }

    if do_download:
        extension = mimetypes.guess_extension(content_type)
        file_name = title + (extension or '')
        response_headers['Content-Disposition'] = 'attachment; filename="%s"' % file_name

    return Response(enclosure.iter_content(chunk_size = 1 * 1024),
        status = HTTPStatus.PARTIAL_CONTENT if 'Content-Range' in response_headers else None,
        mimetype = content_type,
        headers = response_headers)


# TODO: extract title from video where possible
@app.route('/enclosure')
def proxy_enclosure():
    """
    Redirects an enclosure to its direct download URL.
    - `url`: enclosure URL
    - `stream`: if present, streams the enclosure instead of redirecting
    - `download`: if present, downloads the enclosure instead of redirecting
    """

    return proxy_titled_enclosure('video')


# TODO: document
# TODO: tests
# TODO: performance?
if __name__ == '__main__':
    app.run()
