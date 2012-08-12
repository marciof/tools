# -*- coding: UTF-8 -*-


# Standard:
import email, http.client, io, json, logging, os, os.path, re, socket, \
    threading, urllib.error, urllib.parse, urllib.request

# External:
import lxml.html, chardet, colorconsole.terminal, fixes, PIL.Image, unipath

# Internal:
import automate.config


NETWORK_ERROR = (http.client.HTTPException, socket.error, urllib.error.URLError)


if os.name == 'nt':
    import colorconsole.win, ctypes
    stdin_handle = colorconsole.win.Terminal().stdin_handle
    
    def in_console_mode():
        return ctypes.windll.kernel32.GetConsoleMode(stdin_handle)
else:
    import sys
    
    def in_console_mode():
        return sys.stdin.isatty()


def _parse_json(data):
    try:
        return json.loads(data)
    except ValueError as error:
        raise http.client.UnknownTransferEncoding(error)


class ColoredLogStreamHandler (logging.StreamHandler):
    __TERMINAL = colorconsole.terminal.get_terminal()
    __TERMINAL_GUARD = threading.Lock()
    
    
    def __init__(self):
        logging.StreamHandler.__init__(self)
        format = automate.config.USER.logging.format
        
        self.setFormatter(logging.Formatter(
            fmt = format.message,
            datefmt = format.date))
    
    
    def emit(self, record):
        with self.__TERMINAL_GUARD:
            try:
                color_name = automate.config.USER.logging.color.get(
                    logging._levelNames[record.levelno].lower())
                
                if color_name is not None:
                    self.__TERMINAL.set_color(
                        colorconsole.terminal.colors[color_name.upper()])
                
                logging.StreamHandler.emit(self, record)
            finally:
                if os.name == 'nt':
                    # Allow terminal reset to actually reset the color.
                    print(end = '')
                
                self.__TERMINAL.reset()


class Logger:
    __HANDLER = ColoredLogStreamHandler()
    
    
    def __init__(self, name = None):
        self.logger = logging.getLogger(name or type(self).__name__)
        self.logger.addHandler(self.__HANDLER)
        
        self.logger.setLevel(logging._levelNames[
            automate.config.USER.logging.level.upper()])


class Path (unipath.Path):
    if os.name == 'posix':
        @classmethod
        def clean_file_name(class_, file_name):
            return file_name.replace('/', '-')
    elif os.name == 'nt':
        @classmethod
        def clean_file_name(class_, file_name):
            return \
                re.sub(r'\s*:\s*', ' - ',
                re.sub(r'\S:\S', '.',
                re.sub(r'\s*[/|\\]\s*', ' - ', file_name
                    .translate(str.maketrans('*?<>', '#¿()'))
                    .replace('"', "''"))))
    else:
        @classmethod
        def clean_file_name(class_, file_name):
            return file_name
    
    
    @classmethod
    def for_documents(class_):
        path = automate.config.USER.system.path.documents
        
        if path is None:
            from win32com.shell import shellcon
            path = class_.__get_windows_path(shellcon.CSIDL_PERSONAL)
        
        return class_(path)
    
    
    @classmethod
    def for_null(class_):
        return class_(os.path.devnull)
    
    
    @classmethod
    def for_settings(class_):
        path = automate.config.USER.system.path.settings
        
        if path is None:
            from win32com.shell import shellcon
            path = class_.__get_windows_path(shellcon.CSIDL_APPDATA)
        
        return class_(path)
    
    
    @classmethod
    def __get_windows_path(class_, folder_id):
        from win32com.shell import shell
        return class_(shell.SHGetFolderPath(0, folder_id, 0, 0))
    
    
    @property
    def components(self):
        return unipath.Path.components(self)
    
    
    def split_ext(self):
        return os.path.splitext(self)


