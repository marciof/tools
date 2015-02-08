#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Standard:
import fcntl
import getopt
import os
import struct
import sys
import termios

# Internal:
import viewer.compat


#noinspection PyClassicStyleClass
class Options:
    @classmethod
    def from_cmdl_args(cls, cmd_args, **kwargs):
        """
        :type cmd_args: list
        """
        
        options = cls(**kwargs)
        
        # No long options for performance.
        (params, args) = getopt.getopt(cmd_args, 'ho:')
        
        for param, value in params:
            if param == '-h':
                if options.output:
                    options.output.write('Viewer.\n')
                return
            
            elif param == '-o':
                options.output = open(value, 'wb')
        
        options.args.extend(args)
        return options
    
    
    def __init__(self, output = None):
        """
        :type output: file
        """
        
        self.args = []
        self.output = output


def _tty_get_window_size(tty_fd):
    return struct.unpack('HHHH',
        fcntl.ioctl(tty_fd, termios.TIOCGWINSZ,
            struct.pack('HHHH', 0, 0, 0, 0)))


def _tty_set_window_size(tty_fd, rows, columns, x_pixel = 0, y_pixel = 0):
    fcntl.ioctl(tty_fd, termios.TIOCSWINSZ,
        struct.pack('HHHH', rows, columns, x_pixel, y_pixel))


# `subprocess` isn't used because it takes too long to load/execute and doesn't
# allow TTY-like behavior to be faked.
def _exec_process(program, args, env = None):
    window_size = _tty_get_window_size(sys.stdout)
    (pid, io_fd) = os.forkpty()
    
    if pid == 0:
        _tty_set_window_size(sys.stdout, *window_size)
        
        if env is not None:
            os.environ.update(env)
        
        os.execvp(program, [program] + args)
    
    with os.fdopen(io_fd, 'rb') as io_stream:
        output = viewer.compat.read_stream(io_stream)
    
    status = os.waitpid(pid, 0)[1]
    
    if status == 0:
        return output


def ls_viewer(options):
    output = _exec_process('ls', options.args)
    
    if output is not None:
        return lambda: options.output.write(output)


def git_show_viewer(options):
    output = _exec_process('git', ['show'] + options.args, {'GIT_PAGER': ''})
    
    if output is not None:
        return lambda: options.output.write(output)


def main():
    options = Options.from_cmdl_args(sys.argv[1:], output = sys.stdout)
    
    if not options:
        return
    
    for handler in [ls_viewer, git_show_viewer]:
        view = handler(options)
        
        if view:
            view()
            return


if __name__ == '__main__':
    main()
