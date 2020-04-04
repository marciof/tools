#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Standard:
from http import HTTPStatus
import mimetypes
import re
import sys
from urllib.parse import urlencode

# External:
from defusedxml import ElementTree # v0.6.0
from flask import Flask, Response, Request, request, redirect # v1.1.2
import requests # v2.12.4
import youtube_dl # v2020.3.24


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


def extract_video_url(page_url):
    """
    https://github.com/ytdl-org/youtube-dl/tree/master#embedding-youtube-dl
    """

    logger = YoutubeDlUrlInterceptingLogger()

    youtubedl_options = {
        'format': 'best',
        'forceurl': True,
        'simulate': True,
        'logger': logger,
    }

    with youtube_dl.YoutubeDL(youtubedl_options) as ydl:
        ydl.download([page_url])

    [url] = logger.urls
    return url


# FIXME: doesn't preserve namespaces from input
# FIXME: adds a default namespace
def proxy_feed_enclosure_urls(feed_url, transform_url):
    feed_response = requests.get(feed_url)
    feed_response.raise_for_status()

    feed_xml = ElementTree.fromstring(feed_response.text)
    namespaces = {'media': 'http://search.yahoo.com/mrss/'}

    for content in feed_xml.findall('.//media:content', namespaces):
        url = content.attrib['url']
        (content_type, encoding) = mimetypes.guess_type(url)

        if (content_type is None) or (not content_type.startswith('video/')):
            content.attrib['url'] = transform_url(url)
        else:
            print('Not proxying enclosure:', url, file = sys.stderr)

    return ElementTree.tostring(feed_xml, encoding = 'unicode')


def make_enclosure_proxy_url(url):
    return request.host_url + 'enclosure?' + urlencode({'url': url})


app = Flask(__name__)


@app.route('/feed')
def proxy_feed():
    url = request.args.get('url')

    if url is None:
        return 'Missing `url` query string parameter', HTTPStatus.BAD_REQUEST

    feed_xml = proxy_feed_enclosure_urls(url, make_enclosure_proxy_url)
    return Response(feed_xml, mimetype = 'text/xml')


@app.route('/enclosure')
def proxy_enclosure():
    url = request.args.get('url')

    if url is None:
        return 'Missing `url` query string parameter', HTTPStatus.BAD_REQUEST

    return redirect(extract_video_url(url))


if __name__ == '__main__':
    app.run()