class Url (Logger):
    __PARSERS_BY_TYPE = {
        'html': lxml.html.fromstring,
        'jpeg': lambda data: PIL.Image.open(io.BytesIO(data)),
        'json': _parse_json,
    }
    
    
    @classmethod
    def convert_query_to_string(class_, query):
        encoded_query = []
        
        for key, values in query.items():
            for value in (values if isinstance(values, list) else [values]):
                if not isinstance(value, str) and not isinstance(value, bytes):
                    value = str(value)
                
                encoded_query.append('%s=%s' % (
                    urllib.parse.quote(key, safe = b'[]'),
                    urllib.parse.quote(value, safe = b'[]')))
        
        return '&'.join(encoded_query)
    
    
    def __init__(self, url, query = None):
        Logger.__init__(self, 'Network')
        
        if isinstance(url, Url):
            self.__components = url.__components
        else:
            self.__components = urllib.parse.urlparse(url)
        
        if query is not None:
            self.query = query
    
    
    @property
    def host_name(self):
        return self.__components.hostname
    
    
    @host_name.setter
    def host_name(self, host_name):
        components = self.__components._asdict()
        components['netloc'] = host_name
        
        self.__components = urllib.parse.ParseResult(**components)
    
    
    def open(self):
        request = urllib.request.Request(str(self))
        headers = automate.config.USER.network.headers.get(self.host_name)
        
        for key, value in (headers or {}).items():
            request.add_header(key, value)
        
        return urllib.request.build_opener().open(request)
    
    
    @property
    def path(self):
        return Path(self.__components.path)
    
    
    @path.setter
    def path(self, path):
        if isinstance(path, list):
            path = re.sub(r'^/+', '/', '/'.join(path))
        
        components = self.__components._asdict()
        components['path'] = path
        
        self.__components = urllib.parse.ParseResult(**components)
    
    
    @property
    def query(self):
        return urllib.parse.parse_qs(self.__components.query)
    
    
    @query.setter
    def query(self, query):
        components = self.__components._asdict()
        components['query'] = self.convert_query_to_string(query)
        
        self.__components = urllib.parse.ParseResult(**components)
    
    
    def read(self, max_retries = 0, parse = False, binary = False):
        (headers, charset, content) = self.__download_content(max_retries)
        parser = headers.get_content_subtype() if parse is True else parse
        
        decoded_content = None
        parsed_content = None
        
        if (parser == 'html') and (charset is not None):
            decoded_content = content.decode(charset)
            parsed_content = self.__PARSERS_BY_TYPE[parser](decoded_content)
            self.__detect_soft_http_errors(headers, parsed_content)
        
        if binary:
            parsed_content = None
        else:
            content = decoded_content or content.decode(charset)
        
        if not parse:
            return content
        
        if parsed_content is not None:
            return parsed_content
        else:
            return self.__PARSERS_BY_TYPE[parser](content)
    
    
    def resolve(self):
        connection = self.open()
        url = type(self)(connection.geturl())
        
        connection.close()
        return url
    
    
    @property
    def scheme(self):
        return self.__components.scheme
    
    
    @scheme.setter
    def scheme(self, scheme):
        components = self.__components._asdict()
        components['scheme'] = scheme
        
        self.__components = urllib.parse.ParseResult(**components)
    
    
    def __detect_soft_http_errors(self, headers, html):
        [title] = html.xpath('/html/head/title/text()')
        error = re.findall(r'^ (\d+) \s (.+) $', title, re.X)
        
        if len(error) == 0:
            return
        
        [(code, description)] = error
        code = int(code)
        
        if http.client.responses.get(code, '') != description:
            return
        
        raise urllib.error.HTTPError(
            url = str(self),
            code = code,
            msg = description,
            hdrs = headers,
            fp = None)
    
    
    def __download_content(self, max_retries):
        response = self.open()
        nr_retries = 0
        
        while True:
            try:
                content = response.read()
                break
            except NETWORK_ERROR as error:
                if nr_retries >= max_retries:
                    raise
                
                nr_retries += 1
                
                self.logger.warning('Retrying request #%d <%s>: %s',
                    nr_retries, self, error)
        
        headers = email.message_from_string(str(response.headers))
        
        charset = headers.get_content_charset() \
            or chardet.detect(content)['encoding']
        
        return (headers, charset, content)
    
    
    def __eq__(self, that):
        return hash(self) == hash(that)
    
    
    def __hash__(self):
        return hash(str(self))
    
    
    def __lt__(self, that):
        return str(self) < str(that)
    
    
    def __str__(self):
        return urllib.parse.urlunparse(self.__components)
