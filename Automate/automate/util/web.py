# -*- coding: UTF-8 -*-


# Standard:
import abc, datetime, difflib, re

# External:
import fixes

# Internal:
import automate.config, automate.util.io


class ImdbApi (automate.util.io.Logger):
    class Unavailable (LookupError):
        @property
        def api(self):
            return self.args[0]
        
        
        @property
        def error(self):
            return self.args[2]
        
        
        @property
        def title(self):
            return self.args[1]
        
        
        def __eq__(self, error):
            return hash(self) == hash(error)
        
        
        def __hash__(self):
            return hash(str(self))
        
        
        def __str__(self):
            return '%s (%s): %s' % (self.error, self.api.name, self.title)
    
    
    class GenreListUnavailable (Unavailable):
        def __init__(self, *args):
            ImdbApi.Unavailable.__init__(self,
                *(args + ('Genre list unavailable',)))
    
    
    class LanguageListUnavailable (Unavailable):
        def __init__(self, *args):
            ImdbApi.Unavailable.__init__(self,
                *(args + ('Language list unavailable',)))
    
    
    class SearchResultMismatch (Unavailable):
        def __init__(self, api, title, result_title, ratio):
            ImdbApi.Unavailable.__init__(self, *(api, title,
                'Not found: Got "%s" instead, with %.2f title similarity' \
                    % (result_title, ratio)))
    
    
    @abc.abstractmethod
    def get_languages(self, title):
        raise NotImplementedError
    
    
    @abc.abstractmethod
    def get_genres(self, title):
        raise NotImplementedError
    
    
    @abc.abstractmethod
    def get_year(self, title):
        raise NotImplementedError
    
    
    @abc.abstractproperty
    def name(self):
        raise NotImplementedError
    
    
    @property
    def _config(self):
        return automate.config.USER.network.api.imdb
    
    
    def _get_languages_from_title_page(self, title, title_url):
        # Can't search for links in languages' names, because sometimes there
        # aren't any.
        
        self.logger.debug('Get movie language: %s: %s', title, title_url)
        
        try:
            languages = title_url.read(parse = True).xpath(
                '//*[text() = "Language:"]/following-sibling::node()')
        except automate.util.io.NETWORK_ERROR as error:
            raise self.Unavailable(self, title, error)
        
        if len(languages) == 0:
            return set()
        
        def text_content(element):
            if isinstance(element, str):
                return element
            else:
                return element.text_content()
        
        languages = re.split(
            r'\s* \| \s*',
            ''.join(map(text_content, languages)).strip(),
            flags = re.VERBOSE)
        
        # Remove language usage details, e.g. "Japanese (a few words)".
        return set([
            re.sub(r'\s* \( [\s\w]+ \) \s* $', '', lang, flags = re.VERBOSE)
            for lang in languages])


class DeanImdbApi (ImdbApi):
    def __init__(self):
        ImdbApi.__init__(self)
        
        self.__details_by_title = {}
        self.__last_limit = datetime.datetime.min
        self.__last_request = None
        self.__nr_requests = 0
    
    
    def get_languages(self, title):
        details = self.__cached_throttled_query(title)
        languages = details['languages']
        
        if re.search(r'^ \s* N/A \s* $', languages, re.IGNORECASE + re.VERBOSE):
            languages = self._get_languages_from_title_page(title,
                automate.util.io.Url(details['imdburl']))
        else:
            languages = re.split(r'(?: \s* &nbsp;)? \s* , \s*', languages,
                flags = re.IGNORECASE + re.VERBOSE)
            
            # Remove language usage details, e.g. "Japanese(afewwords)".
            languages = set([
                re.sub(r'\s* \( \w+ \) \s* $', '', lang, flags = re.VERBOSE)
                for lang in languages])
        
        if len(languages) == 0:
            raise self.LanguageListUnavailable(self, title)
        
        return languages
    
    
    def get_genres(self, title):
        details = self.__cached_throttled_query(title)
        genres = details['genres']
        
        if re.search(r'^ \s* N/A \s* $', genres, re.IGNORECASE + re.VERBOSE):
            url = automate.util.io.Url(details['imdburl'])
            
            try:
                genres = set(url.read(parse = True).xpath(
                    '//a[starts-with(@href, "/genre/")]/text()'))
            except automate.util.io.NETWORK_ERROR as error:
                raise self.Unavailable(self, title, error)
        else:
            genres = set(re.split(r'\s* , \s*', genres,
                flags = re.IGNORECASE + re.VERBOSE))
        
        if len(genres) == 0:
            raise self.GenreListUnavailable(self, title)
        
        return genres
    
    
    def get_year(self, title):
        return int(self.__cached_throttled_query(title)['year'])
    
    
    @property
    def name(self):
        return "Dean's IMDb API"
    
    
    def __cached_throttled_query(self, title):
        details = self.__details_by_title.get(title)
        
        if details is not None:
            return details
        
        details = self.__details_by_title[title] = self.__throttled_query(title)
        return details
    
    
    def __query(self, title):
        url = automate.util.io.Url('http://www.deanclatworthy.com/imdb/',
            query = {'q': title})
        
        self.logger.debug('Query: %s: %s', title, url)
        
        try:
            details = url.read(parse = 'json')
        except ValueError as error:
            raise self.Unavailable(self, title, error)
        
        if 'error' in details:
            raise self.Unavailable(self, title, details['error'])
        
        result_title = details['title']
        
        # Sometimes the given information doesn't match the movie searched for.
        title_similarity = difflib.SequenceMatcher(
            a = title, b = result_title).ratio()
        
        is_match = \
            (title_similarity >= self._config.similarity.title.ratio) \
            or (self._config.similarity.title.prefix \
                and result_title.startswith(title))
        
        if not is_match:
            raise self.SearchResultMismatch(self, title, result_title,
                title_similarity)
        
        return details
    
    
    def __throttled_query(self, title):
        self.__nr_requests += 1
        self.__last_request = datetime.datetime.now()
        req_rate = self._config.request_rate
        
        elapsed_time = (self.__last_request - self.__last_limit) \
            / req_rate.interval
        
        if (self.__nr_requests / elapsed_time) >= req_rate.count:
            # Too many recent API requests.
            raise self.Unavailable(self, title, req_rate.error)
        
        try:
            return self.__query(title)
        except self.Unavailable as error:
            if error.error == req_rate.error:
                # Throttle down API requests.
                self.__last_limit = datetime.datetime.now()
            
            raise


