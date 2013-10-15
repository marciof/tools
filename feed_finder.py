#!/usr/bin/env python
# -*- coding: UTF-8 -*-


"""
* RSS auto-discovery <http://www.rssboard.org/rss-autodiscovery>.
* robots.xt <http://www.robotstxt.org>, to auto-discover Sitemaps.
* HTML anchors. [1]
* Sitemaps <http://www.sitemaps.org>. [1]
* Common URL paths: "/feed", "/rss".

[1] URL's with a path component of "rss" (case-insensitive).
"""


# TODO: Leverage `feedfinder2`?
# TODO: Detect Atom feeds.
# TODO: Convert all input to Unicode.
# TODO: Verify URL's point to actual feeds? E.g. http://sphinx-doc.org/rss
# TODO: Scrape HTML index pages? E.g. http://www.journaldequebec.com/rss
# TODO: Check <LINK> elements?


# Standard:
from __future__ import absolute_import, division, unicode_literals
import itertools
import logging
import urlparse

# External:
import enum
import lxml.html
import purl
import reppy.cache
import requests


class MimeType (enum.Enum):
    RSS = 'application/rss+xml'


class Feed (object):
    def __init__(self, url, mime_type = None, relation = None, title = None):
        self.url = url
        self.mime_type = mime_type
        self.relation = relation
        self.title = title


    def __unicode__(self):
        return '%s <%s> %s %s' % (
            '?' if self.title is None else repr(self.title),
            self.url,
            self.mime_type,
            '?' if self.relation is None else repr(self.relation))


class Finder (object):
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        
        self._rss_rel = 'alternate'
        self._strict_link_el_location = False
        self._strict_mime_types = False
        self._strict_rss_rel = False
    
    
    def find_in_anchor_links(self, html_doc, base_url):
        self._logger.debug('Finding in anchor links.')
        
        for anchor in html_doc.xpath('//a[@href]'):
            url = anchor.get('href')
            segments = purl.URL(url.lower()).path_segments()
            
            if 'rss' in segments:
                title = anchor.get('title')

                if title is None:
                    title = anchor.text_content()

                yield Feed(
                    url = urlparse.urljoin(base_url, url),
                    title = title)
    
    
    def find_in_auto_discovery(self, html_doc, base_url):
        self._logger.debug('Finding in auto-discovery.')
        link_xpath = 'link[@type]'
        
        if self._strict_link_el_location:
            link_xpath = '/html/head/' + link_xpath
        else:
            link_xpath = '//' + link_xpath
    
        for link in html_doc.xpath(link_xpath):
            mime_type = link.get('type')
    
            if not self._strict_mime_types:
                mime_type = mime_type.strip().lower()
    
            try:
                mime_type = MimeType(mime_type)
            except ValueError:
                continue
    
            url = link.get('href')
    
            if url is None:
                self._logger.warn('Missing "href" attribute: %s',
                    lxml.html.tostring(link))
                continue
    
            rel = link.get('rel')
            
            is_rel_invalid = (self._strict_rss_rel
                and (mime_type is MimeType.RSS)
                and (rel != self._rss_rel))
    
            if is_rel_invalid:
                self._logger.warn('Invalid "rel" attribute: %s',
                    lxml.html.tostring(link))
                continue
    
            yield Feed(
                url = urlparse.urljoin(base_url, url),
                mime_type = mime_type,
                relation = rel,
                title = link.get('title'))
    
    
    def find_in_html(self, html_doc, url):
        self._logger.debug('Finding in HTML.')
        base_url = html_doc.base_url
        
        if base_url is None:
            base_url = url
        
        return itertools.chain(
            self.find_in_auto_discovery(html_doc, base_url),
            self.find_in_anchor_links(html_doc, base_url))


def find_from_robots_txt(url):
    return reppy.cache.RobotsCache().fetch(url).sitemaps


# TODO
def find_from_indices(url):
    url = purl.URL(url).add_path_segment('sitemap_index.xml')

    while True:
        try:
            requests.head(unicode(url)).raise_for_status()
        except requests.HTTPError:
            pass

        segments = list(url.path_segments())

        if len(segments) > 1:
            segments.pop(-2)
            url = url.path_segments(segments)
        else:
            break


if __name__ == '__main__':
    import sys
    args = sys.argv[1:]

    if len(args) != 1:
        sys.exit('Usage: URL')
    
    logging.basicConfig(level = logging.DEBUG)
    
    (url,) = args
    html_doc = lxml.html.parse(url).getroot()
    finder = Finder()

    for feed in finder.find_in_html(html_doc, url):
        print unicode(feed)
