# -*- coding: utf-8 -*-
'''
Created on 2010-10-12

@author: steve
'''
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from agileConfig import Config
from cmap.tools.scrible import MyScribbleWidget
try:
    Log = Config().log.logger
except Exception: #IGNORE:W0703
    from petaapan.utilities.console_logger import ConsoleLogger
    Log = ConsoleLogger('CMAP')
from cmap.tools.borders import MyInnerWindowWithSaveAndTrash
#    MyInnerWindowWithKeyboard
from cmap.tools.myTools import scale_tuple, get_min_screen_size
from pymt.ui.widgets.layout.gridlayout import MTGridLayout
from cmap.tools.myTextInput import MyTextArea, MyTextInput
from pymt.ui.widgets.label import MTLabel
from cmap.tools.uniqueID import uuid
from pymt.ui.window import MTWindow
from pymt.base import runTouchApp
from pymt.core.image import Image
from OpenGL.GL import glReadBuffer, glReadPixels, GL_RGB, \
            GL_UNSIGNED_BYTE, GL_FRONT
from pymt.texture import Texture
from cmap.controller.storyapp import Storyapp

minimal_size = (600,400)
pixels = 9


class MinView(MyInnerWindowWithSaveAndTrash):#MyInnerWindowWithKeyboard):
    def __init__(self,wnd,ctrl, **kwargs):
        if ctrl is None:
            ctrl = TestController(wnd,'minimal' if self.isMinimal else 'full')
        self.ctrl = ctrl
        try:
            self.isMinimal = True if self.isMinimal else False
        except Exception: #IGNORE:W0703
            self.isMinimal = True
        self._type_name = kwargs['type_name']
        self._name = kwargs.setdefault('name',self.ctrl.Name)
        kwargs.setdefault('minimized_label', self._name)
        self._id = self.ctrl.Id
        kwargs['size'] = self.grid_size = minimal_size
        super(MinView,self).__init__(**kwargs)
        story_size = scale_tuple(self.grid_size, 0.2)
        self.story_view_size = None
        self._description = self.ctrl.Description
        self.padding = 8
        self.spacing = 8
        self.font_height = 13 * 2
        self._full_width =  int(story_size[0])
        self._half_width = int(self._full_width /2) 
        self.visible_lines = 3
        self._button_image = None
        
        self.layout = MTGridLayout(size=story_size,rows=3,cols=1,
                                   spacing=self.spacing)

        self.row0 = MTGridLayout(cols=2,rows=2,spacing=self.spacing,
                                 uniform_width=False, uniform_height=False)
        self.row1 = MTGridLayout(cols=1,rows=2, spacing=self.spacing,
                                 uniform_width=False, uniform_height=False)
        text_height = self.font_height * self.visible_lines
        label_txt = ('%s Name: ' % self._type_name)
        txt_in_id = ('%s_name_id' % self._type_name)
        sz=(self._full_width - int(len(label_txt)*pixels),self.font_height)
        self.story_name = MyTextInput(label=self.name,id=txt_in_id,
                                      group=self._id,
                                      size=sz,keyboard_to_root='True',
                                      place_keyboard_by_control='True')
        self.description = MyTextArea(label=self._description,\
                                       id='description_id',
                                       group=self._id,
                                       size=(self._full_width,text_height),
                                       keyboard_to_root='True',
                                      place_keyboard_by_control='True')
        #push handlers for each text input fields
        self.story_name.push_handlers(on_text_change=self._set_name)
        self.description.push_handlers(on_text_change=self._set_description)
        
        
        self.row0.add_widget(MTLabel(label=label_txt))
        self.row0.add_widget(self.story_name)
        
        self.row1.add_widget(MTLabel(label='Description:'))
        self.row1.add_widget(self.description)
        self.layout.add_widget(self.row0)
        self.layout.add_widget(self.row1)
        self.layout.pos = (25,0)
        self.scribleWidget = MyScribbleWidget(size=self.grid_size, scribbles=\
                                              self.ctrl.Scribbles,
                                              TextFields=self.ctrl.TextFields)
        self.scribleWidget.push_handlers(on_change=self.add_remove_scribble)
        self.scribleWidget.push_handlers(on_text_change=self.scribble_text_change)
        self.canvas = self.layout
        self.canvas = self.scribleWidget
        self.scribleWidget.center = self.center
        self.add_widget(self.canvas)
        self.first_draw = True
        
    def draw(self):
        super(MinView, self).draw()
        if self.first_draw:
            self.first_draw = False
            self.set_button_image()
            
    
    def scribble_text_change(self,value):
        self.ctrl.scribble_text_change(value)
        return True
         
    def add_remove_scribble(self,idu,touches):
        try:
            scribble = touches[idu] 
            if not idu in scribble.keys():
                scribble['Id'] = idu 
            try:
                self.ctrl.add_scribble(scribble)
            except Exception: #IGNORE:W0703
                pass
        except KeyError:
            self.ctrl.remove_scribble(id)
    def fullscreen(self, *largs, **kwargs):
        self.isMinimal = not self.isMinimal
        self.ctrl.switch_view(self.isMinimal)
        
    
    def _get_name(self):
        if self._name is None or not len(self._name): 
            return self.ctrl.Name
        return self._name 
    def _set_name(self, value): 
        self._name = value
        self.ctrl.Name = value
    name = property(_get_name, _set_name)
    
    @property
    def Id(self):
        return self._id
    
    
    def _set_description(self, value): 
        self._description = value
        self.ctrl.Description = value.value

    @property        
    def ButtonImage(self):
        return self._button_image
    
    def set_button_image(self):
        pos = self.to_window(*self.pos)
        size = self.size
        glReadBuffer(GL_FRONT)
        data = glReadPixels(pos[0], pos[1], size[0], size[1],
                            GL_RGB, GL_UNSIGNED_BYTE)
        texture = Texture.create(size[0], size[1], format=GL_RGB)
        texture.blit_buffer(data, size)
        self._button_image = Image(texture)
        # Update all the buttons referencing this artifact
        try:
            blist = Storyapp().artifacts[self.Id][1]
            for im in blist:
                blist[im].image = self._button_image
        except KeyError:
            pass
        try:
            blist = Storyapp().backlog[self.Id][1]
            for im in blist:
                blist[im].image = self._button_image
        except KeyError:
            pass

    def save(self, touch=None):
        self.ctrl.save()
    def close(self, touch):
        if self.ctrl.Id is None:
            if not self.name: 
                self.trash()
                return
            self.ctrl.close(self)
        super(MinView, self).close(touch)

    def trash(self, touch=None, *largs, **kwargs):
        self.ctrl.trash()
        super(MinView, self).close(touch)

