# -*- coding: UTF-8 -*-


# Standard library:
import abc, bz2, tarfile

# External modules:
import fixes

# Internal modules:
import automate.util


class BackupFile (tarfile.TarFile):
    def __init__(self, name):
        tarfile.TarFile.__init__(self,
            fileobj = bz2.BZ2File(name + '.tar.bz2', mode = 'w'),
            mode = 'w')
        
        self._extfileobj = False
    
    
    def __enter__(self):
        return self
    
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    
    def add_files(self, folder, files):
        for file in files:
            self.add(folder.child(file), file)


class BackupTask (automate.util.PeriodicTask):
    __metaclass__ = abc.ABCMeta
    
    
    @abc.abstractproperty
    def files(self):
        raise NotImplementedError
    
    
    @abc.abstractproperty
    def path(self):
        raise NotImplementedError
    
    
    def process(self):
        with BackupFile(self.name) as backup_file:
            path = self.path
            self.logger.debug('Backup: %s', path)
            
            for file in self.files:
                backup_file.add(path.child(file), file)


class Winamp (BackupTask):
    @property
    def files(self):
        return [self.name + ext for ext in ('.bm', '.bm8', '.ini')]
    
    
    @property
    def name(self):
        return 'Winamp'
    
    
    @property
    def path(self):
        return automate.util.Path.settings().child(self.name)
