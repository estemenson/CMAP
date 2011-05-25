# -*- coding: utf-8 -*-
'''
Created on Aug 9, 2010

@author: stevenson
'''

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

# This will cause the configuration to be established from the
# configuration files and the command line. It will also setup
# the asynchronous handling systems for communication with the
# repository and the collaboration server
from agileConfig import Config, AsyncHandler
from async import ON_GITHUBNOTIFICATION
from cmap.view.stories.storyViews import MinStoryView, StoryView
from cmap.model.storyModel import StoryModel
from cmap.controller.storyController import StoryController
from cmap.view.projects.projectViews import ProjectView, ProjectMinView
from cmap.model.projectModel import ProjectModel
from cmap.controller.projectController import ProjectController
from cmap.view.releases.releaseViews import ReleaseView, ReleaseMinView
from cmap.model.releaseModel import ReleaseModel
from cmap.controller.releaseController import ReleaseController
from cmap.view.sprints.sprintViews import SprintMinView, SprintView
from cmap.model.sprintModel import SprintModel
from cmap.controller.sprintController import SprintController
from cmap.view.tasks.taskViews import TaskMinView, TaskView
from cmap.model.taskModel import TaskModel
from cmap.controller.taskController import TaskController
try:
    Log = Config().log.logger
except Exception: #IGNORE:W0703
    from petaapan.utilities.console_logger import ConsoleLogger
    Log = ConsoleLogger('AgiMan')
from cmap import BACKLOG,PROJECTS,RELEASES,SPRINTS,STORIES,TASKS,artefact_types
import os.path
from glob     import glob

class StoryAppModel(object):
    def __init__(self, **kwargs):
        self._artefacts = {}
        self.controller = kwargs['controller']
        self.datastore = Config().datastore
        Log.debug('Path to repository: %s' % self.datastore)
        self._current_backlog    = []
        self._current_project    = []
        self._current_release    = []
        self._current_sprint     = []
        self._current_story      = []
        self._current_task       = []

        self._currentProjectView = []
        self._currentReleaseView = []
        self._currentSprintView  = []
        self._currentStoryView   = []
        self._currentTaskView    = []

        self.get_local_artefacts()
        self.load_artefacts()
        
    def get_local_artefacts(self):
        '''
        Loads the file names of all local artefacts into a dictionary
        keyed on artefact type
        '''
        Log.debug('path: %s' % self.datastore)
        self.xmlFiles = {}
        for atype in artefact_types.keys():
            self.xmlFiles[atype] = []
            self.xmlFiles[atype].extend(glob(
                                os.path.join(self.datastore, atype, '*.xml')))
    def load_artefacts(self):
        for type in artefact_types:
            kwargs = artefact_types[type].copy()
            for artefact in self.xmlFiles[type]:
                Log.debug('loading %s' % artefact)
#                ctrl = self.controller.getArtefact(artefact, type['controller'],
#                                        type['model'], type['get_artefact'], 
#                    name=os.path.splitext(os.path.basename(artefact))[0])
                kwargs['name'] =\
                            name=os.path.splitext(os.path.basename(artefact))[0]
                kwargs['file'] = artefact
                ctrl = self.controller.getArtefact(**kwargs) 
                self.artefacts[ctrl.Id] = (ctrl,{})
                self.controller.add_new_artefact(ctrl,
                                     kwargs['container'],
                                     kwargs['viewCurrent'],
                                     self.artefacts[ctrl.Id][1])
    def trash(self,artefact,atype=None):
        Log.debug('Need to trash artefact: %s' % artefact)
        return
    def close(self,touch=None):
        pass
#        #close all the artefacts
#        for a in self.artefacts.values():
#            a[0].close()
#        for b in self.backlog.values():
#            b[0].close()
    
    @property        
    def artefacts(self):
        return self._artefacts
    @property
    def current_project(self):
        return self._current_project 
    @current_project.setter
    def current_project(self, value):
        self._current_project.append(value)
    @property
    def current_release(self):
        return self._current_release
    @current_release.setter
    def current_release(self, value):
        self._current_release.append(value)
    @property
    def current_sprint(self):
        return self._current_sprint
    @current_sprint.setter
    def current_sprint(self, value):
        self._current_sprint.append(value)
    @property
    def current_story(self):
        return self._current_story
    @current_story.setter
    def current_story(self, value):
        self._current_story.append(value)
    @property
    def current_task(self):
        return self._current_task
    @current_task.setter
    def current_task(self, value):
        self._current_task.append(value)
    @property
    def currentProjectView(self):
        return self._currentProjectView
    @currentProjectView.setter
    def currentProjectView(self, value):
        self._currentProjectView.append(value)
    @property
    def currentReleaseView(self):
        return self._currentReleaseView
    @currentReleaseView.setter
    def currentReleaseView(self, value):
        self._currentReleaseView.append(value)
    @property
    def currentSprintView(self):
        return self._currentSprintView
    @currentSprintView.setter
    def currentSprintView(self, value):
        self._currentSprintView.append(value)
    @property
    def currentStoryView(self):
        return self._currentStoryView
    @currentStoryView.setter
    def currentStoryView(self, value):
        self._currentStoryView.append(value)
    @property
    def currentTaskView(self):
        return self._currentTaskView
    @currentTaskView.setter
    def currentTaskView(self, value):
        self._currentTaskView.append(value)
