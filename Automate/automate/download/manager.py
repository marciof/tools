# -*- coding: UTF-8 -*-


# Standard:
import abc, datetime, importlib, threading

# External:
import fixes

# Internal:
import automate.config, automate.download, automate.util, automate.util.io, \
    automate.util.sys


class Manager (metaclass = abc.ABCMeta):
    @abc.abstractmethod
    def download_url(self, url):
        raise NotImplementedError
    
    
    @abc.abstractmethod
    def has_url(self, url):
        raise NotImplementedError
    
    
    @abc.abstractproperty
    def name(self):
        raise NotImplementedError


class FreeDownloadManager (Manager):
    __DownloadText = automate.util.enum(
        *'FILE_NAME FILE_SIZE PROGRESS UNKNOWN_1 DOWNLOAD_PARTS UNKNOWN_2'
            .split())
    
    
    def __init__(self):
        Manager.__init__(self)
        
        self.__last_cache_reset = datetime.datetime.now()
        self.__type_lib = self.__initialize_type_lib()
        
        history_file = self.__config.history_file
        
        if history_file is True:
            history_file = automate.util.io.Path.for_settings().child('fdm.log')
        elif history_file is False:
            history_file = automate.util.io.Path.for_null()
        
        self.__url_history = automate.download.UrlHistory(
            history_file, self.__list_downloaded_urls)
    
    
    def download_url(self, url):
        wg_url_receiver = self.__type_lib.get_data_type('WGUrlReceiver')
        
        wg_url_receiver.Url = str(url)
        wg_url_receiver.DisableURLExistsCheck = False
        wg_url_receiver.ForceDownloadAutoStart = True
        wg_url_receiver.ForceSilent = True
        wg_url_receiver.ForceSilentEx = True
        
        if url.save_as is not None:
            wg_url_receiver.FileName = str(url.save_as)
        
        if url.comment is not None:
            wg_url_receiver.Comment = str(url.comment)
        
        wg_url_receiver.AddDownload()
        self.__url_history.add(url)
        self.__url_history.add(url.resolve())
    
    
    def has_url(self, url):
        if url in self.__url_history:
            return True
        
        resolved_url = url.resolve()
        
        if resolved_url in self.__url_history:
            return True
        
        elapsed_time = datetime.datetime.now() - self.__last_cache_reset
        
        if elapsed_time >= self.__config.cache_reset_interval:
            self.__last_cache_reset = datetime.datetime.now()
            self.__url_history.reset()
        
        return False
    
    
    @property
    def name(self):
        return 'Free Download Manager'
    
    
    @property
    def __config(self):
        return automate.config.USER.download.manager.fdm
    
    
    def __initialize_type_lib(self):
        import winreg
        
        config = self.__config
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, config.install_path.key)
        install_path = winreg.QueryValueEx(key, config.install_path.value)[0]
        
        return automate.util.sys.MsWindowsTypeLibrary(
            automate.util.io.Path(install_path).child(config.type_library))
    
    
    def __list_downloaded_urls(self, start_position = None):
        downloads_stat = self.__type_lib.get_data_type('FDMDownloadsStat')
        downloads_stat.BuildListOfDownloads(True, True)
        
        if start_position is None:
            start_position = downloads_stat.DownloadCount
        
        # Start at the newest URL to find newer downloads faster.
        for i in reversed(range(0, start_position)):
            download = downloads_stat.Download(i)
            
            url = automate.download.Url(download.Url,
                save_as = download.DownloadText(self.__DownloadText.FILE_NAME))
            
            yield (i, automate.download.Url.from_host_name(url))


__MANAGER_INSTANCE = None
__MANAGER_INSTANCE_GUARD = threading.Lock()


def get_instance():
    global __MANAGER_INSTANCE
    
    with __MANAGER_INSTANCE_GUARD:
        if __MANAGER_INSTANCE is None:
            manager_config = automate.config.USER.download.manager
            class_config = manager_config[manager_config.default]
            module_name, _, class_name = class_config['class'].rpartition('.')
            
            __MANAGER_INSTANCE = getattr(
                importlib.import_module(module_name), class_name)()
    
    return __MANAGER_INSTANCE
