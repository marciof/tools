# -*- coding: UTF-8 -*-

# stdlib
import os
from pathlib import Path
import tempfile
from typing import Iterator
from xml.etree.ElementTree import Element

# external
# FIXME missing type stubs for some external libraries
import defusedxml.ElementTree as ElementTree  # type: ignore

# internal
from . import log


class Opml:
    """
    Spec: http://opml.org/spec2.opml
    """

    def __init__(self, path: Path):
        self.logger = log.create_logger('opml')
        self.types = {'rss', 'atom'}
        self.path = path
        self.root = None

    def iter_feed_outline(self) -> Iterator[Element]:
        for (event, el) in ElementTree.iterparse(self.path, {'start'}):
            if self.root is None:
                self.logger.debug('OPML root element: %s', el)
                self.root = el
            elif el.tag == 'outline' and el.attrib.get('type') in self.types:
                self.logger.debug('Feed outline element: %s', el)
                yield el

    def set_feed_outline_attrib(self, name: str, value: str) -> None:
        for feed in self.iter_feed_outline():
            feed.attrib[name] = value

    def to_string(self) -> str:
        return ElementTree.tostring(self.root, encoding='unicode')

    def save_changes(self) -> None:
        content = self.to_string()
        self.logger.debug('Saving content: %s', content)

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_opml:
            temp_opml.write(content)
            temp_opml.close()

            self.logger.info('Replacing: %s --> %s', temp_opml.name, self.path)
            os.replace(temp_opml.name, self.path)
