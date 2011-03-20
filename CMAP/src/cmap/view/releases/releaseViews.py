'''
Created on Sep 29, 2010

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
    from petaapan.utilities.console_logger import ConsoleLogger
    Log = ConsoleLogger('CMAP')
from cmap.tools.myTools import get_min_screen_size, scale_tuple
from cmap.tools.uniqueID import uuid
from pymt.ui.window import MTWindow
from pymt.base import runTouchApp
from cmap.view.baseViews import MinView


class ReleaseMinView(MinView):
    def __init__(self,wnd,ctrl, **kwargs):
        kwargs.setdefault('name','')
        kwargs.setdefault('minimized_label', kwargs['name'])
        super(ReleaseMinView,self).__init__(wnd,ctrl,**kwargs)
class ReleaseView(ReleaseMinView):pass
class TestController(object):
    def __init__(self, w, minv, **kwargs):
        self.screen_size = get_min_screen_size()
        self.isMinimal = True if minv == 'minimal' else False
        self.root = w 
        self.view = None
        self.story_view_size = None
        self.id = uuid()
        self.createView()
    @property
    def name(self):
        return ''
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
    @property
    def Id(self):
        return None
    def createView(self):
        if self.isMinimal:
            self.view = ReleaseMinView(self.root,self, 
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
            self.view = ReleaseMinView(self.root,self, 
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
    args = ['','minimal']#sys.argv
    mw = MTWindow()
    c = TestController(mw,args[1])
    mw.size = scale_tuple(get_min_screen_size(),.045)
    runTouchApp()
