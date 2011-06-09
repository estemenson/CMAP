# -*- coding: utf-8 -*-
'''
Created on Jun 5, 2010

@author: stevenson
'''

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from agileConfig import Config
try:
    Log = Config().log.logger
except Exception:
    from petaapan.logger.console_logger import ConsoleLogger
    Log = ConsoleLogger('CMAP')
# File classtools.py (new) taken from Learning Python 4th edition
# Assorted class utilities and tools
class Dummy(object):
    def view(self): pass
    
class AttrDisplay:
    """
    Provides an inheritable print overload method that displays
    instances with their class names and a name=value pair for
    each attribute stored on the instance itself (but not attrs
    inherited from its classes). Can be mixed into any class,
    and will work on any instance.
    """
    def __gatherAttrs(self):
        attrs = []
        for key in sorted(self.__dict__):
            attrs.append('%s=%s' % (key, getattr(self, key)))
        return ', '.join(attrs)
    def __str__(self):
        return '[%s: %s]' % (self.__class__.__name__, self.__gatherAttrs())


if __name__ == '__main__':
    class TopTest(AttrDisplay):
        count = 0
        def __init__(self):
            self.attr1 = TopTest.count
            self.attr2 = TopTest.count + 1
            TopTest.count += 2

    class SubTest(TopTest):
        pass

    X, Y = TopTest(), SubTest()
    Log.debug(X)                         # Show all instance attrs
    Log.debug(Y)                         # Show lowest class name

class ListInstance:
    """
    Mix-in class that provides a formatted Log.debug() or str() of
    instances via inheritance of __str__, coded here; displays
    instance attrs only; self is the instance of lowest class;
    uses __X names to avoid clashing with client's attrs
    """
    def __str__(self):
        return '<Instance of %s, address %s:\n%s>' % (
                           self.__class__.__name__, # My class's name
                           id(self), # My address
                           self.__attrnames())              # name=value list
    def __attrnames(self):
        result = ''
        for attr in sorted(self.__dict__):                  # Instance attr dict
            result += '\tname %s=%s\n' % (attr, self.__dict__ [attr])
        return result

class ListInherited:
    """
    Use dir() to collect both instance attrs and names
    inherited from its classes; Python 3.0 shows more
    names than 2.6 because of the implied object superclass
    in the new-style class model; getattr() fetches inherited
    names not in self.__dict__; use __str__, not __repr__,
    or else this loops when printing bound methods!
    """
    def __str__(self):
        return ' <Instance of %s, address %s:\n%s>' % (
                           self.__class__.__name__, # My class's name
                           id(self), # My address
                           self.__attrnames())              # name=value list
    def __attrnames(self):
        result = ''
        for attr in dir(self):                              # Instance dir()
            if attr[:2] == '__' and attr[-2:] == '__':      # Skip internals
                result += '\tname %s=<>\n' % attr
            else:
                result += '\tname %s=%s\n' % (attr, getattr(self, attr))
        return result
    
class ListTree:
    """
    Mix-in that returns an __str__ trace of the entire class
    tree and all its objects' attrs at and above self;
    run by Log.debug(), str() returns constructed string;
    uses __X attr names to avoid impacting clients;
    uses generator expr to recurse to superclasses;
    uses str. format() to make substitutions clearer
    """
    def __str__(self):
        self. __visited = {}
        return ' <Instance of {0}, address {1}:\n{2}{3}>'.format(
                           self.__class__.__name__,
                           id(self),
                           self.__attrnames(self, 0),
                           self.__listclass(self.__class__, 4))
    def __listclass(self, aClass, indent):
        dots = ' .' * indent
        if aClass in self.__visited:
            return '\n{0}<Class {1}:, address {2}: (see above)>\n'.format(
                           dots,
                           aClass.__name__,
                           id(aClass))
        else:
            self.__visited[aClass] = True
            genabove = (self.__listclass(c, indent + 4) for c in aClass.__bases__)
            return '\n{0}<Class {1}, address {2}:\n{3}{4}{5}>\n'.format(
                           dots,
                           aClass.__name__,
                           id(aClass),
                           self.__attrnames(aClass, indent),
                           ''.join(genabove),
                           dots)
    def __attrnames(self, obj, indent):
        spaces = ' ' * (indent + 4)
        result = ''
        for attr in sorted(obj.__dict__):
            if attr.startswith('__') and attr.endswith('__'):
                result += spaces + '{0}=<>\n'.format(attr)
            else:
                result += spaces + '{0}={1}\n'.format(attr, getattr(obj, attr))
        return result                

class Set:
    def __init__(self, value=[]):    # Constructor
        self.data = []                 # Manages a list
        self.concat(value)
    def intersect(self, other):        # other is any sequence
        res = []                       # self is the subject
        for x in self.data:
            if x in other:             # Pick common items
                res.append(x)
        return Set(res)                # Return a new Set
    def union(self, other):            # other is any sequence
        res = self.data[:]             # Copy of my list
        for x in other:                # Add items in other
            if not x in res:
                res.append(x)
        return Set(res)
    def concat(self, value):           # value: list, Set...
        for x in value:                # Removes duplicates
            if not x in self.data:
                self.data.append(x)
    def __len__(self):          return len(self.data)            # len(self)
    def __getitem__(self, key): return self.data[key]            # self[i]
    def __and__(self, other):   return self.intersect(other)     # self & other
    def __or__(self, other):    return self.union(other)         # self | other
    def __repr__(self):         return 'Set:' + repr(self.data)  # Log.debug()

class Set_from_list(list):
    def __init__(self, value = []):      # Constructor
        list.__init__([])                # Customizes list
        self.concat(value)               # Copies mutable defaults
    def intersect(self, other):          # other is any sequence
        res = []                         # self is the subject
        for x in self:
            if x in other:               # Pick common items
                res.append(x)
        return Set(res)                  # Return a new Set
    def union(self, other):              # other is any sequence
        res = Set(self)                  # Copy me and my list
        res.concat(other)
        return res
    def concat(self, value):             # value: list, Set . . .
        for x in value:                  # Removes duplicates
            if not x in self:
                self.append(x)
    def __and__(self, other): return self.intersect(other)
    def __or__(self, other):  return self.union(other)
    def __repr__(self):       return 'Set:' + list.__repr__(self)
    
