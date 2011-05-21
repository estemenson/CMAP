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
from cmap.model.storyappModel import StoryAppModel
from cmap.view.storyappView import StoryAppView
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

#size = get_min_screen_size()
BACKLOG,PROJECTS,RELEASES,SPRINTS,STORIES,TASKS = 'backlog','projects',\
                                        'releases','sprints','stories','tasks'
artefact_types = {
    BACKLOG:
        {'type':BACKLOG,'view_type':StoryView, 'mini_view_type':MinStoryView, 
         'get_artefact':'newBacklog', 'model': StoryModel,
         'container':['backlog_list_layout', 'backlog_flow'], 
         'viewCurrent':'viewCurrentBacklog', 'controller':StoryController, 
         'current':'current_backlog'},
    PROJECTS:
        {'type':PROJECTS,'view_type':ProjectView, 
         'mini_view_type':ProjectMinView, 'get_artefact':'newProject',
         'model': ProjectModel,'container':['projects_flow'], 
         'viewCurrent':'viewCurrentProject','callback':'flow_projects_select', 
         'controller':ProjectController, 'current':'current_project'},
    RELEASES:
        {'type':RELEASES,'view_type':ReleaseView, 
         'mini_view_type':ReleaseMinView, 'get_artefact':'newRelease',
         'model': ReleaseModel,'container':['release_flow'], 
         'viewCurrent':'viewCurrentRelease','callback':'flow_release_select', 
         'controller':ReleaseController, 'current':'current_release'},
    SPRINTS:
        {'type':SPRINTS,'view_type':SprintView, 'mini_view_type':SprintMinView,
         'get_artefact':'newSprint', 'model': SprintModel,
         'container':['sprint_flow'],'viewCurrent':'viewCurrentSprint',
         'callback':'flow_sprint_select','controller':SprintController, 
         'current':'current_sprint'},
    STORIES:
        {'type':STORIES,'view_type':StoryView, 'mini_view_type':MinStoryView, 
         'get_artefact':'newStory', 'model': StoryModel,
         'container':['story_flow'], 'callback':'flow_task_select', 
        'viewCurrent':'viewCurrentStory', 'controller':StoryController, 
        'current':'current_story'},
    TASKS:
        {'type':TASKS,'view_type':TaskView, 'mini_view_type':TaskMinView, 
         'get_artefact':'newTask', 'model': TaskModel,'container':['task_flow'], 
         'viewCurrent':'viewCurrentTask','callback':'flow_task_select',
         'controller':TaskController, 'current':'current_task'}
    }

class StoryApp(object):
    def __init__(self, **kwargs):
        global _storyapp_singleton #IGNORE:W0603
        # Make ourself globally known
        _storyapp_singleton = self
        
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

        self.datastore = Config().datastore
        Log.debug('Path to repository: %s' % self.datastore)

        #create the storyapp model and view
        self.view = StoryAppView(self, **kwargs)
        self.model = StoryAppModel(self)

    def add_current_aretfact(self, type, artefact):
        type = artefact_types[type]
        idu  = None
        try:
            #object exists get a reference
            idu = artefact.Id if isinstance(artefact, ArtefactController)\
                         else artefact._id #IGNORE:W0212
        except KeyError:
            #create a new artefact
            id = self.new_artefact().Id
        if not idu:
            #add artefact to the view
            id = idu
            self.view.view_current_Artefact(artefact, type['current'],
                                            type['callback'], type['type'] )     
        #set the current artefact (appends to the list)
        self.__setattr__(type['current'], self.artefacts[id])
        return id
    def new_artefact(self,type,**kwargs): # *largs
        _r = type['controller'](self,None,**kwargs)
        view = type['viewCurrent']
        self.__setattr__(view, _r.newDialog(minv=True))
        self.view.add_artefact(view)
        return _r 

