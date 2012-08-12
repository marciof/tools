# -*- coding: UTF-8 -*-


# Standard library:
import abc, datetime, httplib, os, re, sys, Tkinter, urllib2, urlparse

# External modules:
import feedparser, fixes, lxml.etree, lxml.html, PIL.Image

# Internal modules:
import automate.util


NETWORK_ERROR = (socket.error, httplib.HTTPException, urllib2.URLError)


class GameTrailersVideos (DownloadSource):
    BASE_URL = 'http://www.gametrailers.com'
    
    _CASUAL_GAMES_PLATFORMS = set(['Android', 'iPad', 'iPhone', 'minis',
        'Mobile', 'PlayStation Network', 'WiiWare', 'Xbox Live Arcade'])
    
    _MAIN_GAMES_PLATFORMS = set(['PC', 'PlayStation 2', 'PlayStation 3',
        'Xbox', 'Xbox 360'])
    
    
    def __init__(self,
            skip_cam_videos = False,
            skip_casual_games = False,
            skip_indie_games = False):
        
        DownloadSource.__init__(self)
        
        self._skip_cam_videos = skip_cam_videos
        self._skip_casual_games = skip_casual_games
        self._skip_indie_games = skip_indie_games
        
        self._skipped_urls = set()
    
    
    def get_video_url(self, page_url):
        if page_url in self._skipped_urls:
            raise VideoUrlUnavailable()
        
        try:
            page_html = page_url.open().read()
        except automate.util.NETWORK_ERROR as error:
            self.logger.error('%s: %s', error, page_url)
            raise VideoUrlUnavailable()
        
        page = lxml.html.fromstring(page_html)
        
        if self._skip_indie_game(page, page_url) \
                or self._skip_casual_game(page, page_url):
            raise VideoUrlUnavailable()
        
        video_id = self._get_video_id(page, page_html, page_url)
        url = self._get_video_url_from_html(page, video_id) \
            or self._get_flash_video_url(page_url)
        
        if (url is not None) and not self._skip_cam_video(url, page, page_url):
            url.comment = page_url
            url.save_as = self._get_readable_file_name(page, url)
            return url
        
        raise VideoUrlUnavailable()
    
    
    def _get_flash_video_url(self, page_url):
        self.logger.debug('QuickTime video URL not found: %s', page_url)
        
        # From <http://userscripts.org/scripts/show/46320>.
        info_url = automate.util.Url('http://www.gametrailers.com/neo/',
            query = {
                'movieId': page_url.path.name,
                'page': 'xml.mediaplayer.Mediagen',
            })
        
        try:
            info_xml = lxml.etree.parse(unicode(info_url))
        except (IOError, lxml.etree.XMLSyntaxError) as error:
            self.logger.error(error)
        else:
            return automate.util.Url(
                info_xml.xpath('//rendition/src/text()')[0])
    
    
    def _get_game_title(self, page):
        [game_title] = page.xpath('//*[@class = "GameTitle"]/text()')
        return game_title
    
    
    def _get_readable_file_name(self, page, video_url):
        [video_title] = page.xpath('//*[@class = "movieTitle"]/text()')
        
        file_name = '%s (%s)%s' % (
            self._get_game_title(page),
            re.sub(r'\s+HD$', '', video_title),
            video_url.path.ext)
        
        # ...
        
        self.logger.debug('File name rewrite: %s', file_name)
        return file_name
    
    
    def _get_video_id(self, page, page_html, page_url):
        video_id = re.findall(r'mov_game_id \s* = \s* (\d+)', page_html,
            re.VERBOSE)
        
        if len(video_id) > 0:
            return video_id[0]
        
        [video_title] = page.xpath('//head/title/text()')
        error_message = 'Movie ID not found: %s'
        
        if re.search('^Bonus Round: Episode \d+$', video_title):
            self.logger.debug(error_message, page_url)
        else:
            self.logger.error(error_message, page_url)
        
        self._skipped_urls.add(page_url)
        raise VideoUrlUnavailable()
    
    
    def _get_video_url_from_html(self, page, video_id):
        for video_type in ['MP4', 'WMV', 'Quicktime']:
            video_url = page.xpath('//*[@class = "Downloads"]' \
                + '/a[starts-with(text(), "%s ")]/@href' % video_type)
            
            if len(video_url) > 0:
                video_url = automate.util.Url(video_url[0])
                
                return automate.util.Url(
                    'http://trailers-ak.gametrailers.com/gt_vault/%s/%s' \
                        % (video_id, video_url.path.name))
    
    
    def _has_developer(self, page):
        developer = page.xpath('//*[@class = "developer"]/text()')
        
        if len(developer) == 0:
            raise VideoUrlUnavailable()
        else:
            return developer[0].strip() != 'N/A'
    
    
    def _has_publisher(self, page):
        publisher = page.xpath('//*[@class = "publisher"]/text()')
        
        if len(publisher) == 0:
            raise VideoUrlUnavailable()
        else:
            return publisher[0].strip() != 'N/A'
    
    
    def _is_casual_game(self, page):
        platforms = set(page.xpath('//*[@class = "platforms"]/a/text()'))
        
        nr_casual_platforms = len(platforms & self._CASUAL_GAMES_PLATFORMS)
        nr_main_platforms = len(platforms & self._MAIN_GAMES_PLATFORMS)
        
        return ((nr_casual_platforms > 0) and (nr_main_platforms == 0)) \
            or (nr_casual_platforms > nr_main_platforms)
    
    
    def _skip_cam_video(self, video_url, page, page_url):
        if self._skip_cam_videos:
            [page_title] = page.xpath('//head/title/text()')
            
            is_cam_video = (video_url.path.stem.find('_cam_') > 0) \
                or (page_title.find(' (Cam) ') > 0) \
                or (page_title.find(' (Stream) ') > 0)
            
            if is_cam_video:
                self.logger.warning('Skip cam video: %s <%s>',
                    self._get_game_title(page), page_url)
                
                self._skipped_urls.add(page_url)
                return True
        
        return False
    
    
    def _skip_casual_game(self, page, page_url):
        if self._skip_casual_games and self._is_casual_game(page):
            self.logger.warning('Skip casual game: %s <%s>',
                self._get_game_title(page), page_url)
            
            self._skipped_urls.add(page_url)
            return True
        else:
            return False
    
    
    def _skip_indie_game(self, page, page_url):
        skip_game = self._skip_indie_games \
            and (not self._has_publisher(page)
                or not self._has_developer(page))
        
        if skip_game:
            self.logger.warning('Skip indie game: %s <%s>',
                self._get_game_title(page), page_url)
            
            self._skipped_urls.add(page_url)
            return True
        else:
            return False


