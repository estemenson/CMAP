# -*- coding: utf-8 -*-
'''
Created on Aug 9, 2010

@author: stevenson
'''

from __future__                         import division
from __future__                         import absolute_import
from __future__                         import print_function
from __future__                         import unicode_literals

# This will cause the configuration to be established from the
# configuration files and the command line. It will also setup
# the asynchronous handling systems for communication with the
# repository and the collaboration server
from agileConfig                        import Config, AsyncHandler
from async                              import ON_GITHUBNOTIFICATION
try:
    Log = Config().log.logger
except Exception: #IGNORE:W0703
    from petaapan.utilities.console_logger\
                                        import ConsoleLogger
    Log = ConsoleLogger('AgiMan')
    
    
# Gives access to the StoryApp controller from anywhere in the application
_storyapp_singleton = None 
def Storyapp(): return _storyapp_singleton

import os.path


from random                             import choice
from glob                               import glob
from cmap.tools.classTools              import Dummy
from cmap.tools.myTools                 import get_min_screen_size#, scale_tuple
from pymt.utils                         import curry
from cmap.view.stories.storyViews       import pixels, minimal_size
from cmap.gestures.myGestures           import myGestures
from cmap.gestures.NewGestures          import get_and_or_store_gesture
from pymt.ui.colors                     import css_add_sheet
from cmap.tools.capture                 import MyCaptureWidget
from pygame.display                     import set_caption

from cmap.model.projectModel            import ProjectModel
from cmap.model.releaseModel            import ReleaseModel
from cmap.model.sprintModel             import SprintModel
from cmap.model.storyModel              import StoryModel
from cmap.model.taskModel               import TaskModel

from cmap.view.projects.projectViews    import ProjectMinView, ProjectView
from cmap.view.releases.releaseViews    import ReleaseMinView, ReleaseView
from cmap.view.sprints.sprintViews      import SprintView, SprintMinView
from cmap.view.stories.storyViews       import StoryView, MinStoryView
from cmap.view.tasks.taskViews          import TaskView, TaskMinView

from cmap.controller.basicControllers   import ArtefactController
from cmap.controller.projectController  import ProjectController
from cmap.controller.releaseController  import ReleaseController
from cmap.controller.sprintController   import SprintController
from cmap.controller.storyController    import StoryController
from cmap.controller.taskController     import TaskController

size = get_min_screen_size()


GestureCSS = '''
.gesturecss {
    bg-color: rgba(185,211,238, 255);
    border-color: rgb(100, 100, 220);
    border-width: 20;
    draw-border: 1;    
}
'''
css_add_sheet(GestureCSS)
        kwargs['view_type'] = ProjectView
        kwargs['mini_view_type'] = ProjectMinView
        kwargs['get_artefact'] = 'newProject'
        kwargs['model'] = ProjectModel
        kwargs['folder'] = 'projects'

BACKLOG,PROJECTS,RELEASES,SPRINTS,STORIES,TASKS = 0,1,2,3,4,5
artefact_types = {
                  {BACKLOG:'backlog'},
                  {PROJECTS:'projects','view_type':ProjectView, 
                   'mini_view_type':ProjectMinView, 'get_artefact':'newProject'
        kwargs['model'] = ProjectModel
        kwargs['folder'] = 'projects'},
        ,RELEASES:'releases',
                  SPRINTS:'sprints',STORIES:'stories',TASKS:'tasks'}

