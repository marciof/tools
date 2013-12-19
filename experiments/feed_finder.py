#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals


# Walking up each path segment of a URL: (URL cache?)
# * Download HTML.
#   * RSS auto-discovery.
#   * Anchors.

# * Auto-discovery from HTML.
# * Search HTML for anchors.
# * Append common suffixes to URL.
# * Search sitemaps.
# * Search robots.txt, if root URL.

# Each finder:
# * Uses a different source (e.g. URL, HTML, etc).
# * Indicates if the source is usable or not (e.g. robots.txt if only at root).


_2 = '''
"""
Sources:
* RSS auto-discovery <http://www.rssboard.org/rss-autodiscovery>.
* robots.xt <http://www.robotstxt.org> to find Sitemaps.
* HTML anchors. [1]
* Sitemaps <http://www.sitemaps.org>. [1]
* URL ending in: "/feed", "/rss".

[1] URL's with a case-insensitive path component of: "feed", "rss".

Examples:
  http://sphinx-doc.org
  http://www.thelira.com
  http://www.aksiyon.com.tr
  http://www.gazetevatan.com
  http://www.kadinlarkulubu.com
  http://www.journaldequebec.com/actualite/politique
"""


#Url.extract_sources(): URL, HTML
#Finder : object
#   .register_source(HTML)
#    .find(Source) : list<Feed>
#Feed : object
#    .url : Url


# External:
import urlobject
import urlobject.path


class Url (urlobject.URLObject):
    def walk_up(self):
        """
        :rtype: collections.Iterator<Url>
        """

        url = self
        yield url

        while url.path.segments != ('',):
            url = url.with_path(
                urlobject.path.URLPath.join_segments(
                    url.path.segments[:-1]))

            yield url


class Finder (object):
    def search(self, url):
        """
        :type url: Url
        :rtype: collections.Iterator<Feed>
        """

        raise NotImplementedError()


class RssAutoDiscoveryFinder (Finder):
    def search(self, url):
        return []


if __name__ == '__main__':
    # Standard:
    import sys

    args = sys.argv[1:]

    if len(args) != 1:
        sys.exit('Usage: URL')

    feeds = []
    finders = [RssAutoDiscoveryFinder()]

    for url in Url(args[0]).walk_up():
        for finder in finders:
            feeds.extend(finder.search(url))

    seen_urls = set()

    for feed in feeds:
        if feed.url not in seen_urls:
            print 30 * '-'
            print unicode(feed)
            seen_urls.add(feed.url)
'''


