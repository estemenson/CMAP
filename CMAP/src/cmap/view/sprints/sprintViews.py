# -*- coding: utf-8 -*-
'''
Created on Sep 29, 2010

@author: stevenson
'''
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from agileConfig import Config
from cmap.view.baseViews import minimal_size, pixels, MinView
from pymt.ui.widgets.layout.gridlayout import MTGridLayout
from cmap.tools.myTextInput import MyTextInput, MyTextArea
from pymt.ui.widgets.label import MTLabel
from pymt.ui.widgets.scatter import MTScatter
try:
    Log = Config().log.logger
except Exception:
    from petaapan.utilities.console_logger import ConsoleLogger
    Log = ConsoleLogger('CMAP')
from cmap.tools.borders import MyInnerWindowWithSaveAndTrash
from cmap.tools.myTools import get_min_screen_size, scale_tuple
from cmap.tools.uniqueID import uuid
from pymt.ui.window import MTWindow
from pymt.base import runTouchApp


class SprintMinView(MinView):
    def __init__(self,wnd,ctrl, **kwargs):
        kwargs.setdefault('name','')
        kwargs.setdefault('minimized_label', kwargs['name'])
        super(SprintMinView,self).__init__(wnd,ctrl,**kwargs)
class SprintMinViewOld(MyInnerWindowWithSaveAndTrash):
    def __init__(self,wnd,ctrl, **kwargs):
        kwargs.setdefault('name','')
        kwargs.setdefault('minimized_label', kwargs['name'])
        super(SprintMinViewOld,self).__init__(**kwargs)
        if ctrl is None:
            ctrl = TestController(wnd,'minimal' if self.isMinimal else 'full')
        self.ctrl = ctrl
        try:
            self.isMinimal = True if self.isMinimal else False
        except Exception:
            self.isMinimal = True
        self.grid_size = minimal_size
        story_size = scale_tuple(self.grid_size, 0.2)
        self._name = kwargs['name']
        self._id = kwargs['id']
        self._description = kwargs.setdefault('description', '')
        self.padding = 8
        self.spacing = 8
        self.font_height = 13 * 2
        self._full_width =  int(story_size[0])
        self._half_width = int(self._full_width /2) 
        self.visible_lines = 3
        
        self.layout = MTGridLayout(size=story_size,rows=3,cols=1,
                                   spacing=self.spacing)

        self.row0 = MTGridLayout(cols=2,rows=2,spacing=self.spacing,
                                 uniform_width=False, uniform_height=False)
        self.row1 = MTGridLayout(cols=1,rows=2, spacing=self.spacing,
                                 uniform_width=False, uniform_height=False)
        text_height = self.font_height * self.visible_lines
        sz=(self._full_width - int(len('Sprint Name: ')*pixels),
                                                            self.font_height)
        self.story_name = MyTextInput(label=self.name,id='sprint_name_id',
                                      size=sz,keyboard_to_root='True',
                                      place_keyboard_by_control='True')
        self.description = MyTextArea(label=self._description,\
                                       id='description_id',
                                       size=(self._full_width,text_height),
                                       keyboard_to_root='True',
                                      place_keyboard_by_control='True')
        #push handlers for each text input fields
        self.story_name.push_handlers(on_text_change=self._set_name)
        self.description.push_handlers(on_text_change=self._set_description)
        
        
        self.row0.add_widget(MTLabel(label='Sprint Name:'))
        self.row0.add_widget(self.story_name)
        
        self.row1.add_widget(MTLabel(label='Description:'))
        self.row1.add_widget(self.description)
        self.layout.add_widget(self.row0)
        self.layout.add_widget(self.row1)
        self.layout.pos = (25,0)
        self.canvas = MTScatter(size=self.grid_size, pos=(0,2),
                                cls='storycardcss')
        self.canvas.add_widget(self.layout)
        self.add_widget(self.canvas)
    
    
    
    def fullscreen(self, *largs, **kwargs):
        self.isMinimal = not self.isMinimal
        self.ctrl.switch_view(self.isMinimal)
        
    
    def _get_name(self): return self.ctrl.Name 
    def _set_name(self, value): 
        self.ctrl.Name = value
    name = property(_get_name, _set_name)
    
    
    def _set_description(self, value): 
        self.ctrl.Description = value.value
        
    def save(self, touch, *largs, **kwargs):
        self.ctrl.save()

    def close(self, touch):
        if self.ctrl.Id is None:
            if not self.name: 
                self.trash()
                return
            self.ctrl.close(self)
        super(SprintMinViewOld, self).close(touch)

    def trash(self, touch=None, *largs, **kwargs):
        self.ctrl.trash()
        super(SprintMinViewOld, self).close(touch)
class SprintView(SprintMinView):pass
class TestController(object):
    def __init__(self, w, minv, **kwargs):
        self.screen_size = get_min_screen_size()
        self.isMinimal = True if minv == 'minimal' else False
        self.root = w 
        self.view = None
        self.story_view_size = None
        self.id = uuid()
        self.createView()
    def get_story_size(self):
        return self.screen_size
    def switch_view(self, minv):
        self.isMinimal = minv
        self.root.remove_widget(self.view)
        self.createView()
    def fullscreen(self):
        pass
    def save(self):
        pass
    @property
    def Id(self):
        return None
    def close(self):
        self.save()
    def trash(self):
        pass
    def createView(self):
        if self.isMinimal:
            self.view = SprintMinView(self.root,self, 
                              name='name',
                              id=self.id,
                              as_a='as_a',
                              want_to='want_to',
                              so_that='so_that',
                              estimate='0',
                              actual='0',
                              owner='owner',
                              description='description',
                              control_scale=0.7, cls='type1css')
            self.story_view_size = scale_tuple(self.view.grid_size,-0.001,-0.03)
            self.view.pos = (275,265)
        else:
            self.view = SprintMinView(self.root,self, 
                              name='name',
                              id=self.id,
                              as_a='as_a',
                              want_to='want_to',
                              so_that='so_that',
                              estimate='0',
                              actual='0',
                              owner='owner',
                              description='description',
                              control_scale=0.7, cls='type1css')
            self.story_view_size = scale_tuple(self.view.grid_size,0.07)
            self.view.pos = (75,65)
        self.view.size = self.story_view_size
        self.root.add_widget(self.view)
 
if __name__ == '__main__':
    import sys
    args = sys.argv
    mw = MTWindow()
    c = TestController(mw,args[1])
    mw.size = scale_tuple(get_min_screen_size(),.045)
    runTouchApp()
