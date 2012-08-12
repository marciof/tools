# -*- coding: UTF-8 -*-


# Standard:
import email, json, re, threading, time, urllib.parse

# External:
import feedparser, fixes, locale

# Internal:
import automate.config, automate.download, automate.util.io


class YouTube (automate.download.UrlSource, automate.util.io.Logger):
    class __CaptchaError (automate.download.UrlSource.UrlUnavailable):
        def __init__(self, page_url):
            automate.download.UrlSource.UrlUnavailable.__init__(self,
                'YouTube captcha found: %s' % page_url)
    
    
    class __LiveEventError (automate.download.UrlSource.UrlUnavailable):
        def __init__(self, page_url):
            automate.download.UrlSource.UrlUnavailable.__init__(self,
                'YouTube live event: %s' % page_url)
    
    
    class __VideoUrl (automate.download.Url):
        @property
        def __id(self):
            return self.query['id'][0]
        
        
        def __hash__(self):
            return hash(self.__id)
        
        
        def __lt__(self, url):
            if isinstance(url, type(self)):
                return self.__id < url.__id
            else:
                return automate.download.Url.__lt__(self, url)
    
    
    __VideoUrl.register_host_name(
        re.compile(r'\.c\.youtube\.com $', re.IGNORECASE + re.VERBOSE))
    
    
    # Prevent multiple parallel requests from the same IP address.
    __API_REQUEST_GUARD = threading.Lock()
    
    
    def __init__(self):
        automate.download.UrlSource.__init__(self)
        automate.util.io.Logger.__init__(self, 'YouTube')
    
    
    def get_video_url(self, page_url):
        """
        @see: http://userscripts.org/scripts/show/25105
        """
        
        api_config = self.__config.data_api
        
        page_html = self.__do_api_request(lambda: page_url.read(
            max_retries = api_config.retries_on_error,
            parse = True))
        
        if page_html.xpath('boolean(//form[@action = "/das_captcha"])'):
            raise self.__CaptchaError(page_url)
        
        if page_url.path.components[1] != 'watch':
            feed_url = api_config.uploads_url % page_url.path.components[-1]
            
            items = self.__do_api_request(lambda:
                feedparser.parse(feed_url).entries)
            
            items.sort(key = lambda item: item.updated, reverse = True)
            return self.get_video_url(automate.util.io.Url(items[0].link))
        
        url = self.__get_preferred_video_url(
            self.__get_video_formats(page_html, page_url))
        
        [title] = page_html.xpath('//meta[@property = "og:title"]/@content')
        title = self._pre_process_video_title(title)
        
        query = url.query
        url.comment = page_url
        url.title = title
        
        # The title is used for the video file name, so clean it first.
        query['title'] = automate.util.io.Path.clean_file_name(title)
        
        url.query = query
        return url
    
    
    def list_feed_video_urls(self, author, query = None, filter = None):
        api_config = self.__config.data_api
        max_results = api_config.max_results
        
        url_query = {
            'author': author,
            'max-results': max_results,
            'orderby': 'published',
        }
        
        if query is not None:
            url_query['q'] = query
        
        # An empty string is always present in any string.
        if filter is None:
            filter = ''
        
        nr_urls_found = 0
        start_index = 1
        
        while nr_urls_found < api_config.min_results:
            url_query['start-index'] = start_index
            
            feed_url = automate.util.io.Url(
                url = api_config.videos_url,
                query = url_query)
            
            items = self.__do_api_request(lambda:
                feedparser.parse(str(feed_url)).entries)
            
            for item in items:
                if filter in item.title:
                    nr_urls_found += 1
                    
                    try:
                        yield self.get_video_url(
                            automate.util.io.Url(item.link))
                    except self.UrlUnavailable as error:
                        self.logger.warning(error)
                        
                        if isinstance(error, self.__CaptchaError):
                            raise StopIteration(error)
            
            start_index += max_results
    
    
    def _pre_process_video_title(self, title):
        return title
    
    
    @property
    def __config(self):
        return automate.config.USER.download.source.youtube
    
    
    def __do_api_request(self, request):
        with self.__API_REQUEST_GUARD:
            time.sleep(self.__config.data_api.request_wait.total_seconds())
            
            try:
                return request()
            except automate.util.io.NETWORK_ERROR as error:
                raise self.UrlUnavailable(error)
    
    
    def __get_preferred_video_url(self, formats):
        preferred_types = self.__config.preferred_types
        
        if preferred_types is None:
            return self.__VideoUrl(formats['url'][0])
        
        # The highest quality URL isn't located in the "itag" key.
        urls = [formats['url'][0]]
        
        for url_spec in formats['itag']:
            url = re.findall(r'^ \d+ ,url= (.+)', url_spec, flags = re.VERBOSE)
            if len(url) == 1:
                urls.append(url[0])
        
        types = []
        
        for cont_type in ('Content-Type: %s\n\n' % t for t in formats['type']):
            types.append(
                email.message_from_string(cont_type).get_content_subtype())
        
        highest_quality = formats['quality'][0]
        best_pref = float('inf')
        best_url = urls[0]
        
        for type, url, quality in zip(types, urls, formats['quality']):
            if quality != highest_quality:
                break
            
            for pref, preferred_type in enumerate(preferred_types):
                if (type == preferred_type) and (pref < best_pref):
                    best_pref = pref
                    best_url = url
        
        return self.__VideoUrl(best_url)
    
    
    def __get_video_formats(self, page_html, page_url):
        flash_vars = page_html.xpath(
            '//*[@id = "watch-player"]/embed/@flashvars')
        
        if len(flash_vars) == 0:
            # JavaScript based <embed>.
            flash_vars = page_html.xpath(
                '//script[contains(text(), "flashvars")]/text()')
            
            if len(flash_vars) == 0:
                is_live_event = page_html.xpath(
                    '//script[contains(text(), " yt.www.livestreaming.")]')
                
                if is_live_event:
                    raise self.__LiveEventError(page_url)
                
                # Otherwise fail miserably.
            
            flash_vars = re.findall(r'flashvars \s* = \s* \\" ([^"]+) \\"',
                flash_vars[0], flags = re.VERBOSE)
            
            flash_vars = json.loads('{"value": "%s"}' % flash_vars)['value']
        else:
            # HTML based <embed>.
            [flash_vars] = flash_vars
        
        return urllib.parse.parse_qs(
            urllib.parse.parse_qs(flash_vars)['url_encoded_fmt_stream_map'][0])
