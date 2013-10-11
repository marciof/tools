#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import logging
import sys
import urlparse

# External:
import enum
import lxml.html
import requests
import unipath


# What is searched for:
# - RSS auto-discovery
# - Atom auto-discovery
# - Paths auto-discovery
# - www.sitemaps.org
# robots.txt ?
# <link> next rel index ?

_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
_logger.addHandler(_handler)


STRICT_MIME_TYPES = False

STRICT_RSS_REL = False
RSS_REL = 'alternate'

PATHS_DISCOVERY = set(['/feed', '/rss'])
PATHS_DISCOVERY_TRAILING_SLASH = True

FIND_FROM_HTML = True
FIND_FROM_URL_PATHS = True
FIND_FROM_URL_WORDS = True


class MimeType (enum.Enum):
    # http://www.rssboard.org/rss-autodiscovery
    RSS = 'application/rss+xml'
    
    # TODO: Read Atom spec.
    # http://en.wikipedia.org/wiki/Atom_(standard)
    ATOM = 'application/atom+xml'


# TODO: Convert relative URL's to absolute.
class Feed (object):
    def __init__(self, url, mime_type = None, relation = None, title = None):
        self.url = url
        self.mime_type = mime_type
        self.relation = relation
        self.title = title
    
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    
    def __hash__(self):
        return hash(self.url)
    
    
    def __unicode__(self):
        return '%s <%s> %s %s' % (
            '?' if self.title is None else repr(self.title),
            self.url,
            self.mime_type,
            '?' if self.relation is None else repr(self.relation))


class Error (Exception):
    pass


def find_from_html(url):
    _logger.debug('Finding from HTML: %s', url)
    
    try:
        html = lxml.html.parse(url)
    except IOError as error:
        raise Error(error)
    
    for link in html.xpath('/html/head/link[@type]'):
        mime_type = link.get('type')
        
        if not STRICT_MIME_TYPES:
            mime_type = mime_type.strip().lower()
        
        try:
            mime_type = MimeType(mime_type)
        except ValueError:
            continue
        
        url = link.get('href')
        
        if url is None:
            _logger.warn('<LINK> element without @href attribute: %s',
                lxml.html.tostring(link))
            continue
        
        rel = link.get('rel')
        
        if STRICT_RSS_REL and (mime_type is MimeType.RSS) and (rel != RSS_REL):
            _logger.warn('<LINK> element with invalid @rel attribute: %s',
                lxml.html.tostring(link))
            continue
        
        yield Feed(
            url = url,
            mime_type = mime_type,
            relation = rel,
            title = link.get('title'))


def find_from_url_paths(url):
    _logger.debug('Finding from URL paths: %s', url)
    
    parts = urlparse.urlparse(url)
    path = parts.path
    paths_discovery = set(PATHS_DISCOVERY)
    
    if PATHS_DISCOVERY_TRAILING_SLASH:
        for extra_path in PATHS_DISCOVERY:
            paths_discovery.add(extra_path + '/')
    
    if path not in paths_discovery:
        for extra_path in paths_discovery:
            parts = list(parts)
            parts[2] = extra_path
            
            extra_url = urlparse.urlunparse(parts)
            _logger.debug('Checking extra URL: %s', extra_url)
            
            try:
                # TODO: Ensure that the content looks like a feed.
                requests.head(url).raise_for_status()
            except requests.HTTPError:
                continue
            
            # TODO: Get MIME type (and other details?) from HTTP headers.
            yield Feed(url = extra_url)


# TODO: Reuse the other URL split.
def find_from_url_words(url):
    _logger.debug('Finding from URL words: %s', url)
    
    parts = urlparse.urlparse(url)
    
    for component in reversed(unipath.Path(parts.path).components()):
        print component
    
    raise StopIteration()


args = sys.argv[1:]

if len(args) != 1:
    sys.exit('Usage: URL')

# TODO: Leverage `feedfinder2`?
(url,) = args
feeds = set()
finders = []

if FIND_FROM_HTML:
    finders.append(find_from_html)

if FIND_FROM_URL_PATHS:
    finders.append(find_from_url_paths)

if FIND_FROM_URL_WORDS:
    finders.append(find_from_url_words)

for finder in finders:
    try:
        for feed in finder(url):
            if feed not in feeds:
                print unicode(feed)
                feeds.add(feed)
    except Error as error:
        _logger.error(error)
