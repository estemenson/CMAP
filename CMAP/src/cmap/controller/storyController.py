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

from cmap.tools.myTools import scale_tuple
from cmap.view.stories.storyViews import StoryView, MinStoryView
from pymt.ui.window import MTWindow
from pymt.base import runTouchApp
from cmap.controller.basicControllers import ArtifactController

class StoryController(ArtifactController):
    def __init__(self,main, defn=None, **kwargs):
        kwargs['view_type_name'] = 'Story'
        super(StoryController,self).__init__(main, defn, **kwargs)
        if kwargs.setdefault('project',None):
            self.project = kwargs['project'] 
        if kwargs.setdefault('p_artifact',None):
            self.sprint = kwargs['p_artifact'] 
        
    def createView(self):
        pos = None
        if self.view is not None: pos = self.view.pos
        if self.isMinimal:
            self._view = MinStoryView(self.root,self, 
                              name=self._model.Name,
                              id=self._model.Id,
                              as_a=self._model.As_a,
                              want_to=self._model.Want_to,
                              so_that=self._model.So_that,
                              estimate=self._model.EstimateFinishDate,
                              actual=self._model.ActualFinish ,
                              owner=self._model.Owner,
                              description=self._model.Description,
                              control_scale=0.7, cls='type1css')
            self.story_view_size = scale_tuple(self.view.grid_size,-0.001,-0.03)
        else:
            self._view = StoryView(self.root,self, 
                              name=self._model.Name,
                              id=self._model.Id,
                              as_a=self._model.As_a,
                              want_to=self._model.Want_to,
                              so_that=self._model.So_that,
                              estimate=self._model.EstimateFinishDate,
                              actual=self._model.ActualFinish ,
                              owner=self._model.Owner,
                              description=self._model.Description,
                              control_scale=0.7, cls='type1css')
            self.story_view_size = scale_tuple(self.view.grid_size,0.15,.03)
        self.view.size = self.story_view_size
        if pos is not None:
            self.view.pos = pos
        else : self.view.pos = (100,200)
        
 
    def _get_as_a(self): return self._model.As_a  
    def _set_as_a(self, value): 
        self._model.As_a = value
    as_a = property(_get_as_a, _set_as_a)
    def _get_want_to(self): return self._model.Want_to
    def _set_want_to(self,  value): 
        self._model.Want_to = value
    want_to = property(_get_want_to, _set_want_to)
    def _get_so_that(self): return self._model.So_that
    def _set_so_that(self,  value): 
        self._model.So_that = value
    so_that = property(_get_so_that, _set_so_that)
    def _get_owner(self): return self._model.Owner
    def _set_owner(self, value): 
        self._model.Owner = value
    owner = property(_get_owner, _set_owner)
    def _get_tasks(self): return self._model.Tasks
    def _set_tasks(self, value): self._model.Tasks = value
    tasks = property(_get_tasks, _set_tasks)
    def _get_project(self): return self._model.Project
    def _set_project(self, value): 
        self._model.Project = value
    project = property(_get_project, _set_project)
    def _get_sprint(self): return self._model.Sprint
    def _set_sprint(self, value): 
        self._model.Sprint = value
    sprint = property(_get_sprint, _set_sprint)
if __name__ == '__main__':
    root = MTWindow()
    project = StoryController(root)
    runTouchApp()