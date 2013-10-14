#!/usr/bin/env python
# -*- coding: UTF-8 -*-


"""
What's currently searched for:

* RSS auto-discovery: http://www.rssboard.org/rss-autodiscovery
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import logging
import sys
import urlparse

# External:
import enum
import lxml.html


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
        return '%s <%s> %s %s' % (
            '?' if self.title is None else repr(self.title),
            self.url,
            self.mime_type,
            '?' if self.relation is None else repr(self.relation))


# TODO: Leverage `feedfinder2`?
# TODO: Detect Atom feeds.
# TODO: Convert links to absolute, even when <BASE> is missing.
class Finder (object):
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        
        self._rss_rel = 'alternate'
        self._strict_link_el_location = False
        self._strict_mime_types = False
        self._strict_rss_rel = False
    
    
    def find_in_html(self, html_doc):
        self._logger.debug('Finding from HTML.')
        
        base_url = html_doc.base_url
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
    
            if base_url is not None:
                url = urlparse.urljoin(base_url, url)
    
            yield Feed(
                url = url,
                mime_type = mime_type,
                relation = rel,
                title = link.get('title'))


if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) != 1:
        sys.exit('Usage: URL')
    
    logging.basicConfig(level = logging.DEBUG)
    
    (url,) = args
    html_doc = lxml.html.parse(url).getroot()
    finder = Finder()
    seen_feeds = set()
    
    def log_feed(feed):
        if feed not in seen_feeds:
            print unicode(feed)
            seen_feeds.add(feed)
    
    for feed in finder.find_in_html(html_doc):
        log_feed(feed)
