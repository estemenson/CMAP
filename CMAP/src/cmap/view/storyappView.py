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
try:
    Log = Config().log.logger
except Exception: #IGNORE:W0703
    from petaapan.utilities.console_logger import ConsoleLogger
    Log = ConsoleLogger('AgiMan')
    
    
# Gives access to the StoryApp controller from anywhere in the application
_storyapp_singleton = None 
def Storyapp(): return _storyapp_singleton

from cmap.tools.decorators import MyDragableContainer
from cmap.controller.sprintController import SprintController
from cmap.controller.taskController import TaskController
from cmap.model.projectModel import ProjectModel
from cmap.model.releaseModel import ReleaseModel
from cmap.view.releases.releaseViews import ReleaseMinView, ReleaseView
from random import choice
from cmap.model.sprintModel import SprintModel
from cmap.view.sprints.sprintViews import SprintView, SprintMinView
from cmap.model.taskModel import TaskModel
from cmap.view.tasks.taskViews import TaskView, TaskMinView
from cmap.model.storyModel import StoryModel
from cmap.tools.classTools import Dummy
from pymt.ui.widgets.sidepanel import MTSidePanel
from pymt.ui.widgets.coverflow import MTCoverFlow
from cmap.view.projects.projectViews import ProjectMinView, ProjectView
from glob import glob
from cmap.tools.myTools import get_min_screen_size, scale_tuple
from pymt.ui.widgets.klist import MTList
from cmap.controller.storyController import StoryController
from cmap.controller.projectController import ProjectController
from cmap.controller.releaseController import ReleaseController
from cmap.controller.basicControllers import ArtefactController
from pymt.ui.widgets.button import MTToggleButton, MTButton 
from cmap.tools.my_buttons import MyImageButton
from pymt.loader import Loader
from pymt.ui.widgets.layout.gridlayout import MTGridLayout
from pymt.utils import curry
from cmap.view.stories.storyViews import pixels, minimal_size, StoryView, \
        MinStoryView
import os.path
from cmap.gestures.myGestures import myGestures
from cmap.gestures.NewGestures import get_and_or_store_gesture
from pymt.ui.widgets.scatter import MTScatter
from pymt.ui.colors import css_add_sheet
from cmap.tools.capture import MyCaptureWidget
size = get_min_screen_size()

from cmap.tools.borders import MyInnerWindow
from pymt.ui.window import MTWindow
from pymt.base import runTouchApp, stopTouchApp
from pygame.display import set_caption
from cmap import BACKLOG,PROJECTS,RELEASES,SPRINTS,STORIES,TASKS,artefact_types
GestureCSS = '''
.gesturecss {
    bg-color: rgba(185,211,238, 255);
    border-color: rgb(100, 100, 220);
    border-width: 20;
    draw-border: 1;    
}
'''
css_add_sheet(GestureCSS)

LABEL_NEW_PROJECT   = 'New\nProject...'
LABEL_NEW_RELEASE   = 'New\nRelease...'
LABEL_NEW_SPRINT    = 'New\nSprint...'
LABEL_NEW_STORY     = 'New\nStory...'
LABEL_NEW_TASK      = 'New\nTask...'
LABEL_BROWSE_BACKLOG='Browse\nBacklog...'
LABEL_BROWSE_PROJECT='Browse\nProjects...'
LABEL_BROWSE_RELEASE='Browse\nReleases...'
LABEL_BROWSE_SPRINT ='Browse\nSprints...'
LABEL_BROWSE_STORY  ='Browse\nStories...'
LABEL_BROWSE_TASK   ='Browse\nTasks...'

