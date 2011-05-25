# -*- coding: utf-8 -*-
'''
Created on Jun 5, 2010

@author: stevenson
'''
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from os import path
import shelve
import logging
try:
    from agileConfig import Config
    Log = Config().log.logger
except:
    Log = logging.getLogger()
    Log.setLevel(logging.DEBUG)
from pymt.gesture import GestureDatabase

class myGestures(GestureDatabase):
    def pull_gesture_from_shelf(self, name):
        try:
            _gdb = 'gesturesDB'
            #Log.debug('current directory: %s' % path.abspath(path.curdir))
            _file = path.join(Config().gestures, _gdb)
#            if not path.exists(_file):
#                _file = path.join(path.join(path.join(\
#                        path.abspath(path.curdir),'cmap'),'gestures'),_gdb)
            db = shelve.open(_file)
            if name in db.keys():
                return db[str(name)]
            return
        finally:
            db.close()
    def push_gesture_to_shelf(self, gesture):
        try:
            db = shelve.open('gesturesDB')
            db[str(gesture.label)] = gesture
            if not self.find(gesture):
                self.add_gesture(gesture)
        finally:
            db.close()
    def remove_gesture_from_shelf(self,gesture):
        try:
            db = shelve.open('gesturesDB')
            del db[str(gesture.label)]
        finally:
            db.close()
