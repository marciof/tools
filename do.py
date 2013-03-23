#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Standard:
from __future__ import absolute_import, division, unicode_literals
import functools
import inspect


# FIXME: Reuse same wrapper/decorator for listeners and scopes.

# TODO: Refactor.
# TODO: Check if listener receives argument for optional listened result?
# TODO: Check function locals refer to the target? Disabled with __debug__.
# TODO: Log listener exceptions?

# TODO: Comment code.
# TODO: Examples (is_enabled = __debug__).
# TODO: Document (scoped is slower, exceptions aren't caught).
# TODO: Document: easily searchable with grep.
# TODO: Document: scoped application.
# TODO: Document: related code placed together.
# TODO: Document: easy to disable for performance.

# TODO: Profile quick startup for development.
# TODO: Profile ~0% run-time overhead for production.

# TODO: Test if debugging is affected (e.g. harder to understand).
# TODO: Test functions, methods, class methods, static methods.
# TODO: Test multiple listeners on same function.
# TODO: Test mix of listener and scope on same function.
# TODO: Test listener/scope on listener/scope function.
# TODO: Test correct listener execution order.
# TODO: Test disabled listeners.
# TODO: Test recursion.
# TODO: Test scope.
# TODO: Test *.py vs *.pyc scopes.
# TODO: Test exceptions in the listener and listened.


def after(
        listener,
        at = None,
        is_enabled = False,
        listeners_attr = '__do_after_listeners__',
        scopes_attr = '__do_after_scopes__'):
    
    if is_enabled:
        return lambda function: function
    
    if at is None:
        def decorator(function):
            listeners = getattr(function, listeners_attr, None)
            
            if listeners is not None:
                listeners.append(listener)
                return function
            
            @functools.wraps(function)
            def wrapper(*args, **kwargs):
                result = function(*args, **kwargs)
                
                for listener in getattr(wrapper, listeners_attr):
                    try:
                        listener(result)
                    except:
                        pass
                
                return result
            
            setattr(wrapper, listeners_attr, [listener])
            return wrapper
        
        return decorator
    else:
        target = at
        listeners = getattr(target, listeners_attr, None)
        
        def decorator(function):
            scopes = getattr(listener, scopes_attr, None)
            scope = (inspect.getfile(function), function.__name__)
            
            if scopes is None:
                setattr(listener, scopes_attr, set([scope]))
            else:
                scopes.add(scope)
            
            return function
        
        if listeners is not None:
            listeners.append(listener)
            return decorator
        
        @functools.wraps(target)
        def wrapper(*args, **kwargs):
            result = target(*args, **kwargs)
            caller = inspect.getframeinfo(inspect.currentframe().f_back)
            scope = (caller.filename, caller.function)
            
            for listener in getattr(wrapper, listeners_attr):
                if scope in getattr(listener, scopes_attr):
                    try:
                        listener(result)
                    except:
                        pass
            
            return result
        
        setattr(inspect.getmodule(target), target.__name__, wrapper)
        setattr(wrapper, listeners_attr, [listener])
        return decorator
