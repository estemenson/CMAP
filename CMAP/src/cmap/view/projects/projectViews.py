'''
Created on Sep 26, 2010

@author: stevenson
'''

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from agileConfig import Config
try:
    Log = Config().log.logger
except Exception: #IGNORE:W0703
    from petaapan.logger.console_logger import ConsoleLogger
    Log = ConsoleLogger('CMAP')
    
from cmap.view.baseViews import MinView
from cmap.tools.myTools import scale_tuple, get_min_screen_size
from cmap.tools.uniqueID import uuid
from pymt.base import runTouchApp
from pymt.ui.window import MTWindow

class ProjectMinView(MinView):   
    def __init__(self,wnd,ctrl, **kwargs):
        kwargs.setdefault('name','')
        kwargs.setdefault('minimized_label', kwargs['name'])
        super(ProjectMinView,self).__init__(wnd,ctrl,**kwargs)
#class ProjectMinViewOld(MyInnerWindowWithSaveAndTrash):   
#    def __init__(self,wnd,ctrl, **kwargs):
#        kwargs.setdefault('name','')
#        kwargs.setdefault('minimized_label', kwargs['name'])
#        super(ProjectMinViewOld,self).__init__(**kwargs)
#        if ctrl is None:
#            ctrl = TestController(wnd,'minimal' if self.isMinimal else 'full')
#        self.ctrl = ctrl
#        try:
#            self.isMinimal = True if self.isMinimal else False
#        except Exception: #IGNORE:W0703
#            self.isMinimal = True
#        self.grid_size = minimal_size
#        story_size = scale_tuple(self.grid_size, 0.2)
#        self._name = kwargs['name']
#        self._id = kwargs['id']
#        self._description = kwargs.setdefault('description', '')
#        self.padding = 8
#        self.spacing = 8
#        self.font_height = 13 * 2
#        self._full_width =  int(story_size[0])
#        self._half_width = int(self._full_width /2) 
#        self.visible_lines = 3
#        
#        self.layout = MTGridLayout(size=story_size,rows=3,cols=1,
#                                   spacing=self.spacing)
#
#        self.row0 = MTGridLayout(cols=2,rows=2,spacing=self.spacing,
#                                 uniform_width=False, uniform_height=False)
#        self.row1 = MTGridLayout(cols=1,rows=2, spacing=self.spacing,
#                                 uniform_width=False, uniform_height=False)
#        text_height = self.font_height * self.visible_lines
#        sz=(self._full_width - int(len('Project Name: ')*pixels),self.font_height)
#        self.story_name = MyTextInput(label=self._name,id='project_name_id',
#                                      size=sz,keyboard_to_root='True',
#                                      place_keyboard_by_control='True')
#        self.description = MyTextArea(label=self._description,\
#                                       id='description_id',
#                                       size=(self._full_width,text_height),
#                                       keyboard_to_root='True',
#                                      place_keyboard_by_control='True')
#        #push handlers for each text input fields
#        self.story_name.push_handlers(on_text_change=self._set_name)
#        self.description.push_handlers(on_text_change=self._set_description)
#        
#        
#        self.row0.add_widget(MTLabel(label='Project Name:'))
#        self.row0.add_widget(self.story_name)
#        
#        self.row1.add_widget(MTLabel(label='Description:'))
#        self.row1.add_widget(self.description)
#        self.layout.add_widget(self.row0)
#        self.layout.add_widget(self.row1)
#        self.layout.pos = (25,0)
#        self.canvas = MTScatter(size=self.grid_size, pos=(0,2),
#                                cls='storycardcss')
#        self.canvas.add_widget(self.layout)
#        self.add_widget(self.canvas)
#    
#    
#    
#    def fullscreen(self, *largs, **kwargs):
#        self.isMinimal = not self.isMinimal
#        self.ctrl.switch_view(self.isMinimal)
#        
#    
#    def _get_name(self):
#        return self._name if self._name else self.ctrl.Name 
#    def _set_name(self, value):
#        self._name = value 
#        self.ctrl.Name = value
#    Name = property(_get_name, _set_name)
#    
#    def _get_description(self):
#        return self._description if self._description\
#                                 else self.ctrl.Description    
#    def _set_description(self, value):
#        self._description = value 
#        self.ctrl.Description = value.value
#    Description = property(_get_description, _set_description)
#        
#    def save(self, touch=None):
#        self.ctrl.save()
#        
#    def close(self, touch):
#        if self.ctrl.Id is None:
#            if not self._name: 
#                self.trash()
#                return
#            self.ctrl.close(self)
#        super(ProjectMinViewOld, self).close(touch)
#
#    def trash(self, touch=None, *largs, **kwargs):
#        self.ctrl.trash()
#        super(ProjectMinViewOld, self).close(touch)
class ProjectView(ProjectMinView):pass
class TestController(object):
    def __init__(self, w, minv):
        self.screen_size = get_min_screen_size()
        self.isMinimal = True if minv == 'minimal' else False
        self.root = w 
        self.view = None
        self.story_view_size = None
        self.id = uuid()
        self.createView()
        self._name = None
        self._description = None
    def get_story_size(self):
        return self.screen_size
    def switch_view(self, minv):
        self.isMinimal = minv
        self.root.remove_widget(self.view)
        self.createView()
    @property
    def Name(self):
        return ''
    @property
    def Description(self):
        return ''
    def fullscreen(self):
        pass
    def save(self, touch=None):
        pass
    def close(self):
        self.save()
    def trash(self):
        pass
    @property
    def Id(self):
        return None
    def createView(self):
        if self.isMinimal:
            self.view = ProjectMinView(self.root,self, 
                              name='name',
                              id=self.id,
                              as_a='as_a',
                              want_to='want_to',
                              so_that='so_that',
                              estimate='0',
                              actual='0',
                              owner='owner',
                              description='description',
                              control_scale=1.0, cls='type1css')
            self.story_view_size = scale_tuple(self.view.grid_size,-0.001,-0.03)
            self.view.pos = (275,265)
        else:
            self.view = ProjectMinView(self.root,self, 
                              name='name',
                              id=self.id,
                              as_a='as_a',
                              want_to='want_to',
                              so_that='so_that',
                              estimate='0',
                              actual='0',
                              owner='owner',
                              description='description',
                              control_scale=1.0, cls='type1css')
            self.story_view_size = scale_tuple(self.view.grid_size,0.07)
            self.view.pos = (75,65)
        self.view.size = self.story_view_size
        self.root.add_widget(self.view)
 
if __name__ == '__main__':
    args = ['','minimal']
    mw = MTWindow()
    c = TestController(mw,args[1])
    mw.size = scale_tuple(get_min_screen_size(),.045)
    runTouchApp()
