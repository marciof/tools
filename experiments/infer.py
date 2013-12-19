#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import __builtin__
import collections
import csv
import exceptions
import functools
import inspect
import os
import sys
import types
import urllib

# External:
import funcsigs
import ordereddict


_fq_name_module_override = {
    types.ClassType: types,
    types.FunctionType: types,
    types.NoneType: types,
}


_fq_name_override = {
    types.ClassType: 'ClassType',
    types.FunctionType: 'FunctionType',
}


class OrderedDefaultDict (ordereddict.OrderedDict, collections.defaultdict):
    def __init__(self, *args, **kwargs):
        ordereddict.OrderedDict.__init__(self)
        collections.defaultdict.__init__(self, *args, **kwargs)


# TODO: Inner classes? Types defined within functions?
# TODO: Type of old-style classes?
def calc_fq_name(value):
    module = _fq_name_module_override.get(value) or inspect.getmodule(value)
    parts = []

    if module in (__builtin__, exceptions):
        module = None
    else:
        module = module.__name__

    if inspect.ismethod(value):
        parts.append(value.im_class.__name__)

    parts.append(_fq_name_override.get(value, value.__name__))
    return (module, '.'.join(parts))


def calc_signature_id(function):
    arg_spec = inspect.getargspec(function)

    return hash((
        tuple([tuple(p) if isinstance(p, list) else p for p in arg_spec.args]),
        arg_spec.defaults))


def deduce_param_signature(sig, args_list, kwargs_list):
    types_by_param = OrderedDefaultDict(set)

    for args, kwargs in zip(args_list, kwargs_list):
        params = sig.bind(*args, **kwargs).arguments

        for name, param_type in params.items():
            types_by_param[name].add(param_type)

        for name, param in sig.parameters.items():
            if name not in params:
                types_by_param[name].add(type(param.default))

    sig_by_param = ordereddict.OrderedDict()

    for name, type_set in types_by_param.items():
        if len(type_set) > 1:
            t = find_common_type(type_set)
            sig_by_param[name] = type_set if t is None else set([t])
        else:
            sig_by_param[name] = type_set

    return sig_by_param


def deduce_return_signature(return_set):
    if len(return_set) == 1:
        return return_set
    elif len(return_set) > 1:
        common_return_type = find_common_type(return_set)

        if common_return_type is None:
            return return_set
        else:
            return set([common_return_type])
    else:
        return None


def deduce_signature(function, args_list, kwargs_list, return_set, exc_set):
    function = getattr(function, '__wrapped__', function)
    sig = funcsigs.signature(function)
    param_sig = deduce_param_signature(sig, args_list, kwargs_list)
    return_sig = deduce_return_signature(return_set)

    return (param_sig, return_sig, exc_set)


def find_common_type(type_set):
    type_set = list(type_set)
    hierarchies = [set(inspect.getmro(t)) for t in type_set[1:]]

    for t in inspect.getmro(type_set[0]):
        is_common = True

        for hierarchy in hierarchies:
            if t not in hierarchy:
                is_common = False
                break

        if is_common:
            return None if t is object else t


# TODO: Check exception tracebacks for additional call sites.
def log_signature_to(log):
    if os.getenv('INFER_SIGNATURE_DISABLED') is not None:
        return lambda function: function

    def decorator(function):
        function_name = calc_fq_name(function)
        signature_id = calc_signature_id(function)

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            args_type_names = [calc_fq_name(type(v)) for v in args]

            kwargs_type_names = dict((n, calc_fq_name(type(v)))
                for n, v in kwargs.items())

            return_value = None
            exc_type = None
            traceback = None

            try:
                return_value = function(*args, **kwargs)
                return return_value
            except Exception:
                (exc_type, _, traceback) = sys.exc_info()
                raise
            finally:
                return_type_name = None
                exc_type_name = None

                if traceback is not None:
                    raise_site = inspect.getinnerframes(traceback)[-1][0]

                    # Only exceptions directly thrown by the function.
                    if raise_site.f_code is function.func_code:
                        exc_type_name = calc_fq_name(exc_type)

                    # Break circular references. See:
                    # - http://docs.python.org/library/inspect.html#the-interpreter-stack
                    # - http://docs.python.org/library/sys.html#sys.exc_info
                    del raise_site, traceback
                elif return_value is not None:
                    return_type_name = calc_fq_name(type(return_value))

                log(signature_id,
                    function_name,
                    args_type_names,
                    kwargs_type_names,
                    return_type_name,
                    exc_type_name)

        wrapper.__wrapped__ = function
        return wrapper

    return decorator


# TODO: Play nice with logrotate.
class CsvLogger (object):
    def __init__(self, path):
        self.file = open(path, 'a', 0)
        self.writer = csv.writer(self.file, strict = True)


    def __call__(self, sig_id, function, args, kwargs, return_, exception):
        def type_to_str(fq_name):
            (module, name) = fq_name
            return name if module is None else '%s@%s' % (name, module)

        self.writer.writerow([
            '%X' % sig_id,
            type_to_str(function),
            '&'.join(map(type_to_str, args)),
            urllib.urlencode([(n, type_to_str(t)) for n, t in kwargs.items()]),
            type_to_str(return_) if return_ is not None else '',
            type_to_str(exception) if exception is not None else '',
        ])


    def __del__(self):
        self.file.close()


class ReadableLogger (object):
    def __init__(self, stream):
        self.stream = stream


    def __call__(self, sig_id, function, args, kwargs, return_, exception):
        def type_to_str(fq_name):
            (module, name) = fq_name
            return name if module is None else '%s.%s' % (module, name)

        kwargs_sig = ', '.join(
            ['%s : %s' % (n, type_to_str(t)) for n, t in kwargs.items()])

        sig = '%s(%s%s)' % (
            type_to_str(function),
            ', '.join(map(type_to_str, args)),
            ((', ' if args else '') + kwargs_sig) if kwargs_sig else '')

        if return_ is not None:
            sig += ' : ' + type_to_str(return_)

        if exception is not None:
            sig += ' -> ' + type_to_str(exception)

        print >> self.stream, '<%X>' % sig_id, sig


def log_signature(function):
    return log_signature_to(CsvLogger(sys.argv[0] + '.sig'))(function)


print_signature = log_signature_to(ReadableLogger(sys.stderr))


if __name__ == '__main__':
    @print_signature
    def f(x, y = 0.0):
        return g()
        # raise RuntimeError('called f()')

    def g():
        return 123
        #raise RuntimeError('called g()')

    f(x = 'a')
    f(b'', True)
