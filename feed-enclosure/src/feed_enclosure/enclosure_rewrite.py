# -*- coding: UTF-8 -*-

"""
Rewrites enclosure URLs to have the best quality possible.
"""

# stdlib
import argparse
import re
from typing import List, Optional


MODULE_DOC = __doc__.strip()


# TODO accept feeds.ign.com URLs and follow HTTP redirection?
def is_ign_daily_fix_url(url: str) -> bool:
    return re.search(r'://assets\d*\.ign\.com/videos/', url) is not None


# TODO verify final URL is valid?
def rewrite_ign_daily_fix_url(url: str) -> str:
    """
    Upgrades to the highest resolution available.
    """
    return re.sub(r'/\d+/([\dA-Fa-f]+)-\d+-', r'/1920/\g<1>-3906000-', url)


# TODO add IGN Daily Fix support to youtube-dl?
#      https://github.com/ytdl-org/youtube-dl/tree/master#adding-support-for-a-new-site
#      https://github.com/ytdl-org/youtube-dl/issues/24771
def process_url(url: str) -> str:
    if is_ign_daily_fix_url(url):
        return rewrite_ign_daily_fix_url(url)
    else:
        return url


def parse_args(args: Optional[List[str]]) -> str:
    parser = argparse.ArgumentParser(description=MODULE_DOC)
    parser.add_argument('url', help='URL to rewrite')
    parsed_args = parser.parse_args(args)
    return parsed_args.url


def main(args: Optional[List[str]] = None) -> None:
    url = parse_args(args)
    print(process_url(url))


# TODO tests, refactor as library?
if __name__ == '__main__':
    main()