class StoryApp(object):
    def __init__(self, **kwargs):
        global _storyapp_singleton #IGNORE:W0603
        # Make ourself globally known
        _storyapp_singleton = self
        
        set_caption("Collaborative Multitouch Agile Planner")
        
        #call back for repository notifications
        AsyncHandler().set_handler(ON_GITHUBNOTIFICATION,
                                   self.on_github_notification)
        self.no_local_repo = Config().localRepoNotAvailable
        if not self.no_local_repo:
            AsyncHandler().save([],
                                'Cleanup any outstanding uncommitted edits')
        
        self.root_window = kwargs['root_window']
        #x and y ranges are used when calculating random positions for artefacts
        self._x_range = range(self.root_window.x, self.root_window.x + \
                              self.root_window.width - minimal_size[0])
        self._y_range = range(self.root_window.y, self.root_window.y + \
                              self.root_window.height - minimal_size[1])

        #self.backlog = {}
        self.artefacts = {}
        self.story_files = []
        #self.tasks = {}

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
        
        self.datastore = Config().datastore
        Log.debug('Path to repository: %s' % self.datastore)

        #enable gesture detection
        self.enable_gestures()
        self.xmlFiles = self.get_local_artefacts()
        
        #create the storyapp model and view
        
        
    def on_github_notification(self, ret):
        msg = ret[1]
        print("GOOGLE APP HOOK CCALLED ***************************************************************************")
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
            idu = btn.Id if isinstance(btn, ArtefactController)\
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
            idu = btn.Id if isinstance(btn, ArtefactController)\
                         else btn._id #IGNORE:W0212
            self.current_project = self.artefacts[idu]
            self.viewCurrentProject(btn)     
        except KeyError:
            #create new project
            lbl = self.new_project_pressed()
            if lbl is None: return
            self.current_project = self.artefacts[lbl.Id]
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
                if release in self.artefacts:
                    r = self.artefacts[release][0]
                    if r.ArtefactType != 'Release': continue
                    self.newRelease(r)
                else:
                    Log.debug('Project: %s found a release: %s not in releases' % \
                              (self.current_project[0].Name,release))
    def flow_release_select(self,btn):
        #make the selected release the active one
        try:
            idu = btn.Id if isinstance(btn, ArtefactController)\
                         else btn._id #IGNORE:W0212
            self.current_release = self.artefacts[idu]
            self.viewCurrentRelease(btn)
        except KeyError:
            #create new release
            lbl = self.new_release_pressed()
            if lbl is None: return
            self.current_release = self.artefacts[lbl.Id]
        #we need to populate the sprint flow with any sprints already
        #in the current release
        self.load_sprints()
        self.container_reset_children('sprint_flow')
        self.container_reset_children('story_flow')
        self.container_reset_children('task_flow')
        if self.current_release and self.current_release[0].Children:
            for sprint in self.current_release[0].Children:
                if sprint in self.artefacts.keys():
                    s = self.artefacts[sprint][0]
                    if s.ArtefactType != 'Sprint': continue
                    self.newSprint(s)
                else:
                    Log.debug('Release: %s found a sprint: %s not in sprints' % \
                              (self.current_release[0].Name,sprint))
    def flow_sprint_select(self,btn):
        #make the selected sprint the active one
        try:
            idu = btn.Id if isinstance(btn, ArtefactController)\
                         else btn._id #IGNORE:W0212
            self.current_sprint = self.artefacts[idu]
            self.viewCurrentSprint(btn)
        except KeyError:
            #create new sprint
            lbl = self.new_sprint_pressed()
            if lbl is None: return
            self.current_sprint = self.artefacts[lbl.Id]
        #we need to populate the story flow with any stories already
        #in the current sprint
        self.load_stories()
        self.container_reset_children('story_flow')
        self.container_reset_children('task_flow')
        if self.current_sprint and self.current_sprint[0].Children:
            for story in self.current_sprint[0].Children:
                if story in self.artefacts.keys():
                    s = self.artefacts[story][0]
                    if s.ArtefactType != 'Story': continue
                    self.newStory(s)
                else:
                    Log.debug('Sprint: %s found a story: %s not in stories' % \
                              (self.current_sprint[0].Name,story))
    def flow_story_select(self,btn):
        try:
            idu = btn.Id if isinstance(btn, ArtefactController)\
                         else btn._id #IGNORE:W0212
            self.current_story = self.artefacts[idu]
            self.viewCurrentStory(btn)
        except KeyError:
            #create new story
            lbl = self.new_story_pressed()
            if lbl is None: return
            if lbl.Parent:
                self.current_story = self.artefacts[lbl.Id]
        #we need to populate the task flow with any tasks already
        #in the current story
        self.load_tasks()
        self.container_reset_children('task_flow')
        if self.current_story and self.current_story[0].Children:
            for task in self.current_story[0].Children:
                if task in self.artefacts.keys():
                    t = self.artefacts[task][0]
                    if t.ArtefactType != 'Task': continue
                    self.newTask(t)
                else:
                    Log.debug('Story: %s found a task: %s not in tasks' % \
                              (self.current_story[0].Name,task))
    def flow_task_select(self,btn):
        try:
            idu = btn.Id if isinstance(btn, ArtefactController)\
                         else btn._id #IGNORE:W0212
            self.current_task = self.artefacts[idu]
            self.viewCurrentTask(btn)
        except KeyError:
            #create new task
            lbl = self.new_task_pressed()
            if lbl is None: return
            self.current_task = self.artefacts[lbl.Id]
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
    def new_backlog_pressed(self): # *largs
        _b = self.new_artefact_pressed(StoryController,
                                       'currentBacklogView',
                                       model=StoryModel,
                                       mini_view_type=MinStoryView,
                                       view_type=StoryView,
                                       get_artefact='newBacklog',
                                       folder='backlog')
        self.backlog[_b.Id] = (_b,{})
        return _b
    def new_project_pressed(self, *largs): #IGNORE:W0613
        _p = self.new_artefact_pressed(ProjectController,
                                       'currentProjectView',
                                       model=ProjectModel,
                                       mini_view_type=ProjectMinView,
                                       view_type=ProjectView,
                                       get_artefact='newProject')
        pobj = (_p, {})
        self.artefacts[_p.Id] = pobj
        self.current_project = pobj
        return _p
    def new_release_pressed(self, *largs): #IGNORE:W0613
        project = None if self.current_project is None \
                                        else self.current_project[0].Id
        if not project:
            return # Do not support releases in backlog now
        _r = self.new_artefact_pressed(ReleaseController,
                                       'currentReleaseView',
                                       project=project if project else None,
                                       model=ReleaseModel,
                                       view_type=ReleaseView,
                                       mini_view_type=ReleaseMinView,
                                       get_artefact='newRelease' if project\
                                                     else 'newBacklog',
                                       folder='releases' if project\
                                               else 'backlog')
        robj = (_r, {})
        self.artefacts[_r.Id] = robj
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
        _s = self.new_artefact_pressed(SprintController,
                                       'currentSprintView',
                                       p_artefact=release,
                                       model=SprintModel,
                                       view_type=SprintView,
                                       mini_view_type=SprintMinView,
                                       get_artefact='newSprint'\
                                                    if release or project\
                                                    else 'newBacklog',
                                       folder='sprints' if release or project\
                                              else 'backlog',
                                       release=release)
        sobj = (_s, {})
        self.artefacts[_s.Id] = sobj
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
        _s = self.new_artefact_pressed(StoryController,
                                       'currentStoryView',
                                        p_artefact=parent,
                                        project=project.Id if project else None,
                                        model=StoryModel,
                                        view_type=StoryView,
                                        mini_view_type=MinStoryView,
                                        get_artefact='newStory' if parent\
                                                      else 'newBacklog',
                                        folder='stories' if parent\
                                                else 'backlog')
        sobj = (_s, {})
        if sprint:
            self.current_sprint[0].Children = _s.Id
            _s.Parent = sprint.Id
            self.artefacts[_s.Id] = sobj
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
        _t = self.new_artefact_pressed(TaskController,
                                       'currentTaskView',
                                       p_artefact=parent,
                                       model=TaskModel,
                                       view_type=TaskView,
                                       mini_view_type=TaskMinView,
                                       get_artefact='newTask',
                                       folder='tasks')
        tobj = (_t, {})
        self.artefacts[_t.Id] = tobj
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
    def new_artefact_pressed(self,ctrl,view, **kwargs): # *largs
        _r = ctrl(self,None,**kwargs)
        self.__setattr__(view, _r.newDialog(minv=True))
        super(StoryApp,self).add_widget(self.__getattribute__(view))
        return _r 
    def getBacklog(self,defn,**kwargs):
        kwargs['view_type'] = StoryView
        kwargs['mini_view_type'] = MinStoryView
        kwargs['get_artefact'] = 'newBacklog'
        kwargs['model'] = StoryModel
        kwargs['folder'] = 'backlog'
        return self.getArtefact(defn, StoryController, **kwargs)
    def getProject(self,defn,**kwargs):
        kwargs['view_type'] = ProjectView
        kwargs['mini_view_type'] = ProjectMinView
        kwargs['get_artefact'] = 'newProject'
        kwargs['model'] = ProjectModel
        kwargs['folder'] = 'projects'
        return self.getArtefact(defn, ProjectController, **kwargs)
    def getRelease(self,defn,**kwargs):
        kwargs['view_type'] = ReleaseView
        kwargs['mini_view_type'] = ReleaseMinView
        kwargs['get_artefact'] = 'newRelease'
        kwargs['model'] = ReleaseModel
        kwargs['folder'] = 'releases'
        return self.getArtefact(defn, ReleaseController, **kwargs)
    def getSprint(self,defn,**kwargs):
        kwargs['view_type'] = SprintView
        kwargs['mini_view_type'] = SprintMinView
        kwargs['get_artefact'] = 'newSprint'
        kwargs['model'] = SprintModel
        kwargs['folder'] = 'sprints'
        return self.getArtefact(defn, SprintController, **kwargs)
    def getStory(self,defn,**kwargs):
        kwargs['view_type'] = StoryView
        kwargs['mini_view_type'] = MinStoryView
        kwargs['get_artefact'] = 'newStory'
        kwargs['model'] = StoryModel
        kwargs['folder'] = 'stories'
        return self.getArtefact(defn, StoryController, **kwargs)
    def getTask(self,defn,**kwargs):
        kwargs['view_type'] = TaskView
        kwargs['mini_view_type'] = TaskMinView
        kwargs['get_artefact'] = 'newTask'
        kwargs['model'] = TaskModel
        kwargs['folder'] = 'tasks'
        return self.getArtefact(defn, TaskController,**kwargs)
    def getArtefact(self,defn,ctrl,**kwargs):
        _p = kwargs.setdefault('controller', None)
        if _p is None:
            _p = ctrl(self,defn,**kwargs)
        return _p
    def remove_project_view(self,w):
        super(StoryApp,self).remove_widget(w)
    def newBacklog(self,ctrl):
        return self.add_new_artefact(ctrl, CONTAINERS_BACKLOG, 
                              'viewCurrentBacklog', self.backlog[ctrl.Id][1])
    def newProject(self,ctrl):
        return self.add_new_artefact(ctrl,
                                     CONTAINERS_PROJECT,
                                     'viewCurrentProject',
                                     self.artefacts[ctrl.Id][1])
    def newRelease(self,ctrl):
        return self.add_new_artefact(ctrl,
                                     CONTAINERS_RELEASE,
                                     'viewCurrentRelease',
                                     self.artefacts[ctrl.Id][1])
    def newSprint(self,ctrl):
        return self.add_new_artefact(ctrl,
                                     CONTAINERS_SPRINT,
                                     'viewCurrentSprint',
                                     self.artefacts[ctrl.Id][1])
    def newStory(self,ctrl):
        return self.add_new_artefact(ctrl,
                                     CONTAINERS_STORY, 
                                     'viewCurrentStory',
                                     self.artefacts[ctrl.Id][1])
    def newTask(self,ctrl):
        return self.add_new_artefact(ctrl,
                                     CONTAINERS_TASK,
                                     'viewCurrentTask',
                                     self.artefacts[ctrl.Id][1])
    def add_new_artefact(self, ctrl, container, callback, ret):
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
            _c = self.__getattribute__(curr)[0]
        except Exception: #IGNORE:W0703
            _c = Dummy()
            _c.Id = ''

        idu =  lbl.Id if isinstance(lbl, ArtefactController)\
                      else lbl._id #IGNORE:W0212          
        if _c.Id != idu:
            #set current artefact to the one selected
            self.__getattribute__(flow_select)\
                            (self.__getattribute__(container)[lbl._id][0]) #IGNORE:W0212
            return #to avoid add then removing the same widget
        _view = _c.view
        if _view in self.container.children:
            super(StoryApp,self).remove_widget(_view)
        else:
            super(StoryApp,self).add_widget(_view)
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
    def trash(self,artefact,atype=None):
        if atype is None:# or type is 'stories':
            btn = self.buttons[artefact.Id]
            lbl = self.labels[artefact.Id]
            self.backlog_list_layout.remove_widget(btn)
            self.story_flow.remove_widget(lbl)
            self.remove_widget(artefact)
            del self.artefacts[artefact.Id]
        else:
            if artefact.Id in self.Artefacts:
                dic = self.Artefacts[artefact.Id][1]
                for l in dic.keys():
                    self.__getattribute__(l).remove_widget(dic[l])
                del self.Artefacts[artefact.Id]
                super(StoryApp,self).remove_widget(artefact.view)
        return
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
        #close all the artefacts
        for a in self.artefacts.values():
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
    def Artefacts(self):
        return self.artefacts
    
        
if __name__ == '__main__':
    from pymt.ui.window import MTWindow
    from pymt.base import runTouchApp, stopTouchApp
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
    