_1 = '''
import itertools
import logging
import urlparse

# External:
import enum
import lxml.etree
import lxml.html
import purl
import reppy.cache
import requests
import werkzeug.http
import zope.contenttype


_logger = logging.getLogger(__name__)


class MimeType (enum.Enum):
    RSS = 'application/rss+xml'


class Feed (object):
    def __init__(self, url, mime_type = None, relation = None, title = None):
        self.url = url
        self.mime_type = mime_type
        self.relation = relation
        self.title = title


    def __unicode__(self):
        if self.title is None:
            return self.url
        else:
            return '%s <%s>' % (self.title, self.url)


# TODO: Check that URL's are RSS feeds.
def find_in_anchor_links(html, base_url):
    """
    :type html: lxml.html.HtmlElement
    :type base_url: unicode
    :rtype: collections.Iterator<Feed>
    """
    
    _logger.debug('Find in anchor links')
    
    for anchor in html.xpath('//a[@href]'):
        href = anchor.get('href')

        if is_feed_like_url(purl.URL(href)):
            title = anchor.get('title')

            if title is None:
                title = anchor.text_content()

            title = title.strip()

            if title == '':
                title = None

            yield Feed(
                url = urlparse.urljoin(base_url, href),
                title = title)


# TODO: Detect Atom feeds.
def find_in_auto_discovery(html, base_url,
        strict_link_el_loc = False,
        strict_mime_types = False,
        strict_rss_rel = False):

    """
    :type html: lxml.html.HtmlElement
    :type base_url: unicode
    :type strict_link_el_loc: bool
    :type strict_mime_types: bool
    :type strict_rss_rel: bool
    :rtype: collections.Iterator<Feed>
    """

    _logger.debug('Find in auto-discovery')
    link_xpath = 'link[@type]'

    if strict_link_el_loc:
        link_xpath = '/html/head/' + link_xpath
    else:
        link_xpath = '//' + link_xpath

    for link in html.xpath(link_xpath):
        mime_type = link.get('type')

        if not strict_mime_types:
            mime_type = mime_type.strip().lower()

        try:
            mime_type = MimeType(mime_type)
        except ValueError:
            continue

        href = link.get('href')

        if href is None:
            _logger.warn('Missing "href" attribute: %s',
                lxml.html.tostring(link))
            continue

        rel = link.get('rel')

        is_rel_invalid = (strict_rss_rel
            and (mime_type is MimeType.RSS)
            and (rel != 'alternate'))

        if is_rel_invalid:
            _logger.warn('Invalid "rel" attribute: %s',
                lxml.html.tostring(link))
            continue

        yield Feed(
            url = urlparse.urljoin(base_url, href),
            mime_type = mime_type,
            relation = rel,
            title = link.get('title'))


def find_in_html(response, url):
    """
    :type response: requests.Response
    :type url: purl.URL
    :rtype: collections.Iterator<Feed>
    """
    
    html = lxml.html.fromstring(response.content, base_url = unicode(url))
    base_url = html.base_url
    
    if base_url is None:
        base_url = unicode(url)
    
    return itertools.chain(
        find_in_auto_discovery(html, base_url),
        find_in_anchor_links(html, base_url))


def find_in_sitemap(sitemap, url):
    """
    :type sitemap: str
    :type url: purl.URL
    :rtype: collections.Iterator<Feed>
    """

    _logger.debug('Find in sitemap')
    sitemap = lxml.etree.fromstring(sitemap, base_url = unicode(url))
    return []


def find_sitemaps_in_index(url, strict_xml_ns = False):
    """
    :type url: purl.URL
    :type strict_xml_ns: bool
    :rtype: collections.Iterator<purl.URL>
    """

    url = unicode(url.add_path_segment('sitemap_index.xml'))
    _logger.debug('Find sitemaps in sitemap index: %s', url)
    (sitemap_tag, loc_tag) = ('sitemap', 'loc')

    if not strict_xml_ns:
        sitemap_tag = '*[local-name() = "%s"]' % sitemap_tag
        loc_tag = '*[local-name() = "%s"]' % loc_tag

    response = requests.get(url)
    response.raise_for_status()

    if not is_xml(response):
        _logger.debug('Sitemap index not XML')
        return []

    index = lxml.etree.fromstring(response.text, base_url = url)
    return map(purl.URL, index.xpath('//%s/%s/text()' % (sitemap_tag, loc_tag)))


def find_sitemaps_in_robots_txt(url):
    """
    :type url: purl.URL
    :rtype: collections.Iterator<purl.URL>
    """

    _logger.debug('Find sitemaps in robots.txt')
    return map(purl.URL, reppy.cache.RobotsCache().fetch(unicode(url)).sitemaps)


def is_feed_like_url(url):
    """
    :type url: purl.URL
    :rtype: bool
    """
    
    segments = set([segment.lower() for segment in url.path_segments()])
    return ('feed' in segments) or ('rss' in segments)


def is_html(response):
    """
    :type response: requests.Response
    :rtype: bool
    """

    mime_type = find_content_type(response)
    return mime_type in set(['application/xhtml+xml', 'text/html'])


def is_xml(response):
    """
    :type response: requests.Response
    :rtype: bool
    """

    mime_type = find_content_type(response)

    return (mime_type.endswith('+xml')
        or (mime_type in set(['application/xml', 'text/xml'])))


def find_content_type(response):
    """
    :type response: requests.Response
    :rtype: unicode
    """

    content_type = response.headers.get('Content-Type')

    if content_type is None:
        return guess_content_type(response.content)
    else:
        (mime_type, options) = werkzeug.http.parse_options_header(
            response.headers['Content-Type'])

        return mime_type


def guess_content_type(data):
    """
    :type data: str
    :rtype: unicode
    """

    (content_type, enc) = zope.contenttype.guess_content_type(body = data)

    # Further heuristics for HTML detection.
    if content_type.startswith('text/') and not content_type.endswith('/html'):
        for hint in (b']]>', b'<?'):
            if hint in data:
                return 'text/html'

    _logger.debug('Content type guess: %s', content_type)
    return content_type

    logging.basicConfig(level = logging.DEBUG)

    # TODO: Handle sitemap indices.
    sitemap_urls = set(find_sitemaps_in_robots_txt(start_url))

    for url in walk_url_up(start_url):
        response = requests.get(url)
        
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            pass
        else:
            if is_html(response):
                feeds.extend(find_in_html(response, url))

        try:
            sitemap_urls.update(find_sitemaps_in_index(url))
        except requests.HTTPError as error:
            pass

        sitemap_urls.add(url.add_path_segment('sitemap.xml'))

    for url in sitemap_urls:
        response = requests.get(url)

        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            pass
        else:
            if is_xml(response):
                feeds.extend(find_in_sitemap(response.content, url))
'''
