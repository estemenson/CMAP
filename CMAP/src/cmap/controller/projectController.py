# -*- coding: utf-8 -*-
'''
Created on Sep 26, 2010

@author: stevenson
'''
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from agileConfig import Config
from cmap.model.projectModel import ProjectModel
from cmap.view.baseViews import MinView

try:
    Log = Config().log.logger
except Exception:
    from petaapan.utilities.console_logger import ConsoleLogger
    Log = ConsoleLogger('CMAP')

from cmap.controller.basicControllers import ArtefactController
from pymt.ui.window import MTWindow
from pymt.base import runTouchApp
class ProjectCtrl(ArtefactController):
    def __init__(self,root, file=None, **kwargs):
        kwargs.setdefault('mini_view_type', MinView)#ProjectMinView)
        kwargs.setdefault('view_type', MinView)#ProjectMinView)
        kwargs.setdefault('get_artefact',None)
        kwargs.setdefault('ctrl_container', None)
        kwargs.setdefault('model', ProjectModel)
        kwargs['view_type_name'] = 'Project'
        super(ProjectCtrl,self).__init__(root, file, **kwargs)
    def _get_backlog(self): return self.model.ProjectBackLog
    def _set_backlog(self,  value): 
        self.model.ProjectBackLog = value
    backlog = property(_get_backlog, _set_backlog)
    def _get_releases(self): 
        return self.model.Releases
    def _set_releases(self,  value): 
        self.model.Releases = value
    releases = property(_get_releases, _set_releases)
    def _get_owner(self): return self.model.Owner
    def _set_owner(self, value): 
        self.model.Owner = value
    owner = property(_get_owner, _set_owner)
    def _get_scrum_master(self): return self.model.ScrumMaster
    def _set_scrum_master(self, value): 
        self.model.ScrumMaster = value
    scrumMaster = property(_get_scrum_master, _set_scrum_master)
    def _get_status(self): return self.model.Status
    def _set_status(self, value): 
        self.model.Status = value
    status = property(_get_status, _set_status)

class ProjectController(ArtefactController):
    def __init__(self, main, defn=None, **kwargs):
        kwargs['view_type_name'] = 'Project'
        super(ProjectController,self).__init__(main, defn, **kwargs)
    def _get_backlog(self): return self._model.ProjectBackLog
    def _set_backlog(self,  value): 
        self._model.ProjectBackLog = value
    backlog = property(_get_backlog, _set_backlog)
    @property
    def Releases(self): 
        return self._model.Releases
    def _get_owner(self): return self._model.Owner
    def _set_owner(self, value): 
        self._model.Owner = value
    owner = property(_get_owner, _set_owner)
    def _get_scrum_master(self): return self._model.ScrumMaster
    def _set_scrum_master(self, value): 
        self._model.ScrumMaster = value
    scrumMaster = property(_get_scrum_master, _set_scrum_master)
    def _get_status(self): return self._model.Status
    def _set_status(self, value): 
        self._model.Status = value
    status = property(_get_status, _set_status)
if __name__ == '__main__':
    root = MTWindow()
    project = ProjectController(root)
    runTouchApp()