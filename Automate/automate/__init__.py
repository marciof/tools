# -*- coding: UTF-8 -*-


# Standard:
import argparse, difflib, re, threading

# External:
import fixes

# Internal:
import automate.config, automate.download, automate.download.manager, \
    automate.task, automate.util.io, automate.util.sys


class Automate (argparse.ArgumentParser, automate.util.io.Logger):
    def __init__(self):
        argparse.ArgumentParser.__init__(self,
            description = 'Task automation.')
        automate.util.io.Logger.__init__(self)
        
        threading.current_thread().name = type(self).__name__
        self.__task_by_name = {}
        
        for task_class in automate.task.list_classes():
            task = task_class()
            
            if task.name in self.__task_by_name:
                self.logger.warning('Duplicate task: %s %s',
                    task.name, type(task))
            else:
                self.__task_by_name[task.name] = task
        
        self.__initialize_arguments()
    
    
    def execute(self):
        arguments = self.parse_args()
        automate.config.USER = arguments.config
        
        if automate.util.io.in_console_mode():
            arguments.func(arguments)
        else:
            import sys
            from PyQt4 import QtGui
            
            app = QtGui.QApplication(sys.argv)
            
            widget = QtGui.QWidget()
            widget.resize(250, 150)
            widget.move(300, 300)
            widget.setWindowTitle('Simple')
            widget.show()
            
            sys.exit(app.exec_())
    
    
    def __download_urls(self, arguments):
        download_manager = automate.download.manager.get_instance()
        
        for url in arguments.URL:
            download_manager.download_url(url)
    
    
    def __find_task(self, name):
        similarity_by_task_name = []
        
        for task_name in self.__task_by_name.keys():
            similarity = difflib.SequenceMatcher(
                a = task_name.lower(),
                b = name.lower())
            
            similarity_by_task_name.append((task_name, similarity.ratio()))
        
        similarity_by_task_name.sort(
            key = lambda task: task[1],
            reverse = True)
        
        ((closest_name, closest_score),
         (next_closest_name, next_closest_score)) \
            = similarity_by_task_name[0:2]
        
        config = automate.config.USER.task.detection
        
        found_task = (closest_score > config.similarity) and \
            ((closest_score - next_closest_score) > config.dissimilarity)
        
        if found_task:
            return self.__task_by_name[closest_name]
        else:
            return None
    
    
    def __initialize_arguments(self):
        arguments = [
            ('--config', {
                'action': 'store',
                'default': automate.config.USER,
                'help': 'path to the configuration file',
                'type': self.__validate_config_file,
            }),
        ]
        
        for name, options in arguments:
            self.add_argument(name, **options)
        
        commands = self.add_subparsers(parser_class = argparse.ArgumentParser)
        
        download_command = commands.add_parser('download',
            help = "download URL's using the default download manager")
        
        download_command.add_argument('URL',
            nargs = '+',
            help = 'resource URL',
            type = automate.download.Url)
        
        tasks = self.__task_by_name.values()
        longest_task_name = max(len(task.name) for task in tasks)
        tasks_list = []
        
        for task in tasks:
            tasks_list.append('  * %s%s'
                % (task.name.ljust(longest_task_name + 4), task.url))
        
        task_command = commands.add_parser('task',
            epilog = 'available tasks:\n' + '\n'.join(sorted(tasks_list)),
            formatter_class = argparse.RawDescriptionHelpFormatter,
            help = 'start tasks on-demand')
        
        task_command.add_argument('TASK',
            default = self.__task_by_name.values(),
            nargs = '*',
            help = 'literal task name or regular expression surrounded by /',
            type = self.__validate_task_name)
        
        download_command.set_defaults(func = self.__download_urls)
        task_command.set_defaults(func = self.__start_tasks)
    
    
    def __start_tasks(self, arguments):
        task_manager = automate.task.Manager()
        
        task_manager.queue(*set(arguments.TASK))
        task_manager.start()
        
        automate.util.sys.pause()
    
    
    def __validate_config_file(self, path):
        try:
            return automate.config.Configuration.load(path)
        except Exception as error:
            raise argparse.ArgumentTypeError(
                'Invalid configuration file "%s": %s' % (path, error))
    
    
    def __validate_task_name(self, name):
        try:
            return self.__task_by_name[name]
        except KeyError:
            regex = re.findall(r'^ / (.+) / $', name, re.VERBOSE)
            
            if len(regex) == 1:
                [regex] = regex
                
                for task_name in sorted(self.__task_by_name.keys()):
                    if re.search(regex, task_name):
                        self.logger.info('Matched task: %s' % task_name)
                        return self.__task_by_name[task_name]
            
            found_task = self.__find_task(name)
            
            if found_task:
                self.logger.info('Assuming task "%s": %s',
                    found_task.name, name)
                return found_task
            
            raise argparse.ArgumentTypeError('Unknown task: ' + name)