#    def load_projects(self):
#        for f in self.xmlFiles[artefact_types[PROJECTS]]:
#            Log.debug('load only xmlFile: %s' % f)
#            
#            p = self.getProject(f,model=ProjectModel,
#                    get_artefact='newProject',
#                    name=os.path.splitext(os.path.basename(f))[0])
#            self.artefacts[p.Id] = (p,{})
#            self.newProject(p)
#    def load_sprints(self):
#        if self.checked_for_sprints: return
#        self.checked_for_sprints = True
#        for f in self.xmlFiles[artefact_types[SPRINTS]]:
#            Log.debug('only loading sprint %s' % f)
#            s = self.getSprint(f, model=SprintModel, name=\
#                os.path.splitext(os.path.basename(f))[0])
#            self.artefacts[s.Id] = (s, {})
#            self.newSprint(s)
#    def load_backlog(self):
#        Log.debug('BackLog loading:')
#        for f in self.xmlFiles[artefact_types[BACKLOG]]:
#            b = self.getBacklog(f)
#            self.artefacts[b.Id] = (b,{})
#            self.newBacklog(b)
#        Log.debug('Backlog Done loading')
#    def load_stories(self):
#        if self.checked_for_stories: return
#        self.checked_for_stories = True
#        Log.debug('Stories loading: ')
#        for f in self.xmlFiles[artefact_types[STORIES]]:
#            Log.debug('only loading story %s' % f)
#            s = self.getStory(f)
#            self.artefacts[s.Id] = (s ,{})
#            self.newStory(s)
#        Log.debug('Stories Done loading')
#    def load_tasks(self):
#        if self.checked_for_tasks: return
#        self.checked_for_tasks = True
#        for f in self.xmlFiles[artefact_types[TASKS]]:
#            Log.debug('%s' % f)
#            t = self.getTask(f, name=\
#                os.path.splitext(os.path.basename(f))[0])
#            self.artefacts[t.Id] = (t, {})
#            self.newTask(t)
    def load_children(self,id, type):
        for f in self.xmlFiles[artefact_types[type]]:
            Log.debug('only loading %s %s' % (type,f))
            kwargs = {
                'view_type':artefact_types[type]['view_type'],
                'mini_view_type':artefact_types[type]['mini_view_type'],
                'get_artefact':artefact_types[type]['get_artefact'],
                'model':artefact_types[type]['model'],
                'type':artefact_types[type][type],
                'name':os.path.splitext(os.path.basename(f))[0],
                'file':f,
                'controller':artefact_types[type]['controller']
            }
            r = self.getArtefact(**kwargs)
            self.artefacts[r.Id] = (r,{})
            artefact_types[type]['get_artefact'](self, r)
                
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

        
#    def flow_backlog_select(self,btn):
#        #make the selected backlog item the active one
#        try:
#            idu = btn.Id if isinstance(btn, ArtefactController)\
#                         else btn._id #IGNORE:W0212
#            self.current_backlog = self.artefacts[idu] 
#            self.viewCurrentBacklog(btn)     
#        except KeyError:
#            #create new backlog story
#            lbl = self.new_backlog_pressed()
#            self.current_backlog = self.artefacts[lbl.Id]
#        self.current_story = self.current_backlog
#        set_caption(self.current_backlog[0].Name)
#    def flow_projects_select(self,btn):
#        #make the selected project the active one
#        try:
#            idu = btn.Id if isinstance(btn, ArtefactController)\
#                         else btn._id #IGNORE:W0212
#            self.current_project = self.artefacts[idu]
#            self.viewCurrentProject(btn)     
#        except KeyError:
#            #create new project
#            lbl = self.new_project_pressed()
#            if lbl is None: return
#            self.current_project = self.artefacts[lbl.Id]
#        set_caption(self.current_project[0].Name)
#        #we need to populate the releases flow with any release 
#        #in the current project
#        self.load_releases()
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
#    def flow_release_select(self,btn):
#        #make the selected release the active one
#        try:
#            idu = btn.Id if isinstance(btn, ArtefactController)\
#                         else btn._id #IGNORE:W0212
#            self.current_release = self.artefacts[idu]
#            self.viewCurrentRelease(btn)
#        except KeyError:
#            #create new release
#            lbl = self.new_release_pressed()
#            if lbl is None: return
#            self.current_release = self.artefacts[lbl.Id]
#        #we need to populate the sprint flow with any sprints already
#        #in the current release
#        self.load_sprints()
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
#    def flow_sprint_select(self,btn):
#        #make the selected sprint the active one
#        try:
#            idu = btn.Id if isinstance(btn, ArtefactController)\
#                         else btn._id #IGNORE:W0212
#            self.current_sprint = self.artefacts[idu]
#            self.viewCurrentSprint(btn)
#        except KeyError:
#            #create new sprint
#            lbl = self.new_sprint_pressed()
#            if lbl is None: return
#            self.current_sprint = self.artefacts[lbl.Id]
#        #we need to populate the story flow with any stories already
#        #in the current sprint
#        self.load_stories()
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
#    def flow_story_select(self,btn):
#        try:
#            idu = btn.Id if isinstance(btn, ArtefactController)\
#                         else btn._id #IGNORE:W0212
#            self.current_story = self.artefacts[idu]
#            self.viewCurrentStory(btn)
#        except KeyError:
#            #create new story
#            lbl = self.new_story_pressed()
#            if lbl is None: return
#            if lbl.Parent:
#                self.current_story = self.artefacts[lbl.Id]
#        #we need to populate the task flow with any tasks already
#        #in the current story
#        self.load_tasks()
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
#    def flow_task_select(self,btn):
#        try:
#            idu = btn.Id if isinstance(btn, ArtefactController)\
#                         else btn._id #IGNORE:W0212
#            self.current_task = self.artefacts[idu]
#            self.viewCurrentTask(btn)
#        except KeyError:
#            #create new task
#            lbl = self.new_task_pressed()
#            if lbl is None: return
#            self.current_task = self.artefacts[lbl.Id]
#    def _flow_pressed(self, flag, widget, *largs): #IGNORE:W0613
#        _flag =  not self.__getattribute__(flag)
#        self.__setattr__(flag, _flag)
#        if _flag:
#            super(StoryApp,self).remove_widget(widget)
#        else:
#            widget.pos = self.get_new_random_position()
#            super(StoryApp,self).add_widget(widget)
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
        self.artefacts[_b.Id] = (_b,{})
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
            self.artefacts[_s.Id] = sobj
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
            self.artefacts[_t.Id] = tobj
        if story or sprint:
            self.current_task = tobj
        return _t
    def new_artefact_pressed(self,ctrl,view, **kwargs): # *largs
        _r = ctrl(self,None,**kwargs)
