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
except Exception: #IGNORE:W0703
    from petaapan.utilities.console_logger import ConsoleLogger
    Log = ConsoleLogger('CMAP')

from pymt.ui.window import MTWindow
from cmap.controller.basicControllers import ArtefactController
from pymt.base import runTouchApp

class TaskController(ArtefactController):
    def __init__(self, main, defn=None, **kwargs):
        kwargs['view_type_name'] = 'Task'
        super(TaskController,self).__init__(main,defn,**kwargs)
        self._project = None
        if kwargs.setdefault('p_artefact', None):
            self.story = kwargs['p_artefact']
    def _get_sprint(self): return self._model.Sprint
    def _set_sprint(self,  value): 
        self._model.Sprint = value
    sprint = property(_get_sprint, _set_sprint)
    def _get_story(self): return self._model.Story
    def _set_story(self, value):
        self._model.Story = value
    story = property(_get_story, _set_story)
    def _get_project(self):
        return self._model.project if self.Id else self._project
    def _set_project(self,  value): 
        self._model.project = value
    project = property(_get_project, _set_project)
if __name__ == '__main__':
    root = MTWindow()
    project = TaskController(root)
    runTouchApp()