class StoryAppView(MyInnerWindow):
    def __init__(self,**kwargs):
        self.controller = kwargs['controller']
        super(StoryAppView, self).__init__(**kwargs)
        set_caption("Collaborative Multitouch Agile Planner")
        self.root_window = kwargs['root_window']
        self.canvas = None
        self.backlog_flow_open  = True
        self.projects_flow_open = True
        self.releases_flow_open = True
        self.sprint_flow_open   = True
        self.story_flow_open    = True
        self.task_flow_open     = True
        self.buttons = {}
        self.labels = {}
        self.backlog_list_layout = MTGridLayout(rows=1)
        self.main_ctlrs_container = MTSidePanel(\
                                        corner=MTToggleButton(padding=5,
                                                        label='File...',
                                                        size=(60,45)),
                                        layout=MTGridLayout(rows=1),
                                        align='left',
                                        side='top') 
        self.backlog_container = MTSidePanel(\
                                        corner=MTToggleButton(padding=5,
                                                        label='Backlog...',
                                                        size=(100,45)),
                                        align='middle',
                                        side='bottom',
                                        pos=(0,self.root_window.height-100)) 
        
        # Load the default image for buttons and cover flows
        #path = os.path.join(os.getcwd(), 'data', 'ModelScribble.jpg')
        self.path = Config().datastore
        Log.debug('Path to repository: %s' % self.path)
        path = os.path.join(self.path,'..', 'data', 'ModelScribble.jpg')
        Log.debug('Data Schemas in: %s' % path)
        self._default_button_size = (100, 100)
        self._default_image = Loader.image(path)

        #create the cover flow containers for each artefact type
        self.createFlows([
        (BACKLOG, 1,self.flow_backlog_select, self.createNewStoryButton),
        (PROJECTS,0,self.flow_projects_select,self.createNewProjectButton),
        (RELEASES,0,self.flow_release_select, self.createNewReleaseButton),
        (SPRINTS, 0,self.flow_sprint_select,  self.createNewSprintButton),
        (STORIES, 0,self.flow_story_select,   self.createNewStoryButton),
        (TASKS,   0,self.flow_task_select,    self.createNewTaskButton)])

        #make the coverflow containers dragable
        self.dragable_backlog_flow = MyDragableContainer(self.backlog_flow,
                                    True, size_scaler=(-.1,-.1), cls='dragcss',
                                    use_widget_size=False)
        self.dragable_project_flow = MyDragableContainer(self.projects_flow,
                                    True, size_scaler=(-.2,-.2), cls='dragcss')
        self.dragable_release_flow = MyDragableContainer(self.release_flow,
                                    True, size_scaler=(-.2,-.2), cls='dragcss')
        self.dragable_sprint_flow = MyDragableContainer(self.sprint_flow,
                                    True, size_scaler=(-.2,-.2), cls='dragcss')
        self.dragable_story_flow = MyDragableContainer(self.story_flow,
                                    True, size_scaler=(-.2,-.2), cls='dragcss')
        self.dragable_task_flow = MyDragableContainer(self.task_flow,
                                                          True)
        self.backlog_list = MTList(size=(self.root_window.width,100),pos=(0,0))
        self.backlog_list.add_widget(self.backlog_list_layout)
        self.backlog_container.add_widget(self.backlog_list)

        #enable gesture detection
        self.enable_gestures()
        self.canvas.add_widget(self.backlog_container)
        self.addMainControls()
    def addMainControls(self):
        self.main_ctlrs_container.add_widget(self.createNewProjectButton())
        self.main_ctlrs_container.add_widget(self.createNewReleaseButton())
        self.main_ctlrs_container.add_widget(self.createNewSprintButton())
        self.main_ctlrs_container.add_widget(self.createNewStoryButton())
        self.main_ctlrs_container.add_widget(self.createNewTaskButton())
        self.main_ctlrs_container.add_widget(self.createNewBacklogFlowButton())
        self.main_ctlrs_container.add_widget(self.createNewProjectFlowButton())
        self.main_ctlrs_container.add_widget(self.createNewReleasesFlowButton())
        self.main_ctlrs_container.add_widget(self.createNewSprintFlowButton())
        self.main_ctlrs_container.add_widget(self.createNewStoryFlowButton())
        self.main_ctlrs_container.add_widget(self.createNewTaskFlowButton())
        self.canvas.add_widget(self.main_ctlrs_container)
    def add_new_artefact(self, ctrl, container, callback, ret):
        '''add a button to access the artifact in the appropriate container(s)
    :Parameters:
        `ctrl` : ArtefactController, A derived controller from the 
            ArtefactController base class
        `container` : List containing all the string names of the containers 
            where access to this artefact is needed, usually a CoverFlow or 
            Kinectic List or both
        'callback' : method to be called when when a press event is fired
        'ret' : returns this dictionary keyed on the string names of each 
            container where a button was added, this dictionary is used as a 
            short cut to all buttons that access this artefact
    :Returns: the dictionary 'ret'
    '''        
        for c in container:
            _lbl = MyImageButton(id=ctrl.Id, size=self._default_button_size,
                                 image=self._default_image)
            self.check_btn_width(_lbl)
            _lbl.push_handlers(on_press=curry(self.__getattribute__(callback), 
                                                                        _lbl))
            self.__getattribute__(c).add_widget(_lbl)
            ret[c] = _lbl
        return ret
    def check_btn_width(self,btn):
        _label = btn.label
        _w = int(len(_label) *pixels)
        if _w > btn.width:
            if not btn.multiline:
                btn.multiline = True
            btn.label = '\n'.join(_label.split('-'))
    def close(self,touch=None):
        self.controller.close(touch)
        #close all the artefacts