#        self.__setattr__(view, _r.newDialog(minv=True))
#        super(StoryApp,self).add_widget(self.__getattribute__(view))
        return _r 
    def getArtefact(self,**kwargs):
        _p = kwargs.setdefault('controller', None)
        if type(_p) is None:
            _p = _p(self,kwargs.setdefault('file', None),**kwargs)
        return _p
    def remove_project_view(self,w):
        super(StoryApp,self).remove_widget(w)
    def newBacklog(self,ctrl):
        return self.view.add_new_artefact(ctrl, artefact_types[BACKLOG]['container'], 
            artefact_types[BACKLOG]['viewCurrent'], self.artefacts[ctrl.Id][1])
    def newProject(self,ctrl):
        return self.view.add_new_artefact(ctrl,
                                     artefact_types[PROJECTS]['container'],
                                     artefact_types[PROJECTS]['viewCurrent'],
                                     self.artefacts[ctrl.Id][1])
    def newRelease(self,ctrl):
        return self.view.add_new_artefact(ctrl,
                                     artefact_types[RELEASES]['container'],
                                     artefact_types[RELEASES]['viewCurrent'],
                                     self.artefacts[ctrl.Id][1])
    def newSprint(self,ctrl):
        return self.view.add_new_artefact(ctrl,
                                     artefact_types[SPRINTS]['container'],
                                     artefact_types[SPRINTS]['viewCurrent'],
                                     self.artefacts[ctrl.Id][1])
    def newStory(self,ctrl):
        return self.view.add_new_artefact(ctrl,
                                     artefact_types[STORIES]['container'], 
                                     artefact_types[STORIES]['viewCurrent'],
                                     self.artefacts[ctrl.Id][1])
    def newTask(self,ctrl):
        return self.view.add_new_artefact(ctrl,
                                     artefact_types[TASKS]['container'],
                                     artefact_types[TASKS]['viewCurrent'],
                                     self.artefacts[ctrl.Id][1])
    def add_new_artefact(self, ctrl, container, callback, ret):
        return self.view.add_new_artefact(ctrl, container, callback, ret)
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
        self.view.toggle_view_current_Artefact(_c.view)
        
    def update_story_btn_name(self,story):
        return self.view.update_story_btn_name(story)
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
        ctrl = self.artefacts[btn.id][0]
        view = ctrl.view
        if view not in self.container.children:
            super(StoryApp,self).add_widget(view)
        else: ctrl.app_btn_pressed()
    def fullscreen(self, *largs, **kwargs):
        pass
    def unfullscreen(self, *largs, **kwargs):
        pass
    def close(self,touch=None):
        #close all the artefacts
        for a in self.artefacts.values():
            ctrl = a[0]
            try:
                ctrl.close()
            except TypeError:
                Log.debug('Unable to close %s' % ctrl)