class TheImdbApi (ImdbApi):
    def __init__(self):
        ImdbApi.__init__(self)
        self.__details_by_title = {}
    
    
    def get_languages(self, title):
        title_url = automate.util.io.Url(
            'http://www.imdb.com/title/' + self.__get_imdb_id(title))
        
        languages = self._get_languages_from_title_page(title, title_url)
        
        if len(languages) == 0:
            raise self.LanguageListUnavailable(self, title)
        
        return languages
    
    
    def get_genres(self, title):
        # Don't use response's genre list as it might not be up-to-date.
        url = automate.util.io.Url('http://www.imdb.com/title/'
            + self.__get_imdb_id(title))
        
        try:
            genres = set(url.read(parse = True).xpath(
                '//a[starts-with(@href, "/genre/")]/text()'))
        except automate.util.io.NETWORK_ERROR as error:
            raise self.Unavailable(self, title, error)
        
        if len(genres) == 0:
            raise self.GenreListUnavailable(self, title)
        
        return genres
    
    
    def get_year(self, title):
        return int(self.__cached_query(title)['Year'])
    
    
    @property
    def name(self):
        return 'The IMDb API'
    
    
    def __cached_query(self, title):
        details = self.__details_by_title.get(title)
        
        if details is not None:
            return details
        
        details = self.__details_by_title[title] = self.__query(title)
        return details
    
    
    def __get_imdb_id(self, title):
        return self.__cached_query(title).get('ID') \
            or self.__cached_query(title).get('imdbID')
    
    
    def __query(self, title):
        current_year = datetime.date.today().year
        
        url = automate.util.io.Url('http://www.imdbapi.com/',
            query = {'t': title, 'y': current_year})
        
        self.logger.debug('Query: %s: %s', title, url)
        
        try:
            details = url.read(parse = 'json')
        except automate.util.io.NETWORK_ERROR as error:
            raise self.Unavailable(self, title, error)
        
        result = details['Response']
        
        if result != 'True':
            raise self.Unavailable(self, title, result)
        
        result_title = details['Title']
        
        # Sometimes the given information doesn't match the movie searched for.
        title_similarity = difflib.SequenceMatcher(
            a = title, b = result_title).ratio()
        
        is_match = \
            (title_similarity >= self._config.similarity.title.ratio) \
            or (self._config.similarity.title.prefix \
                and result_title.startswith(title))
        
        if not is_match:
            raise self.SearchResultMismatch(self, title, result_title,
                title_similarity)
        
        year_delta = abs(current_year - int(details['Year']))
        
        if year_delta > self._config.similarity.year:
            raise self.Unavailable(self, title,
                'Not found: Got movie from %s instead' % details['Year'])
        
        return details


class ImdbApiAggregator (ImdbApi):
    def __init__(self):
        ImdbApi.__init__(self)
        automate.util.io.Logger.__init__(self, 'IMDb API')
        
        # Prefer The IDMb API as it doesn't impose any usage limits, and also
        # because it seems to find correct movies better (e.g. in case of
        # multiple ones with the same name).
        
        self.__api_dean = DeanImdbApi()
        self.__api_the = TheImdbApi()
        
        self.__genres_by_title = {}
        self.__languages_by_title = {}
        self.__year_by_title = {}
    
    
    def get_languages(self, title):
        languages = self.__languages_by_title.get(title)
        
        if languages is not None:
            return languages
        
        try:
            languages = self.__api_the.get_languages(title)
        except self.Unavailable as error:
            self.logger.debug(error)
            languages = self.__api_dean.get_languages(title)
        
        self.__languages_by_title[title] = languages
        return languages
    
    
    def get_genres(self, title):
        genres = self.__genres_by_title.get(title)
        
        if genres is not None:
            return genres
        
        try:
            genres = self.__api_the.get_genres(title)
        except self.Unavailable as error:
            self.logger.debug(error)
            genres = self.__api_dean.get_genres(title)
        
        self.__genres_by_title[title] = genres
        return genres
    
    
    def get_year(self, title):
        year = self.__year_by_title.get(title)
        
        if year is not None:
            return year
        
        try:
            year = self.__api_the.get_year(title)
        except self.Unavailable as error:
            self.logger.debug(error)
            year = self.__api_dean.get_year(title)
        
        self.__year_by_title[title] = year
        return year
    
    
    @property
    def name(self):
        raise NotImplementedError
