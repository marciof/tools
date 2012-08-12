# -*- coding: UTF-8 -*-


# Standard:
import collections, mimetypes, os, threading

# External:
import fixes

# Internal:
import automate.config


class MsWindowsTypeLibrary:
    def __init__(self, path):
        import pythoncom, win32com.client
        global pythoncom, win32com
        
        self.__iid_by_type_name = {}
        self.__lib = pythoncom.LoadTypeLib(path)
        self.__path = path
    
    
    def get_data_type(self, type_name):
        pythoncom.CoInitialize()
        
        if type_name in self.__iid_by_type_name:
            return win32com.client.Dispatch(self.__iid_by_type_name[type_name])
        
        for i in range(0, self.__lib.GetTypeInfoCount()):
            (name, doc, help_ctxt, help_file) = self.__lib.GetDocumentation(i)
            
            if type_name == name:
                iid = self.__lib.GetTypeInfo(i).GetTypeAttr().iid
                self.__iid_by_type_name[type_name] = iid
                return win32com.client.Dispatch(iid)
        
        raise Exception('Type "%s" not found in type library "%s".'
            % (name, self.__path))


class ScreenResolution:
    @classmethod
    def from_str(class_, resolution):
        return class_(*map(int, resolution.split('x')))
    
    
    def __init__(self, width, height):
        self.__width = width
        self.__height = height
    
    
    @property
    def height(self):
        return self.__height
    
    
    @property
    def ratio(self):
        return self.width / self.height
    
    
    @property
    def size(self):
        return self.width * self.height
    
    
    @property
    def width(self):
        return self.__width
    
    
    def __eq__(self, that):
        return hash(self) == hash(that)
    
    
    def __hash__(self):
        return hash(str(self))
    
    
    def __lt__(self, that):
        if self.ratio == that.ratio:
            return self.size < that.size
        else:
            return self.ratio < that.ratio
    
    
    def __str__(self):
        return '%dx%d' % (self.width, self.height)


if os.name == 'nt':
    class SystemScreenResolution (ScreenResolution):
        import ctypes
        __USER32_DLL = ctypes.windll.user32
        
        
        def __init__(self, width = None, height = None):
            ScreenResolution.__init__(self, width, height)
        
        
        @property
        def height(self):
            return ScreenResolution.height.fget(self) \
                or self.__USER32_DLL.GetSystemMetrics(1)
        
        
        @property
        def width(self):
            return ScreenResolution.width.fget(self) \
                or self.__USER32_DLL.GetSystemMetrics(0)
else:
    class SystemScreenResolution (ScreenResolution):
        import tkinter
        
        __TK_INSTANCE = None
        __TK_INSTANCE_GUARD = threading.Lock()
        
        
        @classmethod
        def __get_tk_instance(class_):
            with class_.__TK_INSTANCE_GUARD:
                if class_.__TK_INSTANCE is None:
                    class_.__TK_INSTANCE = class_.tkinter.Tk()
            
            return class_.__TK_INSTANCE
        
        
        def __init__(self, width = None, height = None):
            ScreenResolution.__init__(self, width, height)
        
        
        @property
        def height(self):
            return ScreenResolution.height.fget(self) \
                or self.__get_tk_instance().winfo_screenheight()
        
        
        @property
        def width(self):
            return ScreenResolution.width.fget(self) \
                or self.__get_tk_instance().winfo_screenwidth()


if os.name == 'nt':
    import time
    
    def pause():
        time.sleep(-1)
else:
    import signal
    
    def pause():
        signal.pause()


for type, extension in automate.config.USER.system.mime_types.items():
    if mimetypes.guess_extension(type) is None:
        mimetypes.add_type(type, extension, strict = False)