class GameTrailersNewestGameVideos (GameTrailersVideos):
    def __init__(self, game):
        GameTrailersVideos.__init__(self)
        self._game = game
    
    
    def list_urls(self):
        main_url = automate.util.Url(self.BASE_URL + '/game/' + self._game)
        
        try:
            main_html = lxml.html.fromstring(main_url.open().read())
        except automate.util.NETWORK_ERROR as error:
            self.logger.error('%s: %s', error, main_url)
            return
        
        videos = main_html.xpath(
            '//*[@id = "GamepageMedialistFeatures"]' \
            + '//*[@class = "newestlist_movie_format_SDHD"]/a[1]/@href')
        
        for page_url in [automate.util.Url(self.BASE_URL + p) for p in videos]:
            try:
                yield self.get_video_url(page_url)
            except VideoUrlUnavailable:
                pass


class GameTrailers (GameTrailersVideos):
    def __init__(self, systems = []):
        GameTrailersVideos.__init__(self,
            skip_cam_videos = True,
            skip_casual_games = True,
            skip_indie_games = True)
        
        options = {
            'limit': 50,
            'orderby': 'newest',
            'quality[hd]': 'either',
        }
        
        for system in systems:
            options['favplats[%s]' % system] = system
        
        self._feed_url = automate.util.Url(self.BASE_URL + '/rssgenerate.php',
            query = options)
    
    
    def list_urls(self):
        white_list_re = r'\b(%s)\b' % '|'.join([
            'clip', 'demo', 'gameplay', 'preview', 'review', 'teaser',
            'trailer', 'vignette', 'Walkthrough'
        ])
        
        for entry in feedparser.parse(unicode(self._feed_url)).entries:
            if re.search(r'\b Japanese \b', entry.title, re.VERBOSE):
                self.logger.warning('Skip video: %s', entry.title)
            elif re.search(white_list_re, entry.title, re.IGNORECASE):
                try:
                    yield self.get_video_url(automate.util.Url(entry.link))
                except VideoUrlUnavailable:
                    pass
    
    
    @property
    def name(self):
        return 'GameTrailers'


class GtCountdown (GameTrailersNewestGameVideos):
    def __init__(self):
        GameTrailersNewestGameVideos.__init__(self, 'gt-countdown/2111')
    
    
    @property
    def name(self):
        return 'GT Countdown'


class InterfaceLift (DownloadSource):
    def download_finished(self, url, file_path):
        if url.host_name == self._HOST_NAME:
            image = PIL.Image.open(file_path)
            image.save(file_path, quality = 85)


class PopFiction (GameTrailersNewestGameVideos):
    def __init__(self):
        GameTrailersNewestGameVideos.__init__(self, 'pop-fiction/13123')
    
    
    @property
    def name(self):
        return 'Pop-Fiction'


class ScrewAttack (GameTrailersVideos):
    def list_urls(self):
        main_url = automate.util.Url(self.BASE_URL + '/screwattack')
        
        try:
            main_html = lxml.html.fromstring(main_url.open().read())
        except automate.util.NETWORK_ERROR as error:
            self.logger.error('%s: %s', error, main_url)
            return
        
        videos = main_html.xpath(
            '//*[@id = "nerd"]//a[@class = "gamepage_content_row_title"]/@href')
        
        for page_url in [automate.util.Url(self.BASE_URL + p) for p in videos]:
            try:
                yield self.get_video_url(page_url)
            except VideoUrlUnavailable:
                pass
    
    
    @property
    def name(self):
        return 'ScrewAttack'
