# -*- coding: UTF-8 -*-


# Standard:
import abc, threading

# External:
import fixes

# Internal:
import automate.config, automate.util.io


class Url (automate.util.io.Url):
    __class_by_host_name = {}
    __class_by_host_name_re = {}
    
    
    @classmethod
    def from_host_name(class_, url):
        url_class = class_.__class_by_host_name.get(url.host_name)
        
        if url_class is None:
            for host_name, url_class in class_.__class_by_host_name_re.items():
                if host_name.search(url.host_name):
                    return url_class(url)
            
            return url
        else:
            return url_class(url)
    
    
    @classmethod
    def register_host_name(class_, host_name):
        if isinstance(host_name, str):
            class_.__class_by_host_name[host_name] = class_
        else:
            class_.__class_by_host_name_re[host_name] = class_
    
    
    def __init__(self, url,
            comment = None,
            save_as = None,
            title = None,
            **kargs):
        
        automate.util.io.Url.__init__(self, url, **kargs)
        
        if isinstance(url, Url):
            self.comment = comment or url.comment
            self.save_as = save_as or url.save_as
            self.title = title or url.title
        else:
            self.comment = comment
            self.save_as = save_as
            self.title = title
        
        if self.scheme == '':
            default = automate.config.USER.download.url.default_scheme
            
            if default is not None:
                url = default + '://' + str(url)
                automate.util.io.Url.__init__(self, url, **kargs)
    
    
    @property
    def description(self):
        comment = str(self) if self.comment is None else str(self.comment)
        
        if self.title is None:
            return comment
        else:
            return '%s, %s' % (self.title, comment)
    
    
    def resolve(self):
        url = automate.util.io.Url.resolve(self)
        
        url.comment = self.comment
        url.title = self.title
        
        return self.from_host_name(url)


class UrlHistory (set):
    def __init__(self, path, generator):
        set.__init__(self)
        
        self.__generator = generator
        self.__iteration_lock = threading.Lock()
        self.__last_position = None
        
        self._file = open(path,
            mode = '+rt',
            buffering = 1,
            encoding = 'UTF-8')
        
        for line in self._file.readlines():
            set.add(self, Url.from_host_name(Url(line.rstrip('\n'))))
    
    
    def add(self, url):
        with self.__iteration_lock:
            self.__add_unlocked(url)
    
    
    def reset(self):
        self.__last_position = None
    
    
    def __add_unlocked(self, url):
        if not set.__contains__(self, url):
            set.add(self, url)
            self._file.writelines('%s\n' % url)
    
    
    def __contains__(self, search_url):
        with self.__iteration_lock:
            if set.__contains__(self, search_url):
                return True
            
            for position, url in self.__generator(self.__last_position):
                self.__add_unlocked(url)
                self.__last_position = position
                
                if search_url == url:
                    return True
            
            return False


class UrlSource:
    class UrlUnavailable (LookupError):
        pass
    
    
    @abc.abstractmethod
    def get_video_url(self, url):
        raise NotImplementedError
