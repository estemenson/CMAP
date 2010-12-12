# -*- coding: utf-8 -*-
'''
Created on Jul 27, 2010

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
    from petaapan.utilities.console_logger import ConsoleLogger
    Log = ConsoleLogger('CMAP')

from pymt.ui.window import MTWindow
from cmap.controller.basicControllers import ArtifactController
from pymt.base import runTouchApp


class SprintController(ArtifactController):
    def __init__(self, main, defn=None, **kwargs):
        kwargs['view_type_name'] = 'Sprint'
        super(SprintController,self).__init__(main,defn,**kwargs)
        self._release = None
        if kwargs.setdefault('release',None):
            self.release = kwargs['release'] 
        
    def _get_stories(self): return self._model.Stories
    def _set_stories(self,  value): 
        self._model.Stories = value
    stories = property(_get_stories, _set_stories)
    def _get_release(self):
        if self.Id is None: return self._release 
        return self._model.Release
    def _set_release(self,  value):
        if self.Id is None:
            self._release = value
        else: 
            self._model.Release = value
    release = property(_get_release, _set_release)

if __name__ == '__main__':
    root = MTWindow()
    project = SprintController(root)
    runTouchApp()