#        for a in self.artefacts.values():
#            a[0].close()
#        for b in self.backlog.values():
#            b[0].close()
#        self.add_to_git()
#        AsyncHandler().shutdown()
        super(StoryAppView, self).close(touch)
    def createFlows(self, flows): 
        _sf_pos = (200,200)
        for type, container, callback, btn in flows:
            flow = artefact_types[type]['container'][container]
            try:
                self.__setattr__(flow,
                                 MTCoverFlow(
                                   layout=MTGridLayout(spacing=10,rows=1),
                                   pos=_sf_pos,
                                   size=self._default_button_size,
                                   cover_spacing=20,
                                   cover_distance=115,
                                   thumbnail_size=self._default_button_size))
            except Exception: #IGNORE:W0703
                Log.exception("Unable to create %s cover flow" % type)
                self.__setattr__(flow,MTGridLayout(rows=1, pos=_sf_pos))
            self.__getattribute__(flow).push_handlers(on_select=callback)
            self.__getattribute__(flow).add_widget(btn())
    def createNewBacklogButton(self):
        return self.create_button(LABEL_NEW_STORY,curry(self.new_story_pressed))
    def createNewBacklogFlowButton(self):
        return self.create_button(LABEL_BROWSE_BACKLOG,
                                  curry(self.flow_pressed,\
                        'backlog_flow_open',self.dragable_backlog_flow))
    def createNewProjectButton(self):
        return self.create_button(LABEL_NEW_PROJECT,curry(\
                                                    self.new_project_pressed))
    def createNewProjectFlowButton(self):
        return self.create_button(LABEL_BROWSE_PROJECT,\
                                  curry(self.flow_pressed,\
                        'projects_flow_open',self.dragable_project_flow))
    def createNewReleaseButton(self):
        return self.create_button(LABEL_NEW_RELEASE,curry(\
                                                    self.new_release_pressed))
    def createNewReleasesFlowButton(self):
        return self.create_button(LABEL_BROWSE_RELEASE,
                                  curry(self.flow_pressed,\
                        'releases_flow_open',self.dragable_release_flow))
    def createNewSprintButton(self):
        return self.create_button(LABEL_NEW_SPRINT, curry(\
                                                    self.new_sprint_pressed))
    def createNewSprintFlowButton(self):
        return self.create_button(LABEL_BROWSE_SPRINT,
                                  curry(self.flow_pressed,\
                        'sprint_flow_open',self.dragable_sprint_flow))
    def createNewStoryButton(self):
        return self.create_button(LABEL_NEW_STORY,curry(self.new_story_pressed))
    def createNewStoryFlowButton(self):
        return self.create_button(LABEL_BROWSE_STORY, 
            curry(self.flow_pressed,\
                        'story_flow_open',self.dragable_story_flow))
    def createNewTaskButton(self):
        return self.create_button(LABEL_NEW_TASK,curry(self.new_task_pressed))
    def createNewTaskFlowButton(self):
        return self.create_button(LABEL_BROWSE_TASK,
                                  curry(self.flow_pressed,\
                        'task_flow_open',self.dragable_task_flow))
    def create_button(self,label,callback):
        _btn = MTButton(multiline=True, label=label, anchor_x='left',
                        halign='left', padding_x=8)
        _btn.connect('on_press', callback)
        _max = 1
        for _s in label.splitlines():
            _l = len(_s)
            if _l > _max:
                _max = _l
        _btn.width = min(int(_max * pixels),100)
        return _btn
    def enable_gestures(self):
        print("enabling gestures")
        gdb = myGestures()
        defn =  os.path.join(Config().gestures,'xmlGestures','gestures.xml')
        #import S for New Story
        try:
            get_and_or_store_gesture(gdb, 'New Story', 'New_Story',defn)
            get_and_or_store_gesture(gdb, 'Projects', 'Projects',defn)
            get_and_or_store_gesture(gdb, 'Projects1', 'Projects1',defn)
            get_and_or_store_gesture(gdb, 'Releases', 'Releases',defn)
            get_and_or_store_gesture(gdb, 'Releases1', 'Releases1',defn)
            get_and_or_store_gesture(gdb, 'Sprints', 'Sprints',defn)
            get_and_or_store_gesture(gdb, 'Sprints1', 'Sprints1',defn)
            get_and_or_store_gesture(gdb, 'Sprints2', 'Sprints2',defn)
            get_and_or_store_gesture(gdb, 'Tasks', 'Tasks',defn)
            get_and_or_store_gesture(gdb, 'Tasks1', 'Tasks1',defn)
            get_and_or_store_gesture(gdb, 'Backlog', 'Backlog',defn)
            get_and_or_store_gesture(gdb, 'Backlog1', 'Backlog1',defn)
            get_and_or_store_gesture(gdb, 'Square', 'square',defn)
            get_and_or_store_gesture(gdb, 'X', 'x',defn)
        except Exception: #IGNORE:W0703
            print("Some exception in gestures")
        self.canvas = MTScatter(cls='gesturecss') 
        self.canvas.size = self.root_window.size
        self.canvas.pos = (0,0)
        super(StoryAppView,self).add_widget(self.canvas)
        if not self.canvas:
            print("No canvas in gestures ")
        capture = MyCaptureWidget(gdb, self)
        capture.size = self.canvas.size
        if not capture:
            print("No capture device in gestures")
        self.canvas.add_widget(capture)
    def flow_backlog_select(self,btn,*largs):
        #make the selected backlog item the active one
        self.controller.add_current_artefact('backlog',btn)
    def flow_projects_select(self,btn,*largs):
        #we need to populate the releases flow with any release 
        #in the current project
        self.load_children(self.controller.add_current_artefact('projects',btn),
                           'releases')