class FullView(MinView):pass
class TestController(object):
    def __init__(self, w, minv):
        self.screen_size = get_min_screen_size()
        self.isMinimal = True if minv == 'minimal' else False
        self.root = w 
        self.view = None
        self.id = uuid()
        self.Scribbles = None
        self.TextFields = None
        self._name = None
        self._description = None
        self.story_view_size = None
        #self.createView()
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
    def close(self):
        self.save()
    def trash(self):
        pass
    def scribble_text_change(self, value):
        pass
    def add_scribble(self, scribble):
        pass
    def remove_scribble(self, idu):
        pass
    @property
    def Id(self): return None
    def createView(self):
        kwargs = {'type_name':'Task', 'name':'name',
                              'id':self.Id,
                              'as_a':'as_a',
                              'want_to':'want_to',
                              'so_that':'so_that',
                              'estimate':'0',
                              'actual':'0',
                              'owner':'owner',
                              'description':'description',
                              'control_scale':0.7, 'cls':'type1css'}
        if self.isMinimal:
            self.view = MinView(self.root,self, **kwargs) #IGNORE:W0142
            self.story_view_size = scale_tuple(self.view.grid_size,-0.001,-0.03)
            self.view.pos = (275,265)
        else:
            self.view = FullView(self.root,self, **kwargs) #IGNORE:W0142
            self.story_view_size = scale_tuple(self.view.grid_size,0.07)
            self.view.pos = (75,65)
        self.view.size = self.story_view_size
        self.root.add_widget(self.view)
    def _get_name(self):
        return ''    
    def _set_name(self, value):
        pass
    Name = property(_get_name, _set_name)
    def _get_description(self):
        return ''    
    def _set_description(self, value):
        pass
    Description = property(_get_description, _set_description)
 
if __name__ == '__main__':
    import sys
    args = sys.argv
    mw = MTWindow()
    from cmap.controller.taskController import TaskController
    from cmap.model.taskModel import TaskModel 
    mkwargs = {'view_type_name':'Task',
               'name':'name',
               'id':'some_id',
               'as_a':'as_a',
               'want_to':'want_to',
               'so_that':'so_that',
               'estimate':'0',
               'actual':'0',
               'owner':'owner',
               'description':'description',
               'control_scale':0.7,
               'cls':'type1css'}
    c = TaskController(mw,  #IGNORE:W0142
                       None,
                       p_artifact=None,
                       model=TaskModel,
                       view_type=MinView,
                       mini_view_type=MinView,
                       get_artifact=None, **mkwargs)
    mw.add_widget(c.view)
    mw.size = scale_tuple(get_min_screen_size(),.045)
    runTouchApp()
