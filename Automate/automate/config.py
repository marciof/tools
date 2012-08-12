# -*- coding: UTF-8 -*-


# Standard:
import copy, datetime

# External:
import fixes

# Internal:
import automate.util


_DEFAULT = {
    'download': {
        'manager': {
            'default': 'fdm',
            'fdm': {
                'cache_reset_interval': datetime.timedelta(hours = 1),
                'class': 'automate.download.manager.FreeDownloadManager',
                # Download history: True = default, False = disable, else path.
                'history_file': True,
                'install_path': {
                    'key': r'SOFTWARE\Wow6432Node\FreeDownloadManager.ORG\Free Download Manager',
                    'value': 'Path',
                },
                'type_library': 'fdm.tlb',
            },
        },
        'source': {
            'hd_trailers': {
                'feed_url': 'http://feeds.hd-trailers.net/hd-trailers?format=xml',
                'languages': set(['English']),
                # Used to extract the video resolution to sort accordingly and
                # find the highest one.
                'resolution_patterns': [r'(?x) (\d{3,4}) p', r'(?x) (480 | 720 | 1080)'],
                'skip_genres': set(['Documentary', 'Musical']),
                'white_list': {
                    'nr': lambda nr: nr == 1,
                    'type': r'(?ix) \b trailer \b (?! \s+ mirror \b)',
                },
            },
            'interface_lift': {
                'feed_url': 'http://interfacelift.com/wallpaper/rss/index.xml',
                # Retry in case of sporadic HTTP Not Found errors.
                'retries_on_error': 5,
                'script_url': 'http://interfacelift.com/inc_NEW/jscript001.js',
                # Maximum YCbCr luminance value, [0 .. 255], below which an
                # image is considered to be dark and will be skipped.
                'skip_darks_below_y': 0,
            },
            'youtube': {
                'data_api': {
                    'max_results': 50,
                    # Minimum number of filtered entries, use 0 for no limit.
                    'min_results': 10,
                    # Reduce the impression of automated requests by a robot.
                    'request_wait': datetime.timedelta(seconds = 2),
                    # Retry in case of sporadic HTTP Server errors.
                    'retries_on_error': 5,
                    'uploads_url': 'https://gdata.youtube.com/feeds/base/users/%s/uploads',
                    'videos_url': 'http://gdata.youtube.com/feeds/base/videos',
                },
                # Video MIME formats by preference order, use None to disable.
                'preferred_types': ['mp4', 'x-flv'],
            },
        },
        'url': {
            'default_scheme': 'http',
        },
    },
    'logging': {
        'color': {
            'error': 'red',
            'info': 'blue',
            'warning': 'brown',
        },
        'format': {
            'date': '%Y-%m-%d %H:%M:%S',
            'message': '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        },
        'level': 'info',
    },
    'network': {
        'api': {
            'imdb': {
                # Throttle API usage: http://deanclatworthy.com/imdb/
                'request_rate': {
                    'count': 30,
                    'error': 'Exceeded API usage limit',
                    'interval': datetime.timedelta(hours = 1),
                },
                # How much alike should the movie searched for and the result
                # returned by the API be, in order to qualify as a valid match.
                'similarity': {
                    'title': {
                        # Text ratio, [0 .. 1].
                        'ratio': 0.7,
                        # Allow prefixes? # E.g. "Title: Subtitle" = "Title"
                        'prefix': True,
                    },
                    # Maximum delta difference to the current year.
                    'year': 3,
                },
            },
        },
        'headers': {
            'trailers.apple.com': {
                # Allow direct downloads.
                # http://blog.hd-trailers.net/tutorials/how-to-download-hd-trailers-from-apple/#workarounds
                'User-Agent': 'QuickTime',
            },
            'www.youtube.com': {
                # Force English regardless of IP location.
                'Accept-Language': 'en',
                # Bypass age verification.
                # http://userscripts.org/scripts/show/94184
                'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            },
        },
    },
    'system': {
        # Additional MIME types in case they're missing for the current system.
        'mime_types': {
            'video/flv': '.flv',
            'video/mov': '.mov',
        },
        # System wide paths, use None for defaults.
        'path': {
            'documents': None,
            'settings': None,
        },
    },
    'task': {
        # Search specified tasks to be run, when no exact matches are found.
        'detection': {
            # How much different should the next closest match be.
            'dissimilarity': 0.25,
            # How much alike should the closest match be.
            'similarity': 0.75,
        },
        'download': {
            'interval': datetime.timedelta(hours = 1),
        },
        'parallel': 5,
    },
}


class Configuration:
    @classmethod
    def get_default(class_):
        return automate.util.AttributeDict.apply(_DEFAULT)
    
    
    @classmethod
    def load(class_, path):
        with open(path) as file:
            user_config = automate.util.merge_dicts(eval(file.read()), _DEFAULT)
            return automate.util.AttributeDict.apply(user_config)


USER = Configuration.get_default()