#        self.container_reset_children('release_flow')
#        self.container_reset_children('sprint_flow')
#        self.container_reset_children('story_flow')
#        self.container_reset_children('task_flow')
#        if self.current_project and self.current_project[0].Children:
#            for release in self.current_project[0].Children:
#                if release in self.artefacts:
#                    r = self.artefacts[release][0]
#                    if r.ArtefactType != 'Release': continue
#                    self.newRelease(r)
#                else:
#                    Log.debug('Project: %s found a release: %s not in releases' % \
#                              (self.current_project[0].Name,release))
    def flow_release_select(self,btn,*largs):
        #we need to populate the sprint flow with any sprints already
        #in the current release
        self.load_children(self.controller.add_current_artefact('releases',btn),
                           'sprints')
#        self.container_reset_children('sprint_flow')
#        self.container_reset_children('story_flow')
#        self.container_reset_children('task_flow')
#        if self.current_release and self.current_release[0].Children:
#            for sprint in self.current_release[0].Children:
#                if sprint in self.artefacts.keys():
#                    s = self.artefacts[sprint][0]
#                    if s.ArtefactType != 'Sprint': continue
#                    self.newSprint(s)
#                else:
#                    Log.debug('Release: %s found a sprint: %s not in sprints' % \
#                              (self.current_release[0].Name,sprint))
    def flow_sprint_select(self,btn,*largs):
        #we need to populate the story flow with any stories already
        #in the current sprint
        self.load_children(self.controller.add_current_artefact('sprints',btn),
                           'stories')
