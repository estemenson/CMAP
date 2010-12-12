# -*- coding: utf-8 -*-
'''
Created on Aug 9, 2010

@author: stevenson
'''

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

# Determine maximum physical screen size
from sys import platform
screen_size = []
max_size = [0,0]
min_size = [100000,100000]
if platform == 'win32':
    try:
        from win32api import EnumDisplayMonitors
        for mon in EnumDisplayMonitors():
            dim = mon[2]
            ss = (dim[2] - dim[0], dim[3] - dim[1])
            screen_size.append(ss)
            if ss[0] < min_size[0]:
                min_size[0] = ss[0]
            if ss[1] < min_size[1]:
                min_size[1] = ss[1]
            if ss[1] > max_size[0]: #Screen is considered bigger if height is bigger
                max_size = ss
    except ImportError:
        pass
if len(screen_size) == 0:
    screen_size.append((1024, 768))
    min_size = max_size = screen_size[0]
def get_min_screen_size():
    return (min_size[0],min_size[1])
def get_max_screen_size():
    return (max_size[0],max_size[1])
def get_screen_sizes():
    return screen_size
def scale_tuple(t,scale_width, scale_height=None):
    '''reduces a given tuple by the decimal value passed
        t = (100,100) and scale = .25
        returns (75,75)
        to increase the values use a negative scale
        t = (100,100) and scale = -.25
        returns (125,125)
    '''    
    if scale_width is None: return t
    if scale_width == 1 and (scale_height is None or scale_height == 1):
        return t
    elif scale_width ==1 and scale_height is not None:
        #only scale the height
        return (int(t[0]), int(t[1] - (t[1] * scale_height)))
    if scale_height is None:
        scale_height = scale_width
    return (int(t[0] - (t[0] * scale_width)), int(t[1] - (t[1] * scale_height)))
def tuple_diff(t1,t2,delta):
    '''
        checks is 2 tuples have change by less then delta
        returns true if change is less then delta
    '''    
    if t1[0] != t2[0]:
        #x has changed, is the change aceptable
        if abs(t2[0]-t1[0]) > delta:
            return False
    if t1[1] != t2[1]:
        #x has changed, is the change aceptable
        if abs(t2[1]-t1[1]) > delta:
            return False
    return True
        