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
from cmap import BACKLOG,PROJECTS,RELEASES,SPRINTS,STORIES,TASKS,artefact_types
from pymt.ui.widgets.widget import MTWidget

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
        kwargs['controller'] = self
        self.view = StoryAppView(**kwargs)
        self.model = StoryAppModel(**kwargs)
        self.model.get_view_data()
    def add_artefact(self, artefact=None, **kwargs):
        '''
        Create and / or just add an artifact to the main View. Metadata is
        updated as well as current artefacts of the appropriate type
        arguments:
            artefact: an artefact that has an Id or _id property which is used 
            to retrieve the artefact controller (could be the artefact 
            controller but not necessarily)
            kwargs: 
                open: whether or not to add the artifacts view to the app
                current: the container where all current artefacts of this type
                are held 
        '''
        op = kwargs.setdefault('open','True')
        #type = artefact_types[type]
        id  = None
        if artefact:
            #if object exists get the id
            id = artefact.Id if isinstance(artefact, ArtefactController)\
                     else artefact._id #IGNORE:W0212
        if not id:
            #create a new artefact
            id = self.new_artefact(**kwargs).Id
        _view = self.artefacts[id][0].view
        _open = self.view.toggle_view_current_Artefact(_view) if\
                    op == 'True' else op
        self.artefact_changed(Id=id, size=_view.size, pos=_view.pos,
                              open=_open, scale=_view.scale,
                              rotation=_view.rotation)
        #set the current artefact (appends to the list)
        self.__setattr__(kwargs['current'], self.artefacts[id])
        return id
    def add_artefact_access(self, ctrl, container, callback, ret):
        _r = self.view.add_artefact_access(ctrl, container, callback, ret)
    def add_to_git(self):
        AsyncHandler().save(None, 'Commit session edits')
    def artefact_changed(self, **kwargs):#id, size, pos, open='True'):
        kwargs.setdefault('open', 'True')
        kwargs.setdefault('scale', 1.0)
        kwargs.setdefault('rotation', 0.0)
        kwargs.setdefault('size', (600,400))
        kwargs.setdefault('pos', (100,100))
        #store the size and position of artefacts
        self.model.artefact_changed(**kwargs)
    def artefact_moving(self, **kwargs):
        '''
        need to loop through all open artefacts to see if the one moving is 
        intersecting with any currently open artefact, if it is then we need 
        to check if it is reasonable for the dragged artefact to become a child 
        of  the intersected artefact
        '''
        id = kwargs['Id']
        pos = kwargs['pos']
        from cmap.view.baseViews import MinView
        for child in [c for c in self.view.container.children if\
                                isinstance(c, MinView) and c.Id != id]:
            box_pos, box_sz = child.bbox
            if pos[0] >= box_pos[0] and pos[0] <= box_pos[0] + box_sz[0] and\
                    pos[1] >= box_pos[1] and pos[1] <= box_pos[1] + box_sz[1]:
                print('pos: %s bounding box: %s' % (str(pos), str(box_pos)))
                child.nudge()
                child.nudge_reset()
    def check_position(self,**kwargs):
        pos = kwargs.get('pos', None) 
        if pos:
            if pos[0] > self._x_range[-1]:
                pos = (self._x_range[-1], pos[1])
            if pos[1] > self._y_range[-1]:
                pos =  (pos[0],self._y_range[-1])
        return pos
    def close_artefact(self,**kwargs):
        id = kwargs['Id']
        self.model.artefact_changed(**kwargs)
        self.view.toggle_view_current_Artefact(self.artefacts[id][0].view)
    def container_reset_children(self,container):
        f = self.__getattribute__(container)
        x = len(f.children) -1
        while x > 0:
            w = f.children[x]
            f.remove_widget(w) 
            x = len(f.children) -1
    def create_view_and_open(self,ctrl,**kwargs):
        ctrl.newDialog(minv=True,**kwargs)
        kwargs.update(artefact_types[ctrl._type])
        self.add_artefact(ctrl, **kwargs)
    def exit(self,touch=None):
        self.model.close()
        #close all the artefacts
        for a in self.artefacts.values():
            ctrl = a[0]
            try:
                ctrl.exit()
            except TypeError:
                Log.debug('Unable to close %s' % ctrl)
#        for b in self.backlog.values():
#            b[0].close()
        self.add_to_git()
        AsyncHandler().shutdown()
    def getArtefact(self,**kwargs):
        _p = kwargs.setdefault('controller', None)
        if not isinstance(_p, ArtefactController):
            _p = _p(self,kwargs.setdefault('file', None),**kwargs)
        else:
            Log.debug("file:%s, method:%s ha contrller ID: %s"\
                      % (__file__,'getArtefact' ,_p.Id))
        return _p
    def get_new_random_position(self):
        return (choice(self._x_range),choice(self._y_range))
    def list_button_pressed(self, btn):
        ctrl = self.artefacts[btn.id][0]
        view = ctrl.view
        if view not in self.container.children:
            super(StoryApp,self).add_widget(view)
        else: ctrl.app_btn_pressed()
    def load_children(self,id, type):pass
        #TODO: STEVE refactor to get children from model of the artefact
#        for f in self.model.xmlFiles[type]:#artefact_types[type]['type']]:
#            Log.debug('only loading %s %s' % (type,f))
#            kwargs = artefact_types[type].copy()
#            kwargs['name'] = os.path.splitext(os.path.basename(f))[0]
#            kwargs['file'] = f
#            r = self.getArtefact(**kwargs)
#            self.artefacts[r.Id] = (r,{'meta':{}})
    def new_artefact(self,**kwargs): # *largs
        #create the controller for the new artefact
        pos = self.check_position(**kwargs)
        if pos: kwargs['pos'] = pos
        _r = kwargs['controller'](self,None,**kwargs)
        _r.newDialog(True, **kwargs)
        self.artefacts[_r.Id] = (_r,{'meta':{}})
        return _r 
    #TODO: STEVE this group of new_XXX_pressed methods must be refactored
    def new_backlog_artefact(self,**kwargs):
        if kwargs['type'] is STORIES:
            #this story goes in the backlog it was created while there was
            # no active sprint or release, we need to update the kwargs to 
            # reflect that it is backlog story
            kwargs.update(artefact_types[BACKLOG])
        return self.artefacts[self.add_artefact(None, **kwargs)][0]
    def new_project(self, **kwargs):
        return self.artefacts[self.add_artefact(None, **kwargs)][0] 
    def new_release(self, **kwargs): 
        project = None if self.current_project is None \
                                        else self.current_project[0].Id
        if not project:
            return # Do not support releases in backlog now
        _r = self.artefacts[self.add_artefact(None,**kwargs)][0]
        if project:
            project[0].Children = _r.Id
            _r.Parent = project[0].Id
        return _r
    def new_sprint(self, **kwargs): 
        project = None if self.current_project is None \
                                        else self.current_project[0]
        release = None if self.current_release is None \
                        else self.current_release[0].Id
        if not release:
            return # No appropriate parent
        _s = self.artefacts[self.add_artefact(None,**kwargs)][0]
        if release:
            release[0].Children = _s.Id
            _s.Parent = release[0].Id
        return _s
    def new_story(self, **kwargs):
        project = None
        sprint = None
        p = self.current_project
        if p and len(p):
            project = p[0]
        s = self.current_sprint
        if s and len(s):
            sprint = s[0]
        parent = sprint if sprint else project
        if not parent:
            return self.new_backlog_artefact(**kwargs)
        _s = self.artefacts[self.add_artefact(None, **kwargs)][0]
#        _s = self.new_artefact(**kwargs)
#        self.view.toggle_view_current_Artefact(_s.newDialog(True, **kwargs))
        if sprint:
            sprint[0].Children = _s.Id
            _s.Parent = sprint[0].Id
        _s.register_observer(self)
        return _s
    def new_task(self, **kwargs):
        story = None
        sprint = None
        parent = None
        if self.current_story and len(self.current_story):
            story = self.current_story[0]
        if self.current_sprint and len(self.current_sprint):
            sprint = self.current_sprint[0]
        parent = None
        if story:
            parent = story
        elif sprint:
            parent = sprint
        else:
            return # No appropriate parent, we don't support this yet
        _t = self.artefacts[self.add_artefact(None,**kwargs)][0]
        if story:
            story[0].Children = _t.Id
            _t.Parent = story[0].Id
        elif sprint:
            sprint[0].Children = _t.Id
            _t.Parent = sprint[0].Id
        return _t
    def on_github_notification(self, ret):
        msg = ret[1]
        print("GOOGLE APP HOOK CCALLED ***************************************")
        print("***********************************")
        for c in msg['commits']:
            for a in c['added']:
                Log.debug('%s added by %s' % (a, c['author']['name']))
            for m in c['modified']:
                Log.debug('%s modified by %s' % (m, c['author']['name']))
            for r in c['removed']:
                Log.debug('%s removed by %s' % (r, c['author']['name']))
    def remove_widget(self, view):
        self.view.remove_widget(view)
    def trash(self,id):#,atype=None):
#        if atype is None:# or type is 'stories':
#            btn = self.buttons[artefact.Id]
#            lbl = self.labels[artefact.Id]
#            self.backlog_list_layout.remove_widget(btn)
#            self.story_flow.remove_widget(lbl)
#            self.remove_widget(artefact)
#            del self.artefacts[artefact.Id]
#        else:
        if id in self.artefacts:
            dic = self.artefacts[id][1]
            for l in dic.keys():
                if isinstance(dic[l], MTWidget):
                    #self.__getattribute__(l).remove_widget(_widget)
                    self.view.trash(dic[l],l)
            self.model.trash(id)
        return
    def unfullscreen(self, *largs, **kwargs):
        pass
    def update_story_btn_name(self,story):
        return self.view.update_story_btn_name(story)
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
        if not value in self.model.current_project: 
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
#        button = MTToggleButton(label=os.path.basename(fn)) 
#MTImageButton(image=Loader.image(filename))
#        coverflow.add_widget(button)
#    
#    dc = MyDragableContainer(coverflow, True)
#    mw.add_widget(dc)
    runTouchApp()
    