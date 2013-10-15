#!/usr/bin/env python
# -*- coding: UTF-8 -*-


"""
* RSS auto-discovery <http://www.rssboard.org/rss-autodiscovery>.
* robots.xt <http://www.robotstxt.org> to auto-discover Sitemaps.
* HTML anchors. [1]
* Sitemaps <http://www.sitemaps.org>. [1]
* Common URL paths: "/feed", "/rss".

[1] URL's with a path component of "rss" (case-insensitive).
"""


# TODO: Walk URL paths up to check each segment.
# TODO: Find recursively? E.g. check every URL until verified to be a feed.
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
import lxml.etree
import lxml.html
import purl
import reppy.cache


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


    def find_in_anchor_links(self, html, base_url):
        self._logger.debug('Finding in HTML anchor links')
        
        for anchor in html.xpath('//a[@href]'):
            url = anchor.get('href')

            if self.is_feed_like_url(url):
                title = anchor.get('title')

                if title is None:
                    title = anchor.text_content()

                yield Feed(
                    url = urlparse.urljoin(base_url, url),
                    title = title)
    
    
    def find_in_auto_discovery(self, html, base_url):
        self._logger.debug('Finding in auto-discovery')
        link_xpath = 'link[@type]'
        
        if self._strict_link_el_location:
            link_xpath = '/html/head/' + link_xpath
        else:
            link_xpath = '//' + link_xpath
    
        for link in html.xpath(link_xpath):
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
    
    
    def find_in_html(self, url):
        html = lxml.html.parse(url).getroot()
        base_url = html.base_url

        if base_url is None:
            base_url = url
        
        return itertools.chain(
            self.find_in_auto_discovery(html, base_url),
            self.find_in_anchor_links(html, base_url))


    def find_sitemaps(self, url):
        return set(
            self.find_sitemaps_in_robots_txt(url)
            + self.find_sitemaps_in_indices(url))


    def find_sitemaps_in_indices(self, url):
        self._logger.debug('Finding sitemaps from sitemap index')

        url = purl.URL(url).add_path_segment('sitemap_index.xml')
        urls = []

        # Ignore XML namespaces.
        SITEMAP = '*[local-name() = "sitemap"]'
        LOC = '*[local-name() = "loc"]'

        while True:
            self._logger.debug('Checking for sitemap index: %s', url)

            try:
                index = lxml.etree.parse(unicode(url))
                urls.extend(index.xpath('//%s/%s/text()' % (SITEMAP, LOC)))
            except IOError:
                pass

            segments = list(url.path_segments())

            if len(segments) > 1:
                segments.pop(-2)
                url = url.path_segments(segments)
            else:
                break

        return urls


    def find_sitemaps_in_robots_txt(self, url):
        self._logger.debug('Finding sitemaps from robots.txt')
        return reppy.cache.RobotsCache().fetch(url).sitemaps


    def is_feed_like_url(self, url):
        segments = set(purl.URL(url.lower()).path_segments())
        return ('feed' in segments) or ('rss' in segments)


if __name__ == '__main__':
    import sys
    args = sys.argv[1:]

    if len(args) != 1:
        sys.exit('Usage: URL')
    
    logging.basicConfig(level = logging.DEBUG)
    (url,) = args
    finder = Finder()

    for feed in finder.find_in_html(url):
        print unicode(feed)
