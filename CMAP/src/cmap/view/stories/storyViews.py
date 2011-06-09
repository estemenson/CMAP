'''
Storycard

Created on Jun 16, 2010

@author: stevenson
'''

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from agileConfig import Config
try:
    Log = Config().log.logger
except Exception:
    from petaapan.logger.console_logger import ConsoleLogger
    Log = ConsoleLogger('CMAP')
from pymt.ui.colors import css_add_sheet
from pymt.ui.widgets.layout.gridlayout import MTGridLayout
from pymt.ui.widgets.label import MTLabel
from pymt.ui.widgets.scatter import MTScatter
from pymt.ui.widgets.composed.textinput import MTTextInput
from pymt.ui.window import MTWindow
from pymt.base import runTouchApp
from cmap.tools.borders import MyInnerWindowWithSaveAndTrash
from cmap.tools.myTabs import MyTabs
from cmap.tools.myTools import get_min_screen_size, scale_tuple
from cmap.tools.myTextInput import MyTextInput, MyTextArea
from cmap.tools.uniqueID import uuid
from cmap.view.baseViews import MinView, minimal_size, pixels

StoryCardCSS = '''
.storycardcss {
    bg-color: rgba(185,211,238, 255);
    border-color: rgb(100, 100, 220);
    border-width: 20;
    draw-border: 1;    
}
.storycardcss1 {
    bg-color: rgba(211, 211, 211, 255);
    border-color: rgb(80, 125, 130);
    border-width: 10;
    draw-border: 1;   
    } 
.storycardrow0 {
    bg-color: rgba(211, 211, 211, 255);
    border-color: rgb(119, 136, 153);
    border-width: 10;
    draw-border: 1;  
    }  
.storycardrow1 {
    bg-color: rgba(211, 211, 211, 255);
    border-color: rgb(232, 232, 232);
    border-width: 10;
    draw-border: 1;   
    } 
.storycardrow2 {
    bg-color: rgba(211, 211, 211, 255);
    border-color: rgb(0, 206, 209);
    border-width: 10;
    draw-border: 1;  
    }  
.storycardrow3 {
    bg-color: rgba(211, 211, 211, 255);
    border-color: rgb(127, 255, 0);
    border-width: 10;
    draw-border: 1;    
}
'''
css_add_sheet(StoryCardCSS)
#    border-radius: 10;# the larger the value the more rounded the corners;
#border-radius-precision: 0.05;#the smaller the number the smother a rounded 
#                              #corner will look;
class MinimalStoryView(MyInnerWindowWithSaveAndTrash):   
    def __init__(self,wnd,ctrl, **kwargs):
        if not 'name' in kwargs:
            raise KeyError('Name attribute must be passed in kwargs')
        kwargs.setdefault('minimized_label', kwargs['name'])
        super(MinimalStoryView,self).__init__(**kwargs)
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
        self._description = kwargs.setdefault('description','')
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
        sz=(self._full_width - int(len('Story Name: ')*pixels),self.font_height)
        self.story_name = MyTextInput(label=self._name,id='story_name_id',
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
        
        
        self.row0.add_widget(MTLabel(label='Story Name:'))
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
        self.ctrl.close(self)
        super(MinimalStoryView, self).close(touch)

    def trash(self, touch=None, *largs, **kwargs):
        self.ctrl.trash()
        super(MinimalStoryView, self).close(touch)
        
class MinStoryView(MinView):#MinimalStoryView):
    def __init__(self,wnd,ctrl, **kwargs):
        kwargs.setdefault('type_name','Story')
        super(MinStoryView,self).__init__(wnd,ctrl,**kwargs)
         
class StoryView(MinStoryView):
    def __init__(self,wnd,ctrl, **kwargs):
        self.isMinimal = False
        super(StoryView,self).__init__(wnd,ctrl,**kwargs)
        self.canvas.size = self.grid_size = \
                                    scale_tuple(self.ctrl.get_story_size(),.1)
        story_size = scale_tuple(self.grid_size, 0.2)
        self.layout.pos = (60, 80)

        self._as_a = kwargs['as_a']
        self._want_to = kwargs['want_to']
        self._so_that = kwargs['so_that']
        self._estimate = kwargs['estimate']
        self._actual = kwargs['actual']
        self._owner = kwargs['owner']
        self.visible_lines = 5
        self._full_width =  int(story_size[0] - (self.padding * 7)) 
        self._half_width = int(story_size[0] /2) -32
        self.layout.size = (story_size[0], self.font_height*3)
        self.layout.remove_widget(self.row1)
        self.row1 = MTGridLayout(cols=1,rows=2, spacing=self.spacing,
                                 uniform_width=False, uniform_height=False)
        self.row2 = MTGridLayout(cols=2,rows=2,spacing=self.spacing,
                                 uniform_width=False, uniform_height=False)
        text_width = self._full_width
        text_height = self.font_height * self.visible_lines
        self.owner = MyTextInput(label=self._owner,\
                                    id='owner_id',keyboard_to_root='True',
                                    group=self._id,
                                    size=((self._half_width,self.font_height)),
                                    place_keyboard_by_control='True')
        self.description.size = (text_width-8, self.description.height)
        self.as_a = MyTextArea(size=(text_width,text_height), id='as_a_id',
                               group=self._id,
                               label=self._as_a,keyboard_to_root='True',
                                      place_keyboard_by_control='True')
        self.want_to = MyTextArea(size=(text_width,text_height),
                                  keyboard_to_root='True',
                                  id='want_to_id',label=self._want_to,
                                  group=self._id,
                                      place_keyboard_by_control='True')
        self.so_that = MyTextArea(size=(text_width,text_height),
                                  keyboard_to_root='True',
                                  id='so_that_id', label=self._so_that,
                                  group=self._id,
                                      place_keyboard_by_control='True')
        self.estimate = MyTextInput(id='estimate_id',keyboard_to_root='True',
                                    label=self._estimate,
                                    group=self._id,
                                    size=((self._half_width,self.font_height)),
                                      place_keyboard_by_control='True')
        self.actual =  MyTextInput(id='actual_id',keyboard_to_root='True',
                                   label=self._actual,
                                   group=self._id,
                                   size=((self._half_width,self.font_height)),
                                      place_keyboard_by_control='True')

        # Setup the tabs
        self.tabs = MyTabs()
        self.tabs.add_widget(self.as_a, tab='As a')
        self.tabs.add_widget(self.want_to, tab="I want to")
        self.tabs.add_widget(self.so_that, tab='so that')
        self.tabs.select('As a')

        #push handlers for each text input fields
        self.as_a.push_handlers(on_text_change=self._set_as_a)
        self.want_to.push_handlers(on_text_change=self._set_want_to)
        self.so_that.push_handlers(on_text_change=self._set_so_that)
        self.estimate.push_handlers(on_text_change=self._set_estimate)
        self.actual.push_handlers(on_text_change=self._set_actual)
        self.owner.push_handlers(on_text_change=self._set_owner)
        
        self.row0.remove_widget(self.story_name)
        self.story_name.width = self._half_width
        self.row0.add_widget(MTLabel(label='Owner: '))
        self.row0.add_widget(self.story_name)
        self.row0.add_widget(self.owner)
        self.row1.add_widget(MTLabel(label='Description:'))
        self.row1.add_widget(self.description)
        self.row2.add_widget(MTLabel(label='Estimate'))#, autosize=True))
        self.row2.add_widget(MTLabel(label='Actual'))#), autosize=True))
        self.row2.add_widget(self.estimate)
        self.row2.add_widget(self.actual)
#        self.row3.add_widget(MTLabel(label='                      '))
#        self.row3.add_widget(self.tabs)

        #add new rows to layout
        self.layout.add_widget(self.row1)
        self.layout.add_widget(self.row2)
#        self.layout.add_widget(self.row3)
        self.canvas.add_widget(self.tabs)
        self.layout.pos = (45,190)
        self.tabs.pos=(55,185)

    
    def _set_as_a(self, value): 
        self.ctrl.As_a = value.value
    
    
    def _set_want_to(self, value): 
        self.ctrl.Want_to = value.value
    
    
    def _set_so_that(self, value): 
        self.ctrl.So_that = value.value
    
    
    def _set_estimate(self, value): 
        self.ctrl.Estimate = value
    
    
    def _set_actual(self, value): 
        self.ctrl.Actual = value

    def _set_owner(self, value): 
        self.ctrl.Owner = value

    
class StoryCardView(MinimalStoryView):
    def __init__(self,wnd,ctrl, **kwargs):
        self.isMinimal = False
        super(StoryCardView,self).__init__(wnd,ctrl,**kwargs)
        self.canvas.size = self.grid_size = \
                                    scale_tuple(self.ctrl.get_story_size(),.1)
        story_size = scale_tuple(self.grid_size, 0.2)
        self.layout.pos = (60, 80)

        self._as_a = kwargs['as_a']
        self._want_to = kwargs['want_to']
        self._so_that = kwargs['so_that']
        self._estimate = kwargs['estimate']
        self._actual = kwargs['actual']
        self._owner = kwargs['owner']
        self.visible_lines = 5
        self._full_width =  int(story_size[0] - (self.padding * 7)) 
        self._half_width = int(story_size[0] /2) -32
        self.layout.size = (story_size[0], self.font_height*3)
        self.layout.remove_widget(self.row1)
        self.row1 = MTGridLayout(cols=1,rows=2, spacing=self.spacing,
                                 uniform_width=False, uniform_height=False)
        self.row2 = MTGridLayout(cols=2,rows=2,spacing=self.spacing,
                                 uniform_width=False, uniform_height=False)
        text_width = self._full_width
        text_height = self.font_height * self.visible_lines
        self.owner = MyTextInput(label=self._owner,\
                                    id='owner_id',keyboard_to_root='True',
                                    size=((self._half_width,self.font_height)),
                                    place_keyboard_by_control='True')
        self.description.size = (text_width-8, self.font_height)
        self.as_a = MyTextArea(size=(text_width,text_height), id='as_a_id',
                               label=self._as_a,keyboard_to_root='True',
                                      place_keyboard_by_control='True')
        self.want_to = MyTextArea(size=(text_width,text_height),
                                  keyboard_to_root='True',
                                  id='want_to_id',label=self._want_to,
                                      place_keyboard_by_control='True')
        self.so_that = MyTextArea(size=(text_width,text_height),
                                  keyboard_to_root='True',
                                  id='so_that_id', label=self._so_that,
                                      place_keyboard_by_control='True')
        self.estimate = MyTextInput(id='estimate_id',keyboard_to_root='True',
                                    label=self._estimate,
                                    size=((self._half_width,self.font_height)),
                                      place_keyboard_by_control='True')
        self.actual =  MyTextInput(id='actual_id',keyboard_to_root='True',
                                   label=self._actual,
                                   size=((self._half_width,self.font_height)),
                                      place_keyboard_by_control='True')

        # Setup the tabs
        self.tabs = MyTabs()
        self.tabs.add_widget(self.as_a, tab='As a')
        self.tabs.add_widget(self.want_to, tab="I want to")
        self.tabs.add_widget(self.so_that, tab='so that')
        self.tabs.select('As a')

        #push handlers for each text input fields
        self.as_a.push_handlers(on_text_change=self._set_as_a)
        self.want_to.push_handlers(on_text_change=self._set_want_to)
        self.so_that.push_handlers(on_text_change=self._set_so_that)
        self.estimate.push_handlers(on_text_change=self._set_estimate)
        self.actual.push_handlers(on_text_change=self._set_actual)
        self.owner.push_handlers(on_text_change=self._set_owner)
        
        self.row0.remove_widget(self.story_name)
        self.story_name.width = self._half_width
        self.row0.add_widget(MTLabel(label='Owner: '))
        self.row0.add_widget(self.story_name)
        self.row0.add_widget(self.owner)
        self.row1.add_widget(MTLabel(label='Description:'))
        self.row1.add_widget(self.description)
        self.row2.add_widget(MTLabel(label='Estimate'))#, autosize=True))
        self.row2.add_widget(MTLabel(label='Actual'))#), autosize=True))
        self.row2.add_widget(self.estimate)
        self.row2.add_widget(self.actual)

        #add new rows to layout
        self.layout.add_widget(self.row1)
        self.layout.add_widget(self.row2)
#        self.layout.add_widget(self.row3)
        self.canvas.add_widget(self.tabs)
        self.layout.pos = (45,190)
        self.tabs.pos=(55,185)

    
    def _set_as_a(self, value): 
        self.ctrl.As_a = value.value
    
    
    def _set_want_to(self, value): 
        self.ctrl.Want_to = value.value
    
    
    def _set_so_that(self, value): 
        self.ctrl.So_that = value.value
    
    
    def _set_estimate(self, value): 
        self.ctrl.Estimate = value
    
    
    def _set_actual(self, value): 
        self.ctrl.Actual = value

    def _set_owner(self, value): 
        self.ctrl.Owner = value


         
def pymt_plugin_activate(root, ctx):
    pass


def pymt_plugin_deactivate(root, ctx):
    root.remove_widget(ctx.ui)


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
    @property
    def description(self):
        if self.view is None: return ''
        return self.view.description
    @property
    def name(self):
        if self.view is None: return ''
        return self.view.name
    def createView(self):
        if self.isMinimal:
            self.view = MinStoryView(self.root,self, 
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
            self.view = StoryView(self.root,self, 
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
class Dummy(object):
    def __init__(self,root):
        self.grid_size = minimal_size
        story_size = scale_tuple(self.grid_size, 0.2)
        self._name = 'name'
        self._description = 'description'
        self.font_height = 13 * 2
        self._full_width =  int(story_size[0])# - (self.padding * 1))
        #self.layout = MTBoxLayout(size=story_size)
        sz=(self._full_width - int(len('Story Name: ')*pixels),self.font_height)
        self.story_name=MTTextInput(label=self._name,id='story_name_id',size=sz)
        #self.layout.add_widget(MTLabel(label='Story Name:'))
        #self.layout.add_widget(self.story_name)
        #self.layout.pos = (25,200)#(20, 0)#-(text_height*.01))
        #root.add_widget(self.layout)
        root.add_widget(self.story_name)
        self.story_name.label=self._name
 
if __name__ == '__main__':
    import sys
    args = sys.argv
    mw = MTWindow()
    c = TestController(mw,args[1])
    mw.size = scale_tuple(get_min_screen_size(),.045)
    runTouchApp()
