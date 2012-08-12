# -*- coding: UTF-8 -*-


# Standard:
import abc, copy, mimetypes, re

# External:
import dateutil.parser, feedparser, fixes, lxml.html

# Internal:
import automate.config, automate.download, automate.download.source.video, \
    automate.task, automate.util.io, automate.util.web


class HdTrailers (automate.task.Download):
    class __Skipped (Exception):
        @property
        def _title(self):
            return self.args[0]
    
    
    class __GenreSkipped (__Skipped):
        @property
        def __genres(self):
            return self.args[1]
        
        
        def __str__(self):
            return 'Genre skipped: %s: %s' \
                % (self._title, ', '.join(self.__genres))
    
    
    class __LanguageSkipped (__Skipped):
        @property
        def __languages(self):
            return self.args[1]
        
        
        def __str__(self):
            return 'Language skipped: %s: %s' \
                % (self._title, ', '.join(self.__languages))
    
    
    class __NotWhiteListSkipped (__Skipped):
        def __str__(self):
            return 'Skipped via white-list: ' + self._title
    
    
    class __UnsupportedUrlSource (__Skipped):
        @property
        def __url_source(self):
            return self.args[1]
        
        
        def __str__(self):
            return 'Unsupported URL source: %s: %s' \
                % (self._title, self.__url_source)
    
    
    class __YahooVideoUrl (automate.download.Url):
        _HOST_NAME = 'playlist.yahoo.com'
        
        
        @property
        def __id(self):
            if self.host_name == self._HOST_NAME:
                return self.query['sid'][0]
            else:
                return self.query['StreamID'][0]
        
        
        def __hash__(self):
            return hash(self.__id)
        
        
        def __lt__(self, url):
            if isinstance(url, type(self)):
                return self.__id < url.__id
            else:
                return automate.download.Url.__lt__(self, url)
    
    
    __YahooVideoUrl.register_host_name(__YahooVideoUrl._HOST_NAME)
    
    __YahooVideoUrl.register_host_name(
        re.compile(r'^ \w+ \.bcst\.cdn\. \w+ \.yimg\.com $',
            re.IGNORECASE + re.VERBOSE))
    
    
    __URL_SOURCE_BY_HOST_NAME = {
        'www.youtube.com': automate.download.source.video.YouTube(),
    }
    
    
    def __init__(self):
        automate.task.Download.__init__(self)
        
        self.__imdb_api = automate.util.web.ImdbApiAggregator()
        self.__reported_errors = set()
        self.__skipped_titles = set()
        self.__title_by_catalog_url = {}
    
    
    @property
    def name(self):
        return 'HD Trailers'
    
    
    @property
    def url(self):
        return automate.util.io.Url('http://www.hd-trailers.net')
    
    
    def _list_urls(self):
        Unavailable = (automate.util.web.ImdbApi.Unavailable, \
            automate.download.UrlSource.UrlUnavailable)
        
        self.logger.debug('Read feed: %s', self.__config.feed_url)
        
        for item in feedparser.parse(self.__config.feed_url).entries:
            if item.title not in self.__skipped_titles:
                try:
                    yield self.__get_video_url(item)
                except Unavailable as error:
                    if error not in self.__reported_errors:
                        self.logger.warning(error)
                        self.__reported_errors.add(error)
                except self.__Skipped as error:
                    self.logger.debug(error)
                    self.__skipped_titles.add(item.title)
    
    
    @property
    def __config(self):
        return automate.config.USER.download.source.hd_trailers
    
    
    def __get_movie_title(self, item):
        title = self.__title_by_catalog_url.get(item.link)
        
        if title is not None:
            return title
        
        [title] = automate.util.io.Url(item.link).read(parse = True).xpath(
            '//meta[@property = "og:title"]/@content')
        
        self.__title_by_catalog_url[item.link] = title
        return title
    
    
    def __get_video_type_nr(self, title):
        white_list_regex = self.__config.white_list.type
        video_type = re.findall(r'\( (.+) \)$', title.lower(), re.X)
        video_nr = 1
        
        if len(video_type) == 0:
            return (None, video_nr)
        else:
            [video_type] = video_type
        
        def take_video_nr(video_nr_match):
            nonlocal video_nr
            video_nr = int(video_nr_match.group(0))
            return ''
        
        normalization_regexes = [
            (r'n[or]\. \s+', ''),
            (r'((?:\s+ \d)?) \s+ (mirror) $', r' \2\1'),
            (r'(teaser) \s+ trailer', r'\1'),
            (r'\s+ (\d) $', take_video_nr),
            (r'.* (' + white_list_regex + r') .*', r'\1'),
        ]
        
        for substitution in normalization_regexes:
            video_type = re.sub(*(substitution + (video_type,)),
                flags = re.VERBOSE)
        
        if not re.search(white_list_regex, video_type):
            video_type = None
        
        return (video_type, video_nr)
    
    
    def __get_video_url(self, item):
        (video_type, video_nr) = self.__get_video_type_nr(item.title)
        
        if (video_type is None) or not self.__config.white_list.nr(video_nr):
            raise self.__NotWhiteListSkipped(item.title)
        
        config = self.__config
        title = self.__get_movie_title(item)
        genres = config.skip_genres & self.__imdb_api.get_genres(title)
        
        if len(genres) > 0:
            raise self.__GenreSkipped(title, genres)
        
        languages = self.__imdb_api.get_languages(title)
        
        if len(config.languages & languages) == 0:
            raise self.__LanguageSkipped(title, languages)
        
        if hasattr(item, 'enclosures') and (len(item.enclosures) > 0):
            return self.__get_video_url_from_enclosures(item)
        else:
            return self.__get_video_url_from_source(item, title)
    
    
    def __get_video_url_from_enclosures(self, item):
        enclosures = copy.deepcopy(item.enclosures)
        
        def video_resolution_and_size(enclosure):
            for pattern in self.__config.resolution_patterns:
                resolution = re.findall(pattern, enclosure.href)
                
                if len(resolution) > 0:
                    return int(resolution[0])
            
            # Fallback to video's reported size in the enclosure itself.
            return int(enclosure.length)
        
        enclosures.sort(key = video_resolution_and_size, reverse = True)
        ext = mimetypes.guess_extension(enclosures[0].type, strict = False)
        
        # Can't use item's ID as it might not point to the video watch URL
        # associated with this video download URL. Also, resort to the original
        # enclosure if necessary, as it sometimes gets a different URL for the
        # enclosure link.
        watch_url = self.__get_watch_url(item, enclosures[0].href) \
            or self.__get_watch_url(item, item.feedburner_origenclosurelink)
        
        url = automate.download.Url(enclosures[0].href,
            comment = watch_url,
            save_as = automate.util.io.Path.clean_file_name(item.title) + ext,
            title = item.title)
        
        return automate.download.Url.from_host_name(url)
    
    
    def __get_watch_url(self, item, video_url):
        content = lxml.html.fromstring(item.content[0].value)
        
        download_caption = content.xpath('//a[@href = $url]/text()',
            url = video_url)
        
        if len(download_caption) == 0:
            self.logger.warning('Watch URL not found: %s', video_url)
            return None
        
        [url] = content.xpath('//a[text() = $caption and @href != $url]/@href',
            caption = download_caption.pop(),
            url = video_url)
        
        return url
    
    
    def __get_video_url_from_source(self, item, title):
        url = automate.util.io.Url(item.source.href)
        url_source = self.__URL_SOURCE_BY_HOST_NAME.get(url.host_name)
        
        if url_source is None:
            raise self.__UnsupportedUrlSource(title, url)
        
        return url_source.get_video_url(url)


