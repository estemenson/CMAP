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
from cmap.controller.basicControllers import ArtifactController
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

GestureCSS = '''
.gesturecss {
    bg-color: rgba(185,211,238, 255);
    border-color: rgb(100, 100, 220);
    border-width: 20;
    draw-border: 1;    
}
'''
css_add_sheet(GestureCSS)
BACKLOG,PROJECTS,RELEASES,SPRINTS,STORIES,TASKS = 0,1,2,3,4,5
artifact_types = {BACKLOG:'backlog',PROJECTS:'projects',RELEASES:'releases',
                  SPRINTS:'sprints',STORIES:'stories',TASKS:'tasks'}
LABEL_NEW_PROJECT  = 'New\nProject...'
LABEL_NEW_RELEASE  = 'New\nRelease...'
LABEL_NEW_SPRINT   = 'New\nSprint...'
LABEL_NEW_STORY    = 'New\nStory...'
LABEL_NEW_TASK     = 'New\nTask...'
CONTAINERS_BACKLOG = ['backlog_list_layout', 'backlog_flow']
CONTAINERS_PROJECT = ['projects_flow']
CONTAINERS_RELEASE = ['release_flow']
CONTAINERS_SPRINT  = ['sprint_flow']
CONTAINERS_STORY   = ['story_flow']
CONTAINERS_TASK    = ['task_flow']

