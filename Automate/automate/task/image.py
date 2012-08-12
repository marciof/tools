# -*- coding: UTF-8 -*-


# Standard:
import re

# External:
import feedparser, fixes, PIL.Image

# Internal:
import automate.config, automate.download, automate.task, automate.util.sys, \
    automate.util.io


class InterfaceLift (automate.task.Download):
    class __WallpaperUrl (automate.download.Url):
        @property
        def __id(self):
            return self.path.components[-1]
        
        
        def __hash__(self):
            return hash(self.__id)
        
        
        def __lt__(self, url):
            if isinstance(url, type(self)):
                return self.__id < url.__id
            else:
                return automate.download.Url.__lt__(self, url)
    
    
    __WallpaperUrl.register_host_name('interfacelift.com')
    __SCREEN_RES = automate.util.sys.SystemScreenResolution()
    
    
    def __init__(self):
        automate.task.Download.__init__(self)
        self.__skipped_urls = set()
    
    
    @property
    def name(self):
        return 'InterfaceLIFT'
    
    
    @property
    def url(self):
        return automate.util.io.Url('http://interfacelift.com')
    
    
    def _list_urls(self):
        for item in feedparser.parse(self.__config.feed_url).entries:
            view_url = automate.util.io.Url(item.link)
            
            if view_url not in self.__skipped_urls:
                img_url = self.__get_best_wallpaper_url(view_url)
                
                if img_url is None:
                    self.__skipped_urls.add(view_url)
                else:
                    yield img_url
    
    
    @property
    def __config(self):
        return automate.config.USER.download.source.interface_lift
    
    
    def __get_best_wallpaper_url(self, view_url):
        view_html = view_url.read(parse = True)
        [title] = view_html.xpath('//*[@class = "details"]//h1//text()')
        all_resolutions = self.__get_wallpaper_resolutions(view_html)
        
        matching_resolutions = list(filter(
            lambda r: r.ratio == self.__SCREEN_RES.ratio,
            sorted(all_resolutions, reverse = True)))
        
        if len(matching_resolutions) == 0:
            self.logger.warning('No resolutions found at %s: %s: %s',
                self.__SCREEN_RES, title, view_url)
            return None
        
        y = self.__get_wallpaper_luminance(view_html, view_url, all_resolutions)
        
        if y < self.__config.skip_darks_below_y:
            self.logger.warning('Skip dark wallpaper (%d Y): %s, %s',
                y, title, view_url)
            return None
        
        img_url = self.__get_wallpaper_url(view_html, matching_resolutions[0])
        img_url.comment = view_url
        img_url.title = title
        
        return img_url
    
    
    def __get_wallpaper_luminance(self, view_html, view_url, all_resolutions):
        smallest_res = sorted(all_resolutions, key = lambda r: r.size)[0]
        
        self.logger.debug('Get smallest wallpaper to resize to 1x1: %s: %s',
            smallest_res, view_url)
        
        smallest_img = self.__get_wallpaper_url(view_html, smallest_res).read(
            max_retries = self.__config.retries_on_error,
            parse = True,
            binary = True)
        
        self.logger.debug('Resize wallpaper to 1x1 (Y check): %s', smallest_img)
        (r, g, b) = smallest_img.resize((1, 1), PIL.Image.BICUBIC) \
            .getpixel((0, 0))
        
        return 0.299 * r + 0.587 * g + 0.114 * b
    
    
    def __get_wallpaper_resolutions(self, view_html):
        return list(map(
            automate.util.sys.ScreenResolution.from_str,
            view_html.xpath(
                '//select[@name = "resolution"]/optgroup/option/@value')))
    
    
    def __get_wallpaper_url(self, view_html, target_res):
        [url] = view_html.xpath('//*[@class = "preview"]//img[@border]/@src')
        
        url = re.sub(r'(?= \. \w+ $)', '_%s' % target_res, url,
            flags = re.VERBOSE)
        
        url = re.sub(r'(?<= /) previews (?= /)', self.__session_code, url,
            flags = re.VERBOSE)
        
        return self.__WallpaperUrl(url)
    
    
    @property
    def __session_code(self):
        return re.findall('"/wallpaper/ ([^/]+) /"',
            automate.util.io.Url(self.__config.script_url).read(),
            re.VERBOSE)[0]
