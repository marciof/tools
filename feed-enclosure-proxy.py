#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Standard:
from functools import partial
from http import HTTPStatus
import io
import logging
import mimetypes
import re
from urllib.parse import urlencode, quote as urlquote
import xml.etree.ElementTree as ElementTree

# External:
import defusedxml.ElementTree as DefusedElementTree # v0.6.0
from feedgen.feed import FeedGenerator # v0.9.0
import feedparser # v5.2.1
from flask import Flask, Response, request, redirect # v1.1.2
import requests # v2.12.4
from unidecode import unidecode # v1.1.1
import youtube_dl # v2020.3.24


formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)


class YoutubeDlUrlInterceptingLogger (object):
    """
    https://github.com/ytdl-org/youtube-dl/tree/master#embedding-youtube-dl
    """

    def __init__(self):
        self.urls = []

    def debug(self, msg):
        if re.match(r'^\w+://', msg):
            self.urls.append(msg)
        else:
            logger.debug('youtube-dl debug while intercepting URLs: %s', msg)

    def warning(self, msg):
        logger.warning('youtube-dl warning while intercepting URLs: %s', msg)

    def error(self, msg):
        logger.error('youtube-dl error while intercepting URLs: %s', msg)


# TODO: higher-res IGN Daily Fix videos, <https://github.com/ytdl-org/youtube-dl/tree/master#adding-support-for-a-new-site>
# TODO: merge high-res YouTube video+audio on the fly while streaming?
def extract_video_url(url):
    """
    https://github.com/ytdl-org/youtube-dl/tree/master#embedding-youtube-dl
    """

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


def proxy_feed_enclosure_urls(feed_xml, transform_url):
    """
    http://www.rssboard.org/media-rss#media-content
    """

    feed_xml_io = io.StringIO(feed_xml)
    events = {'start', 'start-ns'}
    feed_root = None

    for (event, element) in DefusedElementTree.iterparse(feed_xml_io, events):
        if event == 'start-ns':
            (ns_prefix, ns_uri) = element
            ElementTree.register_namespace(ns_prefix, ns_uri)
        elif event == 'start':
            if feed_root is None:
                feed_root = element

            if element.tag in ('enclosure', '{http://search.yahoo.com/mrss/}content'):
                element.attrib['url'] = transform_url(element.attrib['url'])
                del element.attrib['type']

    return DefusedElementTree.tostring(feed_root, encoding = 'unicode')


def download_feed(feed_url):
    logger.info('Downloading feed from URL <%s>', feed_url)
    feed_response = requests.get(feed_url)
    feed_response.raise_for_status()
    return feed_response.text


def build_rss_feed_entry(feed_entry, rss_feed):
    rss_feed_entry = rss_feed.add_entry()
    rss_feed_entry.title(feed_entry.title)

    if 'id' in feed_entry:
        rss_feed_entry.id(feed_entry.id)
    if 'link' in feed_entry:
        rss_feed_entry.link({'href': feed_entry.link})
    if 'published' in feed_entry:
        rss_feed_entry.published(feed_entry.published)
    if 'updated' in feed_entry:
        rss_feed_entry.updated(feed_entry.updated)
    if 'summary' in feed_entry:
        rss_feed_entry.summary(feed_entry.summary)
    if 'description' in feed_entry:
        rss_feed_entry.description(feed_entry.description)

    if ('content' in feed_entry) and (len(feed_entry.content) > 0):
        first_content = feed_entry.content[0]
        rss_feed_entry.content(
            content = first_content['value'],
            type = first_content['type'])

    return (rss_feed_entry, lambda url, type:
        rss_feed_entry.enclosure(url = url, type = type))


def build_rss_feed(feed):
    logger.info('Converting feed to RSS')
    rss_feed = FeedGenerator()

    if 'id' in feed:
        rss_feed.id(feed.id)
    if 'title' in feed:
        rss_feed.title(feed.title)
    if 'link' in feed:
        rss_feed.link({'href': feed.link})
    if 'published' in feed:
        rss_feed.pubDate(feed.published)

    if 'description' in feed:
        rss_feed.description(feed.description)
    else:
        # `feedgen` requires a non-empty feed description.
        rss_feed.description('-')

    return (rss_feed, partial(build_rss_feed_entry, rss_feed = rss_feed))