#        self.container_reset_children('story_flow')
#        self.container_reset_children('task_flow')
#        if self.current_sprint and self.current_sprint[0].Children:
#            for story in self.current_sprint[0].Children:
#                if story in self.artefacts.keys():
#                    s = self.artefacts[story][0]
#                    if s.ArtefactType != 'Story': continue
#                    self.newStory(s)
#                else:
#                    Log.debug('Sprint: %s found a story: %s not in stories' % \
#                              (self.current_sprint[0].Name,story))
    def flow_story_select(self,btn,*largs):
        #we need to populate the task flow with any tasks already
        #in the current story
        self.load_children(self.controller.add_current_artefact('stories',btn),
                           'tasks')
#        self.container_reset_children('task_flow')
#        if self.current_story and self.current_story[0].Children:
#            for task in self.current_story[0].Children:
#                if task in self.artefacts.keys():
#                    t = self.artefacts[task][0]
#                    if t.ArtefactType != 'Task': continue
#                    self.newTask(t)
#                else:
#                    Log.debug('Story: %s found a task: %s not in tasks' % \
#                              (self.current_story[0].Name,task))
    def flow_task_select(self,btn,*largs):
        self.controller.add_current_artefact('tasks',btn)
    def flow_pressed(self, flag, widget, *largs):
        _flag =  not self.__getattribute__(flag)
        self.__setattr__(flag, _flag)
        if not _flag:
            widget.pos = self.get_new_random_position()
        self.toggle_view_current_Artefact(widget)
    def fullscreen(self, *largs, **kwargs):
        super(StoryAppView,self).fullscreen()
        root_win = self.parent.children
        for rw in root_win:
            try:
                if rw.label == 'Back':
                    self.parent.remove_widget(rw)
                    rw.label = 'Exit'
                    rw.pos = (self.width - 100, 0)
                    rw.size=self._default_button_size
                    self.main_ctlrs_container.add_widget(rw)
                    Log.debug('Renamed back label to exit')
                    return
            except Exception: #IGNORE:W0703
                pass
    def get_new_random_position(self):
        return self.controller.get_new_random_position()
    def list_button_pressed(self, btn):
        ctrl = self.artefacts[btn.id][0]
        view = ctrl.view
        if view not in self.container.children:
            super(StoryAppView,self).add_widget(view)
        else: ctrl.app_btn_pressed()
    def load_children(self, id, type):
        self.controller.load_children(id, type)
    def new_backlog_pressed(self,*largs):
        self.controller.new_backlog_artefact(**artefact_types[BACKLOG])
    def new_project_pressed(self, *largs): 
        self.controller.new_project(**artefact_types[PROJECTS])
    def new_release_pressed(self, *largs): 
        self.controller.new_release(**artefact_types[RELEASES])
    def new_sprint_pressed(self, *largs): 
        self.controller.new_sprint(**artefact_types[SPRINTS])
    def new_story_pressed(self, *largs): 
        self.controller.new_story(**artefact_types[STORIES])
    def new_task_pressed(self, *largs): 
        self.controller.new_task(**artefact_types[TASKS])
    def toggle_view_current_Artefact(self, artefact):
        if artefact in self.container.children:
            self.remove_widget(artefact)
            return "False"
        self.add_widget(artefact)
        return "True"
    def trash(self,artefact):
        self.remove_widget(artefact)
    def unfullscreen(self, *largs, **kwargs):
        self.root_window.remove_widget(self)
        stopTouchApp()
        Log.info('Closing CMAP application')
    def update_story_btn_name(self,story):
        idu = story.Id
        btn = self.buttons[idu]
        if btn.id == idu:
            btn.label = story.Name
            self.check_btn_width(btn)
        return
    def viewCurrentBacklog(self,lbl, *largs): #IGNORE:W0613
        self.view_current_Artefact(lbl, 'current_backlog',\
                                    'flow_backlog_select', 'backlog')
    def viewCurrentProject(self,lbl, *largs): #IGNORE:W0613
        self.view_current_Artefact(lbl, 'current_project',\
                                    'flow_projects_select', 'projects')
    def viewCurrentRelease(self,lbl, *largs): #IGNORE:W0613
        self.view_current_Artefact(lbl, 'current_release',\
                                    'flow_release_select', 'releases')
    def viewCurrentSprint(self,lbl, *largs): #IGNORE:W0613
        self.view_current_Artefact(lbl, 'current_sprint',\
                                    'flow_sprint_select', 'sprints')
    def viewCurrentStory(self,lbl, *largs): #IGNORE:W0613
        self.view_current_Artefact(lbl, 'current_story',\
                                    'flow_story_select', 'stories')
    def viewCurrentTask(self,lbl, *largs): #IGNORE:W0613
        self.view_current_Artefact(lbl, 'current_task',\
                                    'flow_task_select', 'tasks')
    def view_current_Artefact(self,lbl,curr,flow_select, container):
        try:
            #get the controller for this artefact
            _c = self.controller.__getattribute__(curr)[0]
        except Exception: #IGNORE:W0703
            _c = Dummy()
            _c.Id = ''
        idu = None
        idu =  lbl.Id if isinstance(lbl, ArtefactController)\
                      else lbl._id #IGNORE:W0212          
        if _c.Id != idu:
            #set current artefact to the one selected
            self.__getattribute__(flow_select)\
            (self.artefacts[lbl._id][0])
                            #(self.__getattribute__(container)[lbl._id][0]) #IGNORE:W0212
            return #to avoid add then removing the same widget
        self.toggle_view_current_Artefact(_c.view)
    @property        
    def artefacts(self):
        return self.controller.artefacts
    @property
    def currentProjectView(self):
        return self.controller.currentProjectView
    @property
    def currentReleaseView(self):
        return self.controller.currentReleaseView
    @property
    def currentSprintView(self):
        return self.controller.currentSprintView
    @property
    def currentStoryView(self):
        return self.controller.currentStoryView
    @property
    def currentTaskView(self):
        return self.controller.currentTaskView
        
if __name__ == '__main__':
    mw = MTWindow()
    mw.size = scale_tuple(size,0.045)
    scale = .13
    size = scale_tuple(mw.size, scale)
    base_image = os.path.abspath(os.path.join(os.path.dirname(__file__),
                            '..',  '..', 'examples', 'framework','images'))
    coverflow = MTCoverFlow(size=(500,500))
    for fn in glob(os.path.join(base_image, '*.png')):
        button = MTToggleButton(label=os.path.basename(fn)) #MTImageButton(image=Loader.image(filename))
        coverflow.add_widget(button)
    
    dc = MyDragableContainer(coverflow, True)
    mw.add_widget(dc)
    runTouchApp()
    