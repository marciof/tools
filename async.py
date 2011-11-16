#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


# Standard:
import concurrent.futures, inspect

# External:
import fixes


class AsyncFuture:
    def __init__(self, future):
        self._future = future
    
    
    @property
    def result(self):
        return self._future.result()


class AsyncFunction:
    def __init__(self, executor, function):
        self._executor = executor
        self._function = function
    
    
    def async(self, *args, **kargs):
        return AsyncFuture(self._executor.submit(self._function, *args, **kargs))
    
    
    def __call__(self, *args, **kargs):
        return self._function(*args, **kargs)


class AsyncMethod (AsyncFunction):
    def __init__(self, executor, function, instance):
        AsyncFunction.__init__(self, executor, function)
        self._instance = instance
    
    
    def async(self, *args, **kargs):
        return AsyncFunction.async(self, self._instance, *args, **kargs)
    
    
    def __call__(self, *args, **kargs):
        return AsyncFunction.__call__(self, self._instance, *args, **kargs)


async_executor = concurrent.futures.ThreadPoolExecutor(max_workers = 4)


def async(function, executor = async_executor):
    params = inspect.getfullargspec(function)
    
    if (len(params.args) > 0) and (params.args[0] == 'self'):
        return property(lambda self: AsyncMethod(executor, function, self))
    else:
        return AsyncFunction(executor, function)


import time


class Test:
    @async
    def f(self):
        time.sleep(1)
        print('f')


@async
def g():
    time.sleep(1)
    print('g')


g()
Test().f.async()
print('main')