#        for b in self.backlog.values():
#            b[0].close()
        self.add_to_git()
        AsyncHandler().shutdown()
        super(StoryAppView, self.view).close(touch)
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
    def width(self):
        return self.view.width
    @width.setter
    def width(self, value):
        self.view.width = value
    @property
    def height(self):
        return self.view.height
    @height.setter
    def height(self, value):
        self.view.height = value
    @property
    def size(self):
        return self.view.size
    @size.setter
    def size(self, value):
        self.view.size = value
    @property
    def x(self):
        return self.view.x
    @x.setter
    def x(self, value):
        self.view.x = value
    @property
    def y(self):
        return self.view.y
    @y.setter
    def y(self, value):
        self.view.y = value
    @property        
    def artefacts(self):
        return self.model.artefacts
    @property
    def current_project(self):
        return self.model.current_project 
    @current_project.setter
    def current_project(self, value):
        self.model.current_project.append(value)
    @property
    def current_release(self):
        return self.model.current_release
    @current_release.setter
    def current_release(self, value):
        self.model.current_release.append(value)
    @property
    def current_sprint(self):
        return self.model.current_sprint
    @current_sprint.setter
    def current_sprint(self, value):
        self.model.current_sprint.append(value)
    @property
    def current_story(self):
        return self.model.current_story
    @current_story.setter
    def current_story(self, value):
        self.model.current_story.append(value)
    @property
    def current_task(self):
        return self.model.current_task
    @current_task.setter
    def current_task(self, value):
        self.model.current_task.append(value)
    @property
    def currentProjectView(self):
        return self.model.currentProjectView
    @currentProjectView.setter
    def currentProjectView(self, value):
        self.model.currentProjectView.append(value)
    @property
    def currentReleaseView(self):
        return self.model.currentReleaseView
    @currentReleaseView.setter
    def currentReleaseView(self, value):
        self.model.currentReleaseView.append(value)
    @property
    def currentSprintView(self):
        return self.model.currentSprintView
    @currentSprintView.setter
    def currentSprintView(self, value):
        self.model.currentSprintView.append(value)
    @property
    def currentStoryView(self):
        return self.model.currentStoryView
    @currentStoryView.setter
    def currentStoryView(self, value):
        self.model.currentStoryView.append(value)
    @property
    def currentTaskView(self):
        return self.model.currentTaskView
    @currentTaskView.setter
    def currentTaskView(self, value):
        self.model.currentTaskView.append(value)
    
        
if __name__ == '__main__':
    from pymt.ui.window import MTWindow
    from pymt.base import runTouchApp, stopTouchApp
    from cmap.tools.myTools import scale_tuple
    size = get_min_screen_size()
    mw = MTWindow()
    mw.size = scale_tuple(size,0.045)
    scale = .13
    size = scale_tuple(mw.size, scale)
    base_image = os.path.abspath(os.path.join(os.path.dirname(__file__),
                            '..',  '..', 'examples', 'framework','images'))
#    coverflow = MTCoverFlow(size=(500,500))
#    for fn in glob(os.path.join(base_image, '*.png')):
#        button = MTToggleButton(label=os.path.basename(fn)) #MTImageButton(image=Loader.image(filename))
#        coverflow.add_widget(button)
#    
#    dc = MyDragableContainer(coverflow, True)
#    mw.add_widget(dc)
    runTouchApp()
    