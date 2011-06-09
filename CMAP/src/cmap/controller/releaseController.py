# -*- coding: utf-8 -*-
'''
Created on 2010-10-04

@author: steve
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

from cmap.controller.basicControllers import ArtefactController
from pymt.ui.window import MTWindow
from pymt.base import runTouchApp

class ReleaseController(ArtefactController):
    def __init__(self, main, defn=None, **kwargs):
        kwargs['view_type_name'] = 'Release'
        super(ReleaseController,self).__init__(main, defn, **kwargs)
        if kwargs.setdefault('project',None):
            self.project = kwargs['project']
    @property 
    def Sprints(self): return self._model.Sprints
    def _get_project(self):
        if self.Id is None: return self.Parent 
        return self._model.Project
    def _set_project(self,  value): 
        self._model.Project = value
    project = property(_get_project, _set_project)
if __name__ == '__main__':
    root = MTWindow()
    project = ReleaseController(root)
    runTouchApp()