# standard
from abc import ABCMeta, abstractmethod

# internal
from .error import Error

class InvalidAuthUrlError (Error):
    def __init__(self, url):
        super().__init__('Invalid authentication URL:', url)

class MissingAuthCodeUrlError (Error):
    def __init__(self, url):
        super().__init__('No authentication code found in URL:', url)

class MultipleAuthCodesUrlError (Error):
    def __init__(self, url):
        super().__init__('Multiple authentication codes found in URL:', url)

class UnauthenticatedError (Error):
    def __init__(self):
        super().__init__('No authenticated session (did you login?)')

class AuthenticationError (Error):
    def __init__(self):
        super().__init__('Authentication failed')

class Client (metaclass = ABCMeta):

    @abstractmethod
    def authenticate_session(self):
        pass

    @abstractmethod
    def authenticate_url(self, url):
        pass

    @abstractmethod
    def list_changes(self, delta_token):
        pass

    @abstractmethod
    def login(self):
        pass