def list_feed_entry_enclosures(feed_entry):
    for enclosure in feed_entry.enclosures:
        yield (enclosure['href'], enclosure['type'])

    for media in feed_entry.media_content:
        yield (media['url'], media['type'])


def make_enclosure_proxy_url(url, title = None, stream = False):
    if title is None:
        title_path = ''
    else:
        safe_title = unidecode(re.sub(r"[^\w',()-]+", ' ', title).strip())
        title_path = '/' + urlquote(safe_title, safe = "',()-")

    stream_qs_param = 'stream&' if stream else ''
    query_string = '?' + stream_qs_param + urlencode({'url': url})
    return request.host_url + 'enclosure' + title_path + query_string


def get_bool_request_qs_param(name):
    value = request.args.get(name)

    if value is None:
        return False
    elif value == '':
        return True
    else:
        return None


app = Flask(__name__)


@app.route('/feed')
def proxy_feed():
    url = request.args.get('url')
    do_stream = get_bool_request_qs_param('stream')
    do_rss = get_bool_request_qs_param('rss')

    if url is None:
        return 'Missing `url` query string parameter', HTTPStatus.BAD_REQUEST
    if do_stream is None:
        return '`stream` query string parameter must have no value', HTTPStatus.BAD_REQUEST
    if do_rss is None:
        return '`rss` query string parameter must have no value', HTTPStatus.BAD_REQUEST

    feed_xml = download_feed(url)
    parsed_feed = feedparser.parse(feed_xml)
    enclosure_url_to_title = dict()
    rss_feed = None
    add_rss_feed_entry = lambda entry: (None, lambda url, type: None)

    if do_rss:
        if re.match('rss', parsed_feed.version, re.IGNORECASE):
            do_rss = False
        else:
            (rss_feed, add_rss_feed_entry) = build_rss_feed(parsed_feed.feed)

    for entry in parsed_feed.entries:
        (rss_feed_entry, add_enclosure) = add_rss_feed_entry(entry)

        for (enclosure_url, enclosure_type) in list_feed_entry_enclosures(entry):
            enclosure_url_to_title[enclosure_url] = entry.title
            add_enclosure(enclosure_url, enclosure_type)

    if do_rss:
        feed_xml = rss_feed.rss_str().decode()

    proxied_feed_xml = proxy_feed_enclosure_urls(feed_xml,
        transform_url = lambda url:
            make_enclosure_proxy_url(url,
                title = enclosure_url_to_title.get(url),
                stream = do_stream))

    return Response(proxied_feed_xml, mimetype = 'text/xml')


@app.route('/enclosure')
def proxy_enclosure():
    url = request.args.get('url')

    if url is None:
        return 'Missing `url` query string parameter', HTTPStatus.BAD_REQUEST

    return redirect(extract_video_url(url))


@app.route('/enclosure/<title>')
def proxy_titled_enclosure(title):
    url = request.args.get('url')
    do_stream = get_bool_request_qs_param('stream')

    if url is None:
        return 'Missing `url` query string parameter', HTTPStatus.BAD_REQUEST

    if do_stream is None:
        return '`stream` query string parameter must have no value', HTTPStatus.BAD_REQUEST
    elif not do_stream:
        return redirect(extract_video_url(url))

    proxy_request_headers = {
        header: request.headers[header]
            for header in {'Range'} if header in request.headers
    }

    enclosure = requests.get(extract_video_url(url),
        stream = True,
        headers = proxy_request_headers)

    proxy_response_status = None

    proxy_response_headers = {
        header: enclosure.headers[header]
            for header in {'Accept-Ranges', 'Content-Range', 'Content-Length'}
            if header in enclosure.headers
    }

    if 'Content-Range' in proxy_response_headers:
        proxy_response_status = HTTPStatus.PARTIAL_CONTENT

    return Response(enclosure.iter_content(chunk_size = 1 * 1024),
        status = proxy_response_status,
        mimetype = enclosure.headers['Content-Type'],
        headers = proxy_response_headers)


if __name__ == '__main__':
    app.run()
