# standard
from abc import ABCMeta, abstractmethod
import os

# external
from overrides import overrides

class Event (metaclass = ABCMeta):

    @abstractmethod
    def apply(self, prefix):
        pass

class CreatedFileEvent (Event):

    def __init__(self, path, access_time, mod_time, write, logger):
        self.path = path
        self.access_time = access_time
        self.mod_time = mod_time
        self.write = write
        self.logger = logger.getChild(self.__class__.__name__)

    @overrides
    def apply(self, prefix):
        path = os.path.join(prefix, self.path)

        self.logger.debug('Create file at %s', path)
        self.write(path)

        self.logger.debug('Set file access and modified times to %s and %s',
            self.access_time, self.mod_time)
        os.utime(path,
            (self.access_time.timestamp(), self.mod_time.timestamp()))

class CreatedFolderEvent (Event):

    def __init__(self, path, access_time, mod_time, logger):
        self.path = path
        self.access_time = access_time
        self.mod_time = mod_time
        self.logger = logger.getChild(self.__class__.__name__)

    @overrides
    def apply(self, prefix):
        path = os.path.join(prefix, self.path)

        self.logger.debug('Create folder at %s', path)
        os.makedirs(path, exist_ok = True)

        self.logger.debug('Set folder access and modified times to %s and %s',
            self.access_time, self.mod_time)
        os.utime(path,
            (self.access_time.timestamp(), self.mod_time.timestamp()))

class DeletedFileEvent (Event):

    def __init__(self, path, logger):
        self.path = path
        self.logger = logger.getChild(self.__class__.__name__)

    @overrides
    def apply(self, prefix):
        path = os.path.join(prefix, self.path)
        self.logger.debug('Delete file at %s', path)
        os.remove(path)

class DeletedFolderEvent (Event):

    def __init__(self, path, logger):
        self.path = path
        self.logger = logger.getChild(self.__class__.__name__)

    @overrides
    def apply(self, prefix):
        path = os.path.join(prefix, self.path)
        self.logger.debug('Delete folder at %s', path)
        os.rmdir(path)
