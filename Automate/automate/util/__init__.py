# -*- coding: UTF-8 -*-


# Standard:
import copy, re

# External:
import fixes


class AttributeDict (dict):
    """
    @author: Steve Lacy
    @see: http://stackoverflow.com/q/5021467/753501
    """
    
    
    @classmethod
    def apply(class_, dictionary):
        dictionary = copy.copy(dictionary)
        
        for key, value in dictionary.items():
            if isinstance(value, dict):
                dictionary[key] = class_.apply(value)
        
        return class_(dictionary)
    
    
    def __getattr__(self, name):
        try:
            return dict.__getattribute__(self, name)
        except AttributeError as error:
            try:
                return dict.__getitem__(self, name)
            except KeyError:
                raise error
    
    
    def __setattr__(self, *args, **kargs):
        return dict.__setitem__(self, *args, **kargs)


def enum(*sequential, **named):
    """
    @author: Alec Thomas
    @see: http://stackoverflow.com/questions/36932/whats-the-best-way-to-implement-an-enum-in-python/1695250#1695250
    """
    
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


def merge_dicts(dst, src):
    """
    @author: Manuel Muradas
    @see: http://code.activestate.com/recipes/499335-recursively-update-a-dictionary-without-hitting-py/#c1
    """
    
    stack = [(dst, src)]
    
    while stack:
        current_dst, current_src = stack.pop()
        
        for key in current_src:
            if key in current_dst:
                are_dicts = isinstance(current_src[key], dict) \
                    and isinstance(current_dst[key], dict)
                
                if are_dicts:
                    stack.append((current_dst[key], current_src[key]))
                else:
                    current_dst[key] = current_src[key]
            else:
                current_dst[key] = current_src[key]
    
    return dst