class StoryApp(MyInnerWindow):
    def __init__(self, **kwargs):
        global _storyapp_singleton #IGNORE:W0603
        # Make ourself globally known
        _storyapp_singleton = self
        super(StoryApp, self).__init__(**kwargs)
        set_caption("Collaborative Multitouch Agile Planner")
        AsyncHandler().set_handler(ON_GITHUBNOTIFICATION,
                                   self.on_github_notification)
        self.no_local_repo = Config().localRepoNotAvailable
        if not self.no_local_repo:
            AsyncHandler().save([],
                                'Cleanup any outstanding uncommitted edits')
        self.root_window = kwargs['root_window']
        self.canvas = None
        self.backlog_list_layout = MTGridLayout(rows=1)
        self._x_range = range(self.root_window.x, self.root_window.x + \
                              self.root_window.width - minimal_size[0])
        self._y_range = range(self.root_window.y, self.root_window.y + \
                              self.root_window.height - minimal_size[1])

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
        self.buttons = {}
        self.labels = {}
        self.backlog = {}
        self.artifacts = {}
        self.story_files = []
        self.tasks = {}
        self.backlog_flow_open = True
        self.projects_flow_open = True
        self.releases_flow_open = True
        self.story_flow_open = True
        self.sprint_flow_open = True
        self.task_flow_open = True
        self.current_backlog = None
        self.current_project = None
        self.current_release = None
        self.current_sprint = None
        self.current_story = None
        self.current_task = None
        self.currentProjectView = None
        self.currentReleaseView = None
        self.currentSprintView = None
        self.currentStoryView = None
        self.currentTaskView = None
        
        self.checked_for_releases = False
        self.checked_for_sprints = False
        self.checked_for_stories = False
        self.checked_for_tasks = False
        
        # Load the default image for buttons and cover flows
        path = os.path.join(os.getcwd(), 'data', 'ModelScribble.jpg')
        self._default_button_size = (100, 100)
        self._default_image = Loader.image(path)
        _sf_pos = (200,200)
        try:
            self.backlog_flow = MTCoverFlow(
                                      layout=MTGridLayout(spacing=10,rows=1),
                                      pos=_sf_pos,
                                      size=self._default_button_size,
                                      cover_spacing=20,
                                      cover_distance=115,
                                      thumbnail_size=self._default_button_size)
            self.backlog_flow.push_handlers(on_select=self.flow_backlog_select)
            self.backlog_flow.add_widget(self.createNewStoryButton())
        except Exception: #IGNORE:W0703
            Log.exception("Unable to create backlog cover flow")
            self.backlog_flow = MTGridLayout(rows=1, pos=_sf_pos)
            self.backlog_flow.add_widget(self.createNewStoryButton())
        try:
            self.projects_flow = MTCoverFlow(\
                                      layout=MTGridLayout(spacing=10,rows=1),
                                      pos=_sf_pos,
                                      size=self._default_button_size,
                                      cover_spacing=20,
                                      cover_distance=115,
                                      thumbnail_size=self._default_button_size)
            self.projects_flow.push_handlers(\
                                           on_select=self.flow_projects_select)
            self.projects_flow.add_widget(self.createNewProjectButton())
        except Exception: #IGNORE:W0703
            Log.exception("Unable to create project cover flow")
            self.projects_flow = MTGridLayout(rows=1, pos=_sf_pos)
        try:
            self.release_flow = MTCoverFlow(\
                                      layout=MTGridLayout(spacing=10,rows=1),
                                      pos=_sf_pos,
                                      size=self._default_button_size,
                                      cover_spacing=20,
                                      cover_distance=115,
                                      thumbnail_size=self._default_button_size)
            self.release_flow.push_handlers(\
                                            on_select=self.flow_release_select)
            self.release_flow.add_widget(self.createNewReleaseButton())
        except Exception: #IGNORE:W0703
            Log.exception("Unable to create release cover flow")
            self.release_flow = MTGridLayout(rows=1, pos=_sf_pos)
        try:
            self.sprint_flow = MTCoverFlow(\
                                      layout=MTGridLayout(spacing=10,rows=1),
                                      pos=_sf_pos,
                                      size=self._default_button_size,
                                      cover_spacing=20,
                                      cover_distance=115,
                                      thumbnail_size=self._default_button_size)
            self.sprint_flow.push_handlers(\
                                            on_select=self.flow_sprint_select)
            self.sprint_flow.add_widget(self.createNewSprintButton())
        except Exception: #IGNORE:W0703
            Log.exception("Unable to create sprint cover flow")
            self.sprint_flow = MTGridLayout(rows=1, pos=_sf_pos)
        try:
            self.story_flow = MTCoverFlow(\
                                      layout=MTGridLayout(spacing=10,rows=1),
                                      pos=_sf_pos,
                                      size=self._default_button_size,
                                      cover_spacing=20,
                                      cover_distance=115,
                                      thumbnail_size=self._default_button_size)
            self.story_flow.push_handlers(on_select=self.flow_story_select)
            self.story_flow.add_widget(self.createNewStoryButton())
        except Exception: #IGNORE:W0703
            Log.exception("Unable to create story cover flow")
            self.story_flow = MTGridLayout(rows=1, pos=_sf_pos)
        try:
            self.task_flow = MTCoverFlow(\
                                      layout=MTGridLayout(spacing=10,rows=1),
                                      pos=_sf_pos,
                                      size=self._default_button_size,
                                      cover_spacing=20,
                                      cover_distance=115,
                                      thumbnail_size=self._default_button_size)
            self.task_flow.push_handlers(on_select=self.flow_task_select)
            self.task_flow.add_widget(self.createNewTaskButton())
        except Exception: #IGNORE:W0703
            Log.exception("Unable to create task coverflow")
            self.task_flow = MTGridLayout(rows=1, pos=_sf_pos)
        #dragable containers for the flow objects so we can move them around 
        #the screen
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
        self.path = Config().datastore
        Log.debug('Path to repository: %s' % self.path)

        #enable gesture detection
        self.enable_gestures()
        self.canvas.add_widget(self.backlog_container)
        self.addMainControls()
        self.xmlFiles = self.get_local_artifacts()
        self.load_backlog()
        self.load_projects()
        #make sure no projects or stories are set as the current ones
        self.current_project = None
        self.current_story = None
        
    def on_github_notification(self, ret):
        msg = ret[1]
        for c in msg['commits']:
            for a in c['added']:
                Log.debug('%s added by %s' % (a, c['author']['name']))
            for m in c['modified']:
                Log.debug('%s modified by %s' % (m, c['author']['name']))
            for r in c['removed']:
                Log.debug('%s removed by %s' % (r, c['author']['name']))

        
    def flow_backlog_select(self,btn):
        #make the selected backlog item the active one
        try:
            idu = btn.Id if isinstance(btn, ArtifactController)\
                         else btn._id #IGNORE:W0212
            self.current_backlog = self.backlog[idu] 
            self.viewCurrentBacklog(btn)     
        except KeyError:
            #create new backlog story
            lbl = self.new_backlog_pressed()
            self.current_backlog = self.backlog[lbl.Id]
        self.current_story = self.current_backlog
        set_caption(self.current_backlog[0].Name)
    def flow_projects_select(self,btn):
        #make the selected project the active one
        try:
            idu = btn.Id if isinstance(btn, ArtifactController)\
                         else btn._id #IGNORE:W0212
            self.current_project = self.artifacts[idu]
            self.viewCurrentProject(btn)     
        except KeyError:
            #create new project
            lbl = self.new_project_pressed()
            if lbl is None: return
            self.current_project = self.artifacts[lbl.Id]
        set_caption(self.current_project[0].Name)
        #we need to populate the releases flow with any release 
        #in the current project
        self.load_releases()
        self.container_reset_children('release_flow')
        self.container_reset_children('sprint_flow')
        self.container_reset_children('story_flow')
        self.container_reset_children('task_flow')
        if self.current_project and self.current_project[0].Children:
            for release in self.current_project[0].Children:
                if release in self.artifacts:
                    r = self.artifacts[release][0]
                    if r.ArtifactType != 'Release': continue
                    self.newRelease(r)
                else:
                    Log.debug('Project: %s found a release: %s not in releases' % \
                              (self.current_project[0].Name,release))
    def flow_release_select(self,btn):
        #make the selected release the active one
        try:
            idu = btn.Id if isinstance(btn, ArtifactController)\
                         else btn._id #IGNORE:W0212
            self.current_release = self.artifacts[idu]
            self.viewCurrentRelease(btn)
        except KeyError:
            #create new release
            lbl = self.new_release_pressed()
            if lbl is None: return
            self.current_release = self.artifacts[lbl.Id]
        #we need to populate the sprint flow with any sprints already
        #in the current release
        self.load_sprints()
        self.container_reset_children('sprint_flow')
        self.container_reset_children('story_flow')
        self.container_reset_children('task_flow')
        if self.current_release and self.current_release[0].Children:
            for sprint in self.current_release[0].Children:
                if sprint in self.artifacts.keys():
                    s = self.artifacts[sprint][0]
                    if s.ArtifactType != 'Sprint': continue
                    self.newSprint(s)
                else:
                    Log.debug('Release: %s found a sprint: %s not in sprints' % \
                              (self.current_release[0].Name,sprint))
    def flow_sprint_select(self,btn):
        #make the selected sprint the active one
        try:
            idu = btn.Id if isinstance(btn, ArtifactController)\
                         else btn._id #IGNORE:W0212
            self.current_sprint = self.artifacts[idu]
            self.viewCurrentSprint(btn)
        except KeyError:
            #create new sprint
            lbl = self.new_sprint_pressed()
            if lbl is None: return
            self.current_sprint = self.artifacts[lbl.Id]
        #we need to populate the story flow with any stories already
        #in the current sprint
        self.load_stories()
        self.container_reset_children('story_flow')
        self.container_reset_children('task_flow')
        if self.current_sprint and self.current_sprint[0].Children:
            for story in self.current_sprint[0].Children:
                if story in self.artifacts.keys():
                    s = self.artifacts[story][0]
                    if s.ArtifactType != 'Story': continue
                    self.newStory(s)
                else:
                    Log.debug('Sprint: %s found a story: %s not in stories' % \
                              (self.current_sprint[0].Name,story))
    def flow_story_select(self,btn):
        try:
            idu = btn.Id if isinstance(btn, ArtifactController)\
                         else btn._id #IGNORE:W0212
            self.current_story = self.artifacts[idu]
            self.viewCurrentStory(btn)
        except KeyError:
            #create new story
            lbl = self.new_story_pressed()
            if lbl is None: return
            if lbl.Parent:
                self.current_story = self.artifacts[lbl.Id]
        #we need to populate the task flow with any tasks already
        #in the current story
        self.load_tasks()
        self.container_reset_children('task_flow')
        if self.current_story and self.current_story[0].Children:
            for task in self.current_story[0].Children:
                if task in self.artifacts.keys():
                    t = self.artifacts[task][0]
                    if t.ArtifactType != 'Task': continue
                    self.newTask(t)
                else:
                    Log.debug('Story: %s found a task: %s not in tasks' % \
                              (self.current_story[0].Name,task))
    def flow_task_select(self,btn):
        try:
            idu = btn.Id if isinstance(btn, ArtifactController)\
                         else btn._id #IGNORE:W0212
            self.current_task = self.artifacts[idu]
            self.viewCurrentTask(btn)
        except KeyError:
            #create new task
            lbl = self.new_task_pressed()
            if lbl is None: return
            self.current_task = self.artifacts[lbl.Id]
    def _flow_pressed(self, flag, widget, *largs): #IGNORE:W0613
        _flag =  not self.__getattribute__(flag)
        self.__setattr__(flag, _flag)
        if _flag:
            super(StoryApp,self).remove_widget(widget)
        else:
            widget.pos = self.get_new_random_position()
            super(StoryApp,self).add_widget(widget)
    def get_new_random_position(self):
        return (choice(self._x_range),choice(self._y_range))
    def enable_gestures(self):
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
            pass
        self.canvas = MTScatter(cls='gesturecss') 
        self.canvas.size = self.root_window.size
        self.canvas.pos = (0,0)
        super(StoryApp,self).add_widget(self.canvas)
        capture = MyCaptureWidget(gdb, self)
        capture.size = self.canvas.size
        self.canvas.add_widget(capture)
    def get_local_artifacts(self):
        '''
        Loads the file names of all local artifacts into a dictionary
        keyed on artifact type
        '''
        Log.debug('path: %s' % self.path)
        xmlFiles = {}
        for atype in artifact_types.values():
            xmlFiles[atype] = []
            files = glob(os.path.join(self.path, atype, '*.xml'))
            for f in files:
                Log.debug('xmlFile: %s' % f)
                xmlFiles[atype].append(f)
        return xmlFiles
        
    def load_projects(self):
        for f in self.xmlFiles[artifact_types[PROJECTS]]:
            Log.debug('load only xmlFile: %s' % f)
            
            p = self.getProject(f,model=ProjectModel,
                    get_artifact='newProject',
                    name=os.path.splitext(os.path.basename(f))[0])
            self.artifacts[p.Id] = (p,{})
            self.newProject(p)
    def load_releases(self):
        if self.checked_for_releases: return
        self.checked_for_releases = True
        for f in self.xmlFiles[artifact_types[RELEASES]]:
            Log.debug('only loading release %s' % f)
            r = self.getRelease(f, model=ReleaseModel,
                    get_artifact='newRelease',name=\
                os.path.splitext(os.path.basename(f))[0])
            self.artifacts[r.Id] = (r,{})
            self.newRelease(r)
    def load_sprints(self):
        if self.checked_for_sprints: return
        self.checked_for_sprints = True
        for f in self.xmlFiles[artifact_types[SPRINTS]]:
            Log.debug('only loading sprint %s' % f)
            s = self.getSprint(f, model=SprintModel, name=\
                os.path.splitext(os.path.basename(f))[0])
            self.artifacts[s.Id] = (s, {})
            self.newSprint(s)
    def load_backlog(self):
        Log.debug('BackLog loading:')
        for f in self.xmlFiles[artifact_types[BACKLOG]]:
            b = self.getBacklog(f)
            self.backlog[b.Id] = (b,{})
            self.newBacklog(b)
        Log.debug('Backlog Done loading')
    def load_stories(self):
        if self.checked_for_stories: return
        self.checked_for_stories = True
        Log.debug('Stories loading: ')
        for f in self.xmlFiles[artifact_types[STORIES]]:
            Log.debug('only loading story %s' % f)
            s = self.getStory(f)
            self.artifacts[s.Id] = (s ,{})
            self.newStory(s)
        Log.debug('Stories Done loading')
    def load_tasks(self):
        if self.checked_for_tasks: return
        self.checked_for_tasks = True
        for f in self.xmlFiles[artifact_types[TASKS]]:
            Log.debug('%s' % f)
            t = self.getTask(f, name=\
                os.path.splitext(os.path.basename(f))[0])
            self.artifacts[t.Id] = (t, {})
            self.newTask(t)


    def createNewProjectButton(self):
        return self.create_button(LABEL_NEW_PROJECT,curry(\
                                                    self.new_project_pressed))
    def createNewReleaseButton(self):
        return self.create_button(LABEL_NEW_RELEASE,curry(\
                                                    self.new_release_pressed))
    def createNewSprintButton(self):
        return self.create_button(LABEL_NEW_SPRINT, curry(\
                                                    self.new_sprint_pressed))
    def createNewStoryButton(self):
        return self.create_button(LABEL_NEW_STORY,curry(self.new_story_pressed))
    def createNewTaskButton(self):
        return self.create_button(LABEL_NEW_TASK,curry(self.new_task_pressed))
    def new_backlog_pressed(self): # *largs
        _b = self.new_artifact_pressed(StoryController,
                                       'currentBacklogView',
                                       model=StoryModel,
                                       mini_view_type=MinStoryView,
                                       view_type=StoryView,
                                       get_artifact='newBacklog',
                                       folder='backlog')
        self.backlog[_b.Id] = (_b,{})
        return _b
    def new_project_pressed(self, *largs): #IGNORE:W0613
        _p = self.new_artifact_pressed(ProjectController,
                                       'currentProjectView',
                                       model=ProjectModel,
                                       mini_view_type=ProjectMinView,
                                       view_type=ProjectView,
                                       get_artifact='newProject')
        pobj = (_p, {})
        self.artifacts[_p.Id] = pobj
        self.current_project = pobj
        return _p
    def new_release_pressed(self, *largs): #IGNORE:W0613
        project = None if self.current_project is None \
                                        else self.current_project[0].Id
        if not project:
            return # Do not support releases in backlog now
        _r = self.new_artifact_pressed(ReleaseController,
                                       'currentReleaseView',
                                       project=project if project else None,
                                       model=ReleaseModel,
                                       view_type=ReleaseView,
                                       mini_view_type=ReleaseMinView,
                                       get_artifact='newRelease' if project\
                                                     else 'newBacklog',
                                       folder='releases' if project\
                                               else 'backlog')
        robj = (_r, {})
        self.artifacts[_r.Id] = robj
        if project:
            self.current_project[0].Children = _r.Id
            _r.Parent = project
            self.current_release = robj
        return _r
    def new_sprint_pressed(self, *largs): #IGNORE:W0613
        project = None if self.current_project is None \
                                        else self.current_project[0]
        release = None if self.current_release is None \
                        else self.current_release[0].Id
        if not release:
            return # No appropriate parent
        _s = self.new_artifact_pressed(SprintController,
                                       'currentSprintView',
                                       p_artifact=release,
                                       model=SprintModel,
                                       view_type=SprintView,
                                       mini_view_type=SprintMinView,
                                       get_artifact='newSprint'\
                                                    if release or project\
                                                    else 'newBacklog',
                                       folder='sprints' if release or project\
                                              else 'backlog',
                                       release=release)
        sobj = (_s, {})
        self.artifacts[_s.Id] = sobj
        if release:
            self.current_release[0].Children = _s.Id
            _s.Parent = release
            self.current_sprint = sobj
        return _s
    def new_story_pressed(self, *largs): #IGNORE:W0613
        project = None if self.current_project is None \
                                        else self.current_project[0]
        sprint = None if self.current_sprint is None \
                        else self.current_sprint[0]
        parent = sprint if sprint else project
        _s = self.new_artifact_pressed(StoryController,
                                       'currentStoryView',
                                        p_artifact=parent,
                                        project=project.Id if project else None,
                                        model=StoryModel,
                                        view_type=StoryView,
                                        mini_view_type=MinStoryView,
                                        get_artifact='newStory' if parent\
                                                      else 'newBacklog',
                                        folder='stories' if parent\
                                                else 'backlog')
        sobj = (_s, {})
        if sprint:
            self.current_sprint[0].Children = _s.Id
            _s.Parent = sprint.Id
            self.artifacts[_s.Id] = sobj
            self.current_story = sobj
        elif not parent:
            self.backlog[_s.Id] = sobj
        _s.register_observer(self)
        return _s
    def new_task_pressed(self, *largs): #IGNORE:W0613
        story = None if self.current_story is None \
                        else self.current_story[0]
        sprint = None if self.current_sprint is None \
                         else self.current_sprint[0]
        parent = None
        if story:
            parent = story
        elif sprint:
            parent = sprint
        if not parent:
            return # No appropriate parent
        _t = self.new_artifact_pressed(TaskController,
                                       'currentTaskView',
                                       p_artifact=parent,
                                       model=TaskModel,
                                       view_type=TaskView,
                                       mini_view_type=TaskMinView,
                                       get_artifact='newTask',
                                       folder='tasks')
        tobj = (_t, {})
        self.artifacts[_t.Id] = tobj
        if story:
            story.Children = _t.Id
            _t.Parent = story.Id
        elif sprint:
            sprint.Children = _t.Id
            _t.Parent = sprint.Id
        else:    
            self.backlog[_t.Id] = tobj
        if story or sprint:
            self.current_task = tobj
        return _t
    def new_artifact_pressed(self,ctrl,view, **kwargs): # *largs
        _r = ctrl(self,None,**kwargs)
        self.__setattr__(view, _r.newDialog(minv=True))
        super(StoryApp,self).add_widget(self.__getattribute__(view))
        return _r 
    def getBacklog(self,defn,**kwargs):
        kwargs['view_type'] = StoryView
        kwargs['mini_view_type'] = MinStoryView
        kwargs['get_artifact'] = 'newBacklog'
        kwargs['model'] = StoryModel
        kwargs['folder'] = 'backlog'
        return self.getArtifact(defn, StoryController, **kwargs)
    def getProject(self,defn,**kwargs):
        kwargs['view_type'] = ProjectView
        kwargs['mini_view_type'] = ProjectMinView
        kwargs['get_artifact'] = 'newProject'
        kwargs['model'] = ProjectModel
        kwargs['folder'] = 'projects'
        return self.getArtifact(defn, ProjectController, **kwargs)
    def getRelease(self,defn,**kwargs):
        kwargs['view_type'] = ReleaseView
        kwargs['mini_view_type'] = ReleaseMinView
        kwargs['get_artifact'] = 'newRelease'
        kwargs['model'] = ReleaseModel
        kwargs['folder'] = 'releases'
        return self.getArtifact(defn, ReleaseController, **kwargs)
    def getSprint(self,defn,**kwargs):
        kwargs['view_type'] = SprintView
        kwargs['mini_view_type'] = SprintMinView
        kwargs['get_artifact'] = 'newSprint'
        kwargs['model'] = SprintModel
        kwargs['folder'] = 'sprints'
        return self.getArtifact(defn, SprintController, **kwargs)
    def getStory(self,defn,**kwargs):
        kwargs['view_type'] = StoryView
        kwargs['mini_view_type'] = MinStoryView
        kwargs['get_artifact'] = 'newStory'
        kwargs['model'] = StoryModel
        kwargs['folder'] = 'stories'
        return self.getArtifact(defn, StoryController, **kwargs)
    def getTask(self,defn,**kwargs):
        kwargs['view_type'] = TaskView
        kwargs['mini_view_type'] = TaskMinView
        kwargs['get_artifact'] = 'newTask'
        kwargs['model'] = TaskModel
        kwargs['folder'] = 'tasks'
        return self.getArtifact(defn, TaskController,**kwargs)
    def getArtifact(self,defn,ctrl,**kwargs):
        _p = kwargs.setdefault('controller', None)
        if _p is None:
            _p = ctrl(self,defn,**kwargs)
        return _p
    def remove_project_view(self,w):
        super(StoryApp,self).remove_widget(w)
    def newBacklog(self,ctrl):
        return self.add_new_artifact(ctrl, CONTAINERS_BACKLOG, 
                              'viewCurrentBacklog', self.backlog[ctrl.Id][1])
    def newProject(self,ctrl):
        return self.add_new_artifact(ctrl,
                                     CONTAINERS_PROJECT,
                                     'viewCurrentProject',
                                     self.artifacts[ctrl.Id][1])
    def newRelease(self,ctrl):
        return self.add_new_artifact(ctrl,
                                     CONTAINERS_RELEASE,
                                     'viewCurrentRelease',
                                     self.artifacts[ctrl.Id][1])
    def newSprint(self,ctrl):
        return self.add_new_artifact(ctrl,
                                     CONTAINERS_SPRINT,
                                     'viewCurrentSprint',
                                     self.artifacts[ctrl.Id][1])
    def newStory(self,ctrl):
        return self.add_new_artifact(ctrl,
                                     CONTAINERS_STORY, 
                                     'viewCurrentStory',
                                     self.artifacts[ctrl.Id][1])
    def newTask(self,ctrl):
        return self.add_new_artifact(ctrl,
                                     CONTAINERS_TASK,
                                     'viewCurrentTask',
                                     self.artifacts[ctrl.Id][1])
    def add_new_artifact(self, ctrl, container, callback, ret):
        for c in container:
            _lbl = MyImageButton(id=ctrl.Id, size=self._default_button_size,
                                 image=self._default_image)
            self.check_btn_width(_lbl)
            _lbl.push_handlers(on_press=curry(self.__getattribute__(callback), 
                                                                        _lbl))
            self.__getattribute__(c).add_widget(_lbl)
            ret[c] = _lbl
        return ret
            
    def viewCurrentBacklog(self,lbl, *largs): #IGNORE:W0613
        self.view_current_Artifact(lbl, 'current_backlog',\
                                    'flow_backlog_select', 'backlog')
    def viewCurrentProject(self,lbl, *largs): #IGNORE:W0613
        self.view_current_Artifact(lbl, 'current_project',\
                                    'flow_projects_select', 'projects')
    def viewCurrentRelease(self,lbl, *largs): #IGNORE:W0613
        self.view_current_Artifact(lbl, 'current_release',\
                                    'flow_release_select', 'releases')
    def viewCurrentSprint(self,lbl, *largs): #IGNORE:W0613
        self.view_current_Artifact(lbl, 'current_sprint',\
                                    'flow_sprint_select', 'sprints')
    def viewCurrentStory(self,lbl, *largs): #IGNORE:W0613
        self.view_current_Artifact(lbl, 'current_story',\
                                    'flow_story_select', 'stories')
    def viewCurrentTask(self,lbl, *largs): #IGNORE:W0613
        self.view_current_Artifact(lbl, 'current_task',\
                                    'flow_task_select', 'tasks')
    def view_current_Artifact(self,lbl,curr,flow_select, container):
        try:
            _c = self.__getattribute__(curr)[0]
        except Exception: #IGNORE:W0703
            _c = Dummy()
            _c.Id = ''

        idu =  lbl.Id if isinstance(lbl, ArtifactController)\
                      else lbl._id #IGNORE:W0212          
        if _c.Id != idu:
            #set current artifact to the one selected
            self.__getattribute__(flow_select)\
                            (self.__getattribute__(container)[lbl._id][0]) #IGNORE:W0212
            return #to avoid add then removing the same widget
        _view = _c.view
        if _view in self.container.children:
            super(StoryApp,self).remove_widget(_view)
        else:
            super(StoryApp,self).add_widget(_view)
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
    def createNewBacklogFlowButton(self):
        return self.create_button('Browse\nBacklog...',
                                  curry(self._flow_pressed,\
                        'backlog_flow_open',self.dragable_backlog_flow))
    def createNewProjectFlowButton(self):
        return self.create_button('Browse\nProjects...',\
                                  curry(self._flow_pressed,\
                        'projects_flow_open',self.dragable_project_flow))
    def createNewReleasesFlowButton(self):
        return self.create_button('Browse\nReleases...',
                                  curry(self._flow_pressed,\
                        'releases_flow_open',self.dragable_release_flow))
    def createNewSprintFlowButton(self):
        return self.create_button('Browse\nSprints...',
                                  curry(self._flow_pressed,\
                        'sprint_flow_open',self.dragable_sprint_flow))
    def createNewStoryFlowButton(self):
        return self.create_button('Browse\nStories...', 
            curry(self._flow_pressed,\
                        'story_flow_open',self.dragable_story_flow))
    def createNewTaskFlowButton(self):
        return self.create_button('Browse\nTasks...',
                                  curry(self._flow_pressed,\
                        'task_flow_open',self.dragable_task_flow))
    def create_button(self,label,callback):#,flag=None,widget=None):
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
    def update_story_btn_name(self,story):
        idu = story.Id
        btn = self.buttons[idu]
        if btn.id == idu:
            btn.label = story.Name
            self.check_btn_width(btn)
        return
    def trash(self,artifact,atype=None):
        if atype is None:# or type is 'stories':
            btn = self.buttons[artifact.Id]
            lbl = self.labels[artifact.Id]
            self.backlog_list_layout.remove_widget(btn)
            self.story_flow.remove_widget(lbl)
            self.remove_widget(artifact)
            del self.artifacts[artifact.Id]
        else:
            if artifact.Id in self.Artifacts:
                dic = self.Artifacts[artifact.Id][1]
                for l in dic.keys():
                    self.__getattribute__(l).remove_widget(dic[l])
                del self.Artifacts[artifact.Id]
                super(StoryApp,self).remove_widget(artifact.view)
        return
    def check_btn_width(self,btn):
        _label = btn.label
        _w = int(len(_label) *pixels)
        if _w > btn.width:
            if not btn.multiline:
                btn.multiline = True
            btn.label = '\n'.join(_label.split('-'))
    def list_button_pressed(self, btn):
        ctrl = self.backlog[btn.id][0]
        view = ctrl.view
        if view not in self.container.children:
            super(StoryApp,self).add_widget(view)
        else: ctrl.app_btn_pressed()
    def fullscreen(self, *largs, **kwargs):
        super(StoryApp,self).fullscreen()
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
    def unfullscreen(self, *largs, **kwargs):
        self.root_window.remove_widget(self)
        stopTouchApp()
        Log.info('Closing CMAP application')
    def close(self,touch=None):
        #close all the artifacts
        for a in self.artifacts.values():
            a[0].close()
        for b in self.backlog.values():
            b[0].close()
        self.add_to_git()
        AsyncHandler().shutdown()
        super(StoryApp, self).close(touch)
    def add_to_git(self):
        AsyncHandler().save(None, 'Commit session edits')    
    def container_reset_children(self,container):
        f = self.__getattribute__(container)
        x = len(f.children) -1
        while x > 0:
            w = f.children[x]
            f.remove_widget(w) 
            x = len(f.children) -1
    
    @property        
    def Artifacts(self):
        return self.artifacts
    
        
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
    