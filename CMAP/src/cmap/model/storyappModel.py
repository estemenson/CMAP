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
from xml.dom import minidom
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
        self._isDirty = False
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
        #self.get_view_data()
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
                kwargs['name'] =\
                            name=os.path.splitext(os.path.basename(artefact))[0]
                kwargs['file'] = artefact
                ctrl = self.controller.getArtefact(**kwargs) 
                self._artefacts[ctrl.Id] = (ctrl,{})
                self.controller.add_new_artefact(ctrl,
                                     kwargs['container'],
                                     kwargs['viewCurrent'],
                                     self._artefacts[ctrl.Id][1])
    def get_view_data(self):
        #retrieve information about size and position of artefacts
        self.app_file = os.path.join(self.datastore, 'storyApp.xml')
        if not os.path.exists(self.app_file):
            #just get the template
            #_file = os.path.join(self.datastore, '..','data','storyApp.xml')
            self._dom = minidom.parseString(
                                 '''<?xml version="1.0" encoding="UTF-8"?>
                                <storyApp></storyApp>
                                ''')
        else:
            self._dom = minidom.parse(self.app_file)
        self._app = self._dom.getElementsByTagName('storyApp')[0] 
        for element in [n for n in self._app.childNodes \
                   if n.nodeName == 'Artefact']:
                  #if n.nodeType == minidom.Node.ELEMENT_NODE]:
            self.parse(element)
    def parse(self,node):
        if node.hasAttribute('Id') and node.hasAttribute('pos') and\
            node.hasAttribute('size') and node.hasAttribute('open'):
            _id         = node.getAttribute('Id')
            _ctrl       = self._artefacts[_id] 
            _pos        = _ctrl[1]['pos']       = eval(node.getAttribute('pos'))
            _size       = _ctrl[1]['size']      = eval(node.getAttribute('size'))
            _scale      = _ctrl[1]['scale']     = eval(node.getAttribute('scale'))
            _rotation   = _ctrl[1]['rotation']  = eval(\
                                                node.getAttribute('rotation'))
            _open       = _ctrl[1]['open']      = node.getAttribute('open')
            
            self.controller.create_view_and_open(_ctrl[0],open=_open,
                                                 size=_size,pos=_pos,
                                                 scale=_scale,
                                                 rotation=_rotation)
            if _open == 'True':
                print('We need to redisplay this artefact on startup %s' % _id)
                #self.controller.add_current_artefact(_ctrl[0]._type,_ctrl[0])
            else:
                print('Artefact %s will reopen in old position next time user chooses to open it.' % _id)
    def trash(self,id):
        Log.debug('Delete artefact: %s' % id)
        _art = self.get_dom_artefact(id)
        if _art:
            self._app.removeChild(_art)
        del self._artefacts[id]
        return
    def close(self,touch=None):
        #persist data about open artefacts, their size and positions
#        for _id in self._artefacts:
#            _pos = self._artefacts[_id][1].get('pos')
#            if _pos:        
#            #if it has a position then it must have a size and open status    
#                _artefact = self._dom.createElement('Artefact')
#                _artefact.setAttribute('Id', _id)
#                _artefact.setAttribute('pos', str(_pos))
#                _artefact.setAttribute('size',\
#                                           str(self._artefacts[_id][1]['size']))
#                _artefact.setAttribute('open', self._artefacts[_id][1]['open'])
#                self._app.appendChild(_artefact)
        if self._isDirty:
            with open(self.app_file, 'w') as f:
                self._dom.writexml(f)
    def artefact_changed(self, **kwargs):#id, size, pos, open):
        self._isDirty = True
        ctrl = self._artefacts[kwargs['Id']]
        id = ctrl[0].Id
        ctrl[1]['size'] = kwargs['size']
        ctrl[1]['pos'] = kwargs['pos']
        ctrl[1]['open'] = kwargs['open']
        ctrl[1]['rotation'] = kwargs['rotation']
        ctrl[1]['scale'] = kwargs['scale']
        #get this artefact from the dom
        #or create a new element
        _e = self.get_dom_artefact(id)
        if not _e:
            _e = self._dom.createElement('Artefact')
            _e.setAttribute('Id', id)
            self._app.appendChild(_e)
        _e.setAttribute('size', str(kwargs['size']))
        _e.setAttribute('pos', str(kwargs['pos']))
        _e.setAttribute('open', kwargs['open'])
        _e.setAttribute('rotation', str(kwargs['rotation']))
        _e.setAttribute('scale', str(kwargs['scale']))
    def get_dom_artefact(self, id):
        if 'pos' in self._artefacts[id][1]:
            for element in [n for n in self._app.childNodes \
                   if n.nodeName == 'Artefact']:
                _id = element.getAttribute('Id')
                if _id == id: return element
        return None
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
