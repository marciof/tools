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

    def __init__(self, path: Path):
        self.logger = log.create_logger('opml')
        self.path = path
        self.root = None

    def iter_rss_outline(self) -> Iterator[Element]:
        for (event, elem) in ElementTree.iterparse(self.path, {'start'}):
            if self.root is None:
                self.logger.debug('OPML root element: %s', elem)
                self.root = elem
            elif elem.tag == 'outline' and elem.attrib.get('type') == 'rss':
                self.logger.debug('RSS outline: %s', elem)
                yield elem

    def set_rss_outline_attrib(self, name: str, value: str) -> None:
        for rss_outline in self.iter_rss_outline():
            rss_outline.attrib[name] = value

    def to_string(self) -> str:
        return ElementTree.tostring(self.root, encoding='unicode')

    def save_changes(self) -> None:
        content = self.to_string()
        self.logger.debug('OPML content: %s', content)

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_opml:
            temp_opml.write(content)
            temp_opml.close()

            self.logger.info('Saving: %s --> %s', temp_opml.name, self.path)
            os.replace(temp_opml.name, self.path)
