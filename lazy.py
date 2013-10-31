# -*- coding: UTF-8 -*-


"""
Goals:

* Regular `import` syntax.
* Negligible performance overhead.
* Best-effort fail-fast `ImportError`.
* Inheritance from `types.ModuleType`.
* Clear usage through `with`.

Issues:

* Only top-level modules and packages are supported.
"""


# Standard:
from __future__ import absolute_import, division, unicode_literals
import imp
import inspect
import sys
import types


module_info_attr = '__module_info__'
mget = types.ModuleType.__getattribute__
mset = types.ModuleType.__setattr__
mdel = types.ModuleType.__delattr__


def find_top_level_module(name, path = None):
    if '.' in name:
        (top_level, rest) = name.rsplit('.', 1)
    else:
        (top_level, rest) = (name, None)

    return (imp.find_module(top_level, path), top_level, rest)


# TODO: Remove recursion for performance?
def fully_load_module((info, top_level, rest)):
    print 'import', top_level, rest

    try:
        module = imp.load_module(top_level, *info)
    finally:
        if info[0] is not None:
            info[0].close()

    if rest is None:
        return module
    else:
        return fully_load_module(find_top_level_module(rest, module.__path__))


# TODO: Ensure all attributes are set <https://pypi.python.org/pypi/demandimport/>.
# TODO: Override `__delattr__`.
# TODO: Override `__setattr__`.
class Module (types.ModuleType):
    def __init__(self, name):
        types.ModuleType.__init__(self, name)
        mset(self, module_info_attr, find_top_level_module(name))


    # TODO: Faster to copy `__dict__` or to proxy the real module?
    def __getattr__(self, name):
        print '__getattr__', name

        try:
            module_info = mget(self, module_info_attr)
        except AttributeError:
            pass
        else:
            mdel(self, module_info_attr)
            module = fully_load_module(module_info)
            mget(self, '__dict__').update(vars(module))

        return mget(self, name)


# TODO: Thread safe?
# TODO: Follow protocol <http://www.python.org/dev/peps/pep-0302/>.
# TODO: Compare performance <http://www.rfk.id.au/blog/entry/frozen-app-starting-faster/>.
class Importer (object):
    def __init__(self):
        self.frames = []


    def __enter__(self):
        print '>' * 10
        self.frames.append(id(inspect.currentframe().f_back))


    def __exit__(self, exc_type, exc_val, exc_tb):
        print '<' * 10
        self.frames.pop()


    def find_module(self, fullname, path):
        is_top_level = ((path is None)
            and (len(self.frames) > 0)
            and (self.frames[-1] == id(inspect.currentframe().f_back)))

        # Skip sub-modules/packages and nested imports.
        if is_top_level:
            print 'find_module', fullname, path
            return self


    def load_module(self, fullname):
        print 'load_module', fullname

        try:
            return sys.modules[fullname]
        except KeyError:
            sys.modules[fullname] = module = Module(fullname)
            return module


imports = Importer()
sys.meta_path.append(imports)

with imports:
    import flask
    import feedparser

print flask.Flask
print feedparser.parse
