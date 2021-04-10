#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Rebuilds RSS/Atom feeds into RSS so that the "best" enclosures are chosen.
Enclosure URLs will also have their associated feed entry title saved in the
URL fragment part as a filename, so downloaders can use it if/when needed.

Input: stdin in XML feed format
Output: stdout in RSS feed format
"""

# stdlib
import logging
from os.path import splitext
import sys
from typing import List, TextIO, Union
from urllib.parse import urldefrag, urlparse

# external
from feedgen import feed as feedgen
import feedparser


def create_logger(name: str = None) -> logging.Logger:
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    return logger


def list_parsed_feed_entry_enclosure_urls(
        feed_entry: feedparser.FeedParserDict,
        logger: logging.Logger) -> List[str]:

    urls = []

    if 'feedburner_origenclosurelink' in feed_entry:
        urls.append(feed_entry.feedburner_origenclosurelink)

    for enclosure in feed_entry.enclosures:
        urls.append(enclosure['href'])

    for media in feed_entry.media_content:
        urls.append(media['url'])

    logger.debug('Enclosure URLs in "%s": %s', feed_entry.title, urls)
    return urls


def add_title_filename_to_url(url: str, title: str) -> str:
    """
    Adds a title for downloaders to use when the original URL filename
    isn't human readable.
    """

    (defrag_url, fragment) = urldefrag(url)
    path = urlparse(defrag_url).path
    (file_root, file_ext) = splitext(path)

    return defrag_url + '#' + title + file_ext


def rebuild_parsed_feed_entry(
        feed_entry: feedparser.FeedParserDict,
        new_feed: feedgen.FeedGenerator,
        logger: logging.Logger) -> feedgen.FeedEntry:

    new_feed_entry = new_feed.add_entry()
    new_feed_entry.title(feed_entry.title)
    logger.debug('Rebuilding entry: ', feed_entry.title)

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
        new_feed_entry.content(
            content = feed_entry.content[0]['value'],
            type='')

    return new_feed_entry


def rebuild_parsed_feed(
        feed: feedparser.FeedParserDict,
        logger: logging.Logger) -> feedgen.FeedGenerator:

    new_feed = feedgen.FeedGenerator()

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
        logger.warning('No feed description found, setting it anyway.')
        new_feed.description('-')

    return new_feed


def rebuild_feed(feed_xml: Union[str, TextIO], logger: logging.Logger) -> str:
    parsed_feed = feedparser.parse(feed_xml)
    new_feed = rebuild_parsed_feed(parsed_feed, logger)

    for feed_entry in parsed_feed.entries:
        new_feed_entry = rebuild_parsed_feed_entry(feed_entry, new_feed, logger)
        urls = list_parsed_feed_entry_enclosure_urls(feed_entry, logger)

        if len(urls) > 0:
            url = add_title_filename_to_url(urls[0], feed_entry.title)
            logger.info('Enclosure URL for "%s": %s', feed_entry.title, url)
            new_feed_entry.enclosure(url = url, type = '')
        else:
            logger.warning('No enclosure URLs found in "%s".', feed_entry.title)

    return new_feed.rss_str(pretty = True).decode()


if __name__ == '__main__':
    # `feedparser` for some reason breaks on encoding stdin unless it's
    # passed already as a string.
    print(rebuild_feed(sys.stdin.read(), logger = create_logger()))
