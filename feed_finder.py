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
# TODO: Verify URL's point to actual Sitemaps? http://www.esquire.com.tr
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


    def __eq__(self, other):
        return hash(self) == hash(other)
    
    
    def __hash__(self):
        return hash(self.url)


    def __unicode__(self):
        if self.title is None:
            return self.url
        else:
            return '%s <%s>' % (self.title, self.url)


class Finder (object):
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        
        self._ignore_xml_ns = True
        self._rss_rel = 'alternate'
        self._strict_link_el_loc = False
        self._strict_mime_types = False
        self._strict_rss_rel = False
        self._walk_urls_up = True


    def find(self, url):
        if self._walk_urls_up:
            parent_urls = self._walk_url_up(url)
        else:
            parent_urls = [url]
        
        for parent_url in parent_urls:
            for feed in self.find_in_html(parent_url):
                yield feed


    def find_in_anchor_links(self, html, base_url):
        self._logger.debug('Finding in HTML anchor links')
        
        for anchor in html.xpath('//a[@href]'):
            url = anchor.get('href')

            if self._is_feed_like_url(url):
                title = anchor.get('title')

                if title is None:
                    title = anchor.text_content()

                yield Feed(
                    url = urlparse.urljoin(base_url, url),
                    title = title)
    
    
    def find_in_auto_discovery(self, html, base_url):
        self._logger.debug('Finding in auto-discovery')
        link_xpath = 'link[@type]'
        
        if self._strict_link_el_loc:
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


    def _find_sitemaps(self, url):
        parsed_url = purl.URL(url)
        urls = set(self._find_sitemaps_in_robots_txt(url))
        
        urls.update(self._find_sitemaps_in_index(parsed_url))
        urls.add(unicode(parsed_url.add_path_segment('sitemap.xml')))
        
        return urls


    def _find_sitemaps_in_index(self, url):
        self._logger.debug('Finding sitemaps in sitemap index')
        
        url = unicode(url.add_path_segment('sitemap_index.xml'))
        (sitemap_tag, loc_tag) = ('sitemap', 'loc')
        
        if self._ignore_xml_ns:
            sitemap_tag = '*[local-name() = "%s"]' % sitemap_tag
            loc_tag = '*[local-name() = "%s"]' % loc_tag

        try:
            index = lxml.etree.parse(url)
        except IOError:
            return []
        else:
            return index.xpath('//%s/%s/text()' % (sitemap_tag, loc_tag))


    def _find_sitemaps_in_robots_txt(self, url):
        self._logger.debug('Finding sitemaps in robots.txt')
        return reppy.cache.RobotsCache().fetch(url).sitemaps


    def _is_feed_like_url(self, url):
        segments = set(purl.URL(url.lower()).path_segments())
        return ('feed' in segments) or ('rss' in segments)
    
    
    def _walk_url_up(self, url):
        url = purl.URL(url)
        segments = list(url.path_segments())
        
        while True:
            yield unicode(url.path_segments(segments))
            
            if len(segments) > 0:
                segments.pop()
            else:
                break


if __name__ == '__main__':
    import sys
    args = sys.argv[1:]

    if len(args) != 1:
        sys.exit('Usage: URL')
    
    logging.basicConfig(level = logging.DEBUG)
    (url,) = args
    finder = Finder()
    seen_feeds = set()

    for sitemap_url in finder._find_sitemaps(url):
        print ('\t' + sitemap_url).encode('UTF-8')

    print 30 * '-'
    
    for feed in finder.find(url):
        if feed not in seen_feeds:
            print ('\t%s' % feed).encode('UTF-8')
            seen_feeds.add(feed)