class IgnShow (automate.task.Download, automate.download.source.video.YouTube):
    @property
    def url(self):
        return automate.util.io.Url(
            'http://www.youtube.com/show/' + self._show_name)
    
    
    def _list_urls(self):
        for url in self.list_feed_video_urls(
                author = 'IGNentertainment',
                query = self._show_name,
                filter = self._search_filter):
            yield url
    
    
    def _pre_process_video_title(self, title):
        if not title.startswith(self.name):
            # Move show's name to the start.
            title = re.sub(
                r'^ (.+?) \s* - \s* (%s .+) $' % re.escape(self.name),
                r'\2: \1', title, flags = re.VERBOSE)
        
        # Remove non-white-space character between the show's name and date.
        title = re.sub(
            r'(?<= %s) [^\s] (?= \s)' % re.escape(self.name),
            '', title, flags = re.VERBOSE)
        
        def american_to_iso_date(match):
            [date] = match.groups()
            return dateutil.parser.parse(date).date().isoformat()
        
        return re.sub(r'(\d{2} \. \d{2} \. \d{2})',
            american_to_iso_date, title, flags = re.VERBOSE)
    
    
    @property
    def _search_filter(self):
        return None
    
    
    @abc.abstractproperty
    def _show_name(self):
        raise NotImplementedError


class IgnDailyFix (IgnShow):
    @property
    def name(self):
        return 'IGN Daily Fix'
    
    
    def _pre_process_video_title(self, title):
        return IgnShow._pre_process_video_title(self,
            # Fix incomplete show's name.
            title.replace('- ' + self._search_filter, '- ' + self.name))
    
    
    @property
    def _search_filter(self):
        # It might not start with "IGN".
        return 'Daily Fix'
    
    
    @property
    def _show_name(self):
        return 'dailyfix'


class IgnWeeklyWood (IgnShow):
    @property
    def name(self):
        return "IGN Weekly 'Wood"
    
    
    def _pre_process_video_title(self, title):
        # Remove repeated occurrences of the show's name from the start.
        title = re.sub(r'^(%s - )+' % re.escape(self.name), '', title)
        
        if '- Weekly' in title:
            # Fix incomplete show's name.
            title = title.replace('- Weekly', '- IGN Weekly')
        else:
            # Add show's name before the date, unless it's already there.
            title = re.sub(
                r'(?<!%s) \s* : \s* ([.\d]+) $' % re.escape(self.name),
                r' - %s \1' % self.name,
                title,
                flags = re.VERBOSE)
        
        return IgnShow._pre_process_video_title(self, title)
    
    
    @property
    def _show_name(self):
        return 'ignweeklywood'


class MinutePhysics \
        (automate.task.Download, automate.download.source.video.YouTube):
    
    @property
    def name(self):
        return 'Minute Physics'
    
    
    @property
    def url(self):
        return automate.util.io.Url('http://www.youtube.com/user/minutephysics')
    
    
    def _list_urls(self):
        for url in self.list_feed_video_urls('minutephysics'):
            yield url
    
    
    def _pre_process_video_title(self, title):
        if title.startswith(self.name):
            return title
        else:
            return self.name + ': ' + title


class TheLonelyIsland \
        (automate.task.Download, automate.download.source.video.YouTube):
    
    @property
    def name(self):
        return 'The Lonely Island'
    
    
    @property
    def url(self):
        return automate.util.io.Url(
            'http://www.youtube.com/user/thelonelyisland')
    
    
    def _list_urls(self):
        for url in self.list_feed_video_urls('thelonelyisland'):
            yield url
    
    
    def _pre_process_video_title(self, title):
        return self.name + ': ' + title
