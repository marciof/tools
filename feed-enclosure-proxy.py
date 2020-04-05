#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Standard:
from http import HTTPStatus
import io
import mimetypes
import re
import sys
from urllib.parse import urlencode
import xml.etree.ElementTree as ElementTree

# External:
import defusedxml.ElementTree as DefusedElementTree # v0.6.0
from feedgen.feed import FeedGenerator # v0.9.0
import feedparser # v5.2.1
from flask import Flask, Response, request, redirect # v1.1.2
import requests # v2.12.4
from unidecode import unidecode # v1.1.1
import youtube_dl # v2020.3.24


# TODO: use a proper logger for warnings and errors
class YoutubeDlUrlInterceptingLogger (object):
    """
    https://github.com/ytdl-org/youtube-dl/tree/master#embedding-youtube-dl
    """

    def __init__(self):
        self.urls = []

    def debug(self, msg):
        if re.match(r'^\w+://', msg):
            self.urls.append(msg)

    def warning(self, msg):
        print(msg, file = sys.stderr)

    def error(self, msg):
        print(msg, file = sys.stderr)


# TODO: higher resolution IGN Daily Fix videos (youtube_dl extractor?)
# TODO: option to merge YouTube video+audio on the fly? stream -> download
def extract_video_url(url):
    """
    https://github.com/ytdl-org/youtube-dl/tree/master#embedding-youtube-dl
    """

    (content_type, encoding) = mimetypes.guess_type(url)

    if (content_type is not None) and content_type.startswith('video/'):
        return url

    logger = YoutubeDlUrlInterceptingLogger()

    youtubedl_options = {
        'format': 'best',
        'forceurl': True,
        'simulate': True,
        'logger': logger,
    }

    with youtube_dl.YoutubeDL(youtubedl_options) as ydl:
        ydl.download([url])

    [extracted_url] = logger.urls
    return extracted_url


def proxy_feed_enclosure_urls(feed_xml, transform_url, title_url):
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
                url = element.attrib['url']
                element.attrib['url'] = transform_url(url, title_url(url))
                del element.attrib['type']

    return DefusedElementTree.tostring(feed_root, encoding = 'unicode')


def make_enclosure_proxy_url(url, title):
    if title is None:
        title_path = ''
    else:
        title_path = '/' + unidecode(re.sub(r'[^\w]+', '-', title).strip('-'))

    return request.host_url + 'enclosure' + title_path + '?stream&' + urlencode({'url': url})


def download_feed(feed_url):
    feed_response = requests.get(feed_url)
    feed_response.raise_for_status()
    return feed_response.text


# TODO: make RSS conversion optional and refactor
def convert_feed_to_rss(feed_xml):
    feed = feedparser.parse(feed_xml)
    is_already_rss = re.match('rss', feed.version, re.IGNORECASE)
    enclosure_url_to_title = dict()
    rss_feed = None

    if not is_already_rss:
        rss_feed = FeedGenerator()
        if 'id' in feed.feed:
            rss_feed.id(feed.feed.id)
        if 'title' in feed.feed:
            rss_feed.title(feed.feed.title)
        if 'link' in feed.feed:
            rss_feed.link({'href': feed.feed.link})
        if 'published' in feed.feed:
            rss_feed.pubDate(feed.feed.published)
        if 'description' in feed.feed:
            rss_feed.description(feed.feed.description)
        else:
            rss_feed.description('-')

    for entry in feed.entries:
        rss_entry = None

        if not is_already_rss:
            rss_entry = rss_feed.add_entry()
            rss_entry.title(entry.title)
            if 'id' in entry:
                rss_entry.id(entry.id)
            if 'link' in entry:
                rss_entry.link({'href': entry.link})
            if 'published' in entry:
                rss_entry.published(entry.published)
            if 'updated' in entry:
                rss_entry.updated(entry.updated)
            if ('content' in entry) and (len(entry.content) > 0):
                first_content = entry.content[0]
                rss_entry.content(
                    content = first_content['value'],
                    type = first_content['type'])
            if 'summary' in entry:
                rss_entry.summary(entry.summary)
            if 'description' in entry:
                rss_entry.description(entry.description)

        if 'enclosures' in entry:
            for enclosure in entry.enclosures:
                url = enclosure['href']
                enclosure_url_to_title[url] = entry.title
                if not is_already_rss:
                    rss_entry.enclosure(url = url, type = enclosure['type'])

        if 'media_content' in entry:
            for content in entry.media_content:
                url = content['url']
                enclosure_url_to_title[url] = entry.title
                if not is_already_rss:
                    rss_entry.enclosure(url = url, type = content['type'])

    if is_already_rss:
        return (feed_xml, enclosure_url_to_title)
    else:
        return (rss_feed.rss_str().decode(), enclosure_url_to_title)


app = Flask(__name__)


@app.route('/feed')
def proxy_feed():
    url = request.args.get('url')

    if url is None:
        return 'Missing `url` query string parameter', HTTPStatus.BAD_REQUEST

    (feed_xml, enclosure_url_to_title) = convert_feed_to_rss(download_feed(url))

    feed_xml = proxy_feed_enclosure_urls(feed_xml,
        transform_url = make_enclosure_proxy_url,
        title_url = enclosure_url_to_title.get)

    return Response(feed_xml, mimetype = 'text/xml')


@app.route('/enclosure')
def proxy_enclosure():
    url = request.args.get('url')

    if url is None:
        return 'Missing `url` query string parameter', HTTPStatus.BAD_REQUEST

    return redirect(extract_video_url(url))


@app.route('/enclosure/<title>')
def proxy_titled_enclosure(title):
    url = request.args.get('url')
    stream = request.args.get('stream')

    if url is None:
        return 'Missing `url` query string parameter', HTTPStatus.BAD_REQUEST

    if stream is None:
        return redirect(extract_video_url(url))
    elif stream != '':
        return '`stream` query string parameter must have no value', HTTPStatus.BAD_REQUEST

    enclosure = requests.get(extract_video_url(url), stream = True)

    return Response(enclosure.iter_content(chunk_size = 1 * 1024),
        mimetype = enclosure.headers['Content-Type'],
        headers = {'Content-Length': enclosure.headers['Content-Length']})


# TODO: add more logging as operations are taking place
if __name__ == '__main__':
    app.run()
