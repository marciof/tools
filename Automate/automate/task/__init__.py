# -*- coding: UTF-8 -*-


# Standard:
import abc, inspect, operator, queue, threading, traceback

# External:
import fixes

# Internal:
import automate.config, automate.download.manager, automate.util.io


class Task (metaclass = abc.ABCMeta):
    @property
    def interval(self):
        return None
    
    
    @abc.abstractproperty
    def name(self):
        raise NotImplementedError
    
    
    @property
    def priority(self):
        return 0
    
    
    @abc.abstractmethod
    def process(self):
        raise NotImplementedError
    
    
    @abc.abstractproperty
    def url(self):
        raise NotImplementedError
    
    
    def __eq__(self, task):
        return hash(self) == hash(task)
    
    
    def __hash__(self):
        return hash(self.name)
    
    
    def __lt__(self, task):
        return self.name < task.name


class Download (Task, automate.util.io.Logger):
    def __init__(self):
        Task.__init__(self)
        automate.util.io.Logger.__init__(self, self.name)
    
    
    @property
    def interval(self):
        return automate.config.USER.task.download.interval
    
    
    def process(self):
        manager = automate.download.manager.get_instance()
        self.logger.debug('Using download manager: %s', manager.name)
        
        try:
            for url in self._list_urls():
                if not manager.has_url(url):
                    self.logger.info('Download: %s', url.description)
                    manager.download_url(url)
        except automate.util.io.NETWORK_ERROR as error:
            self.logger.error(error)
            self.logger.debug('%s',
                '\n'.join(traceback.format_tb(error.__traceback__)))
    
    
    @abc.abstractmethod
    def _list_urls(self):
        raise NotImplementedError


class Manager (threading.Thread, automate.util.io.Logger):
    def __init__(self):
        threading.Thread.__init__(self, name = 'Task Manager')
        automate.util.io.Logger.__init__(self, self.name)
        
        self.daemon = True
        
        self.__task_queue = queue.PriorityQueue(maxsize = 0)
        self.__task_slot = threading.Semaphore(
            value = automate.config.USER.task.parallel)
    
    
    def queue(self, *tasks):
        for task in tasks:
            self.logger.debug('Queue task: %s', task.name)
            self.__task_queue.put((task.priority, task))
    
    
    def run(self):
        self.logger.info('Start')
        
        while True:
            self.__task_slot.acquire()
            (priority, task) = self.__task_queue.get()
            
            thread = threading.Thread(
                name = '%s (Task)' % task.name,
                target = self.__process_task,
                args = (task,))
            
            self.logger.info('Task start: %s', task.name)
            thread.daemon = True
            thread.start()
    
    
    def __process_task(self, task):
        self.logger.debug('Process task: %s', task.name)
        
        try:
            task.process()
        finally:
            self.__task_slot.release()
            self.logger.info('Task end: %s', task.name)
        
        interval = task.interval
        
        if interval:
            timer = threading.Timer(
                interval = interval.total_seconds(),
                function = self.queue,
                args = (task,))
            
            timer.name = '%s (Timer)' % task.name
            timer.daemon = True
            timer.start()


def list_classes():
    import automate.task.image, automate.task.video
    
    return map(operator.itemgetter(1),
        __list_concrete_classes(Task, automate.task.image)
        + __list_concrete_classes(Task, automate.task.video))


def __list_concrete_classes(base_class, module):
    def is_concrete_class(object):
        return inspect.isclass(object) \
            and not inspect.isabstract(object) \
            and issubclass(object, base_class)
    
    return inspect.getmembers(
        object = module,
        predicate = is_concrete_class)
