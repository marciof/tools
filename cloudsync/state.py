# standard
from abc import ABCMeta, abstractmethod
import os
import pathlib
import stat

# external
import appdirs
from overrides import overrides

# internal
from .error import Error

class State (metaclass = ABCMeta):

    @abstractmethod
    def get(self, namespace):
        pass

    @abstractmethod
    def set(self, namespace, value, is_private = False):
        pass

    @abstractmethod
    def unset(self, namespace):
        pass

class PrefixedState (State):

    def __init__(self, prefix, state):
        self.prefix = prefix
        self.state = state

    @overrides
    def get(self, namespace):
        return self.state.get(self.prefix + namespace)

    @overrides
    def set(self, namespace, value, is_private = False):
        return self.state.set(self.prefix + namespace, value, is_private)

    @overrides
    def unset(self, namespace):
        return self.state.unset(self.prefix + namespace)

    def __str__(self):
        return '%s(%s)' % (':'.join(self.prefix), self.state)

class FileState (State):

    def __init__(self, app_name, logger):
        self.logger = logger.getChild(self.__class__.__name__)

        self.root_path = pathlib.Path(
            appdirs.user_cache_dir(appname = app_name))

    @overrides
    def get(self, namespace):
        path = self._build_path(namespace)
        self.logger.debug('Get state at %s', path)

        try:
            return path.read_text()
        except FileNotFoundError:
            return None

    @overrides
    def set(self, namespace, value, is_private = False):
        path = self._build_path(namespace)
        os.makedirs(str(path.parent), exist_ok = True)

        if is_private:
            self.logger.debug('Set private state at %s', path)
            path.touch(mode = stat.S_IRWXU ^ stat.S_IXUSR, exist_ok = True)
        else:
            self.logger.debug('Set state at %s with value %s', path, value)

        path.write_text(value)

    @overrides
    def unset(self, namespace):
        path = self._build_path(namespace)
        self.logger.debug('Unset state at %s', path)
        os.remove(str(path))

    def _build_path(self, namespace):
        if len(namespace) == 0:
            raise Error('Empty file state namespace')

        path = self.root_path

        for name in namespace:
            path = path.joinpath('TEMPLATE').with_name(name)

        return path

    def __str__(self):
        return str(self.root_path)
