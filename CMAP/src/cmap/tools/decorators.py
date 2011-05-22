'''
Created on Aug 4, 2010

@author: stevenson
'''
from pymt.ui.widgets.widget import MTWidget
from pymt.graphx.colors import set_color
#from pymt.graphx.draw import drawRoundedRectangle
from pymt.ui.window import MTWindow
from pymt.ui.widgets.scatter import MTScatter
from pymt.base import runTouchApp
from pymt.ui.colors import css_add_sheet
from pymt.graphx.css import drawCSSRectangle
from pymt.ui.widgets.dragable import MTDragable
from pymt.utils import interpolate
from cmap.tools.myTools import scale_tuple, get_min_screen_size
from agileConfig import Config
try:
    from cmap.view.baseViews import MinView
except:
    pass
from pymt.ui.widgets.button import MTImageButton
from pymt import pymt_icons_dir
import os
from pymt.vector import Vector
_iconPath = os.path.join(Config().datastore, '..','icons')#os.path.dirname(__file__)
_minimize_icon_path = os.path.join(_iconPath, 'min.png')
_trash_icon_path = os.path.join(_iconPath,'User-trash.png')
_save_icon_path = os.path.join(_iconPath,'save.png')

StoryCardCSS = '''
.storycardcss {
    bg-color: rgba(100, 155, 255, 255);
    border-color: rgb(100, 75, 200);
    border-width: 50;
    draw-border: True;    
}
.storycardcss1 {
    bg-color: rgba(70, 155, 235, 255);
    border-color: rgb(180, 75, 200);
    border-width: 50;
    draw-border: True;    
}
.borderwrapcss {
    border-color: rgb(0, 255, 255);
    bg-color: rgba(0, 155, 235, 30);
    border-width: 5;
    draw-border: False;
}    
.ctrlcss {
    border-color: rgb(75, 255, 255);
    border-width: 1;
    draw-border: True;    
}
'''
CYAN='rgb(0,255,255)'
css_add_sheet(StoryCardCSS)

class MyDragableContainer(MTDragable):
    def __init__(self, widget,isDragable, **kwargs):
        super(MyDragableContainer, self).__init__(**kwargs)
        self.widget = widget
        self.widget_is_dragable = isDragable
        self.add_widget(self.widget)
        self.down_touch_pos = None
        self.up_touch_pos = None
        if 'use_widget_size' in kwargs:
            if not kwargs['use_widget_size']:
                self.size_scaler = kwargs['size_scaler']
            else:
                self.size_scaler = (1,1)
        else:
            self.size_scaler = (1,1)
        self.size = scale_tuple(self.widget.size,self.size_scaler[0],
                                self.size_scaler[1])
    def on_update(self):
        self.widget.pos = interpolate(self.widget.pos, self.pos)
        self.size = interpolate(self.size, self.widget.size)
        super(MyDragableContainer, self).on_update()
    def on_touch_down(self, touch):
        print('Down: Draggable state: %s:  Id: %s' % (self.state, touch.id))
        if super(MyDragableContainer,self).on_touch_down(touch):
            #print('Down: super returned True')
            self.widget.on_touch_down(touch)
            return True
        if self.widget_is_dragable and self.state == 'dragging':
            if self.widget.on_touch_down(touch):
                self.state = 'internal'
            #print('Down: changed state to internal')
            return True
        print('Down: Ignored')
        return False
    def on_touch_move(self, touch):
        #print('Move: Draggable state: %s   Id: %s' % (self.state, touch.id))
        if self.state == 'dragging' or self.state == 'really_dragging':
            self.state = 'really_dragging' 
            return super(MyDragableContainer,self).on_touch_move(touch)
        elif self.state == 'internal':
            self.state = 'internal_dragging'
            return True#self.widget.dispatch_event('on_touch_move',touch)
        elif self.state == 'internal_dragging':
            return True#self.widget.dispatch_event('on_touch_move',touch)
    def on_touch_up(self, touch):
        print('Up: Draggable state: %s   Current: %s:  Id: %s' % \
              (self.state, str(touch.grab_current), touch.id))
        prop = False
        if self.state == 'dragging':
            prop = True
        if super(MyDragableContainer,self).on_touch_up(touch):
            #print('Up: sending touch_down to child')
            if prop:
                self.widget.on_touch_up(touch)
            return True
        if self.state == 'internal_dragging':
            self.state = 'normal'
            print('Up: Reset internal state to normal')
            return True
        if self.state == 'internal':# or self.state == 'dragging':
            self.widget.on_touch_up(touch)
            self.state = 'normal'
            return True
            #self.widget.dispatch_event('on_touch_up',touch)
        print('Up: Ignored')
        return False
class Controls(MTWidget):
    def __init__(self,root=None,ctrls=None,**kwargs):
        self.ctrls_buttons_width = kwargs.setdefault('ctrls_button_width',0)
        self.ctrls_buttons_height = kwargs.setdefault('ctrls_button_heigth',0)
        self.control_scale = kwargs.setdefault('control_scale',1)
        self.scale = kwargs.setdefault('scale',1)
        #kwargs['cls'] = 'ctrlcss'
        
        super(Controls,self).__init__(**kwargs)
        if root:
            self.parent = root
        for b in ctrls:
            self.add_widget(b)
        self.update_controls()
    def add_btn_size(self,btn):
        try:
            pad = btn.my_padding
        except:
            pad = btn.my_padding = 5
        self.ctrls_buttons_width += btn.width + pad
        self.ctrls_buttons_height = max(self.ctrls_buttons_height, 
                                        btn.height + pad *2) 
    def del_btn_size(self,btn):
        try:
            pad = btn.my_padding
        except:
            pad = btn.my_padding = 5
        self.ctrls_buttons_width -= btn.width + pad
        self.ctrls_buttons_height = max(self.ctrls_buttons_height, 
                                        btn.height + pad *2) 
    def place(self, x,y):
        self.center = self.parent.center[0], y + self.height/2
        self.update_controls()
    def update_controls(self):
        ctrl_center = self.center#self.to_window(*self.center) 
        center_x = ctrl_center[0]
        center_y = ctrl_center[1]
        ctrls  = self.children
        start_pos_x = center_x - (self.ctrls_buttons_width/2)
            
        for button in ctrls:
            button.scale = self.control_scale / self.scale
            button.pos = start_pos_x,center_y - (button.height / 2)
            try:
                pad = button.my_padding
            except:
                pad = button.my_padding = 5 # set a default
            start_pos_x += button.width + pad
    def add_widget(self, w):
        super(Controls,self).add_widget(w)
        self.add_btn_size(w)
        self.size = scale_tuple(
                    (self.ctrls_buttons_width,self.ctrls_buttons_height),-.2)
    def remove_widget(self, w):
        super(Controls,self).remove(w)
        self.del_btn_size(w)
        self.size = scale_tuple(
                    (self.ctrls_buttons_width,self.ctrls_buttons_height),-.2)
    def to_local(self, x, y, **k):
        return super(Controls,self).to_local(*self.to_window(x, y),**k)

class Border2(MTScatter):
    def __init__(self,widget, **kwargs):
        #get the widget border color if any
        self.my_state = 'normal'
        self.widget_is_dragable = True
        self.controls = kwargs.get('ctrls', None)
        self.ctrls_height = 0
#        bc = kwargs.setdefault('border-color',self.shade_of(\
#                                            widget.style.get('border-color', 
#                            widget.style.get('bg-color',parse_color(CYAN)))))
        bc = widget.style['border-color']
        kwargs.setdefault('style', {'bg-color':self.shade_of(bc),
#                                'border-color':kwargs['border-color'],
#                                'draw-border': True,
                                'draw-background': True})
        kwargs.setdefault('size_scaler', (-1.1,-.1))
        kwargs['use_widget_size'] = False
        self.widget = widget
        if 'use_widget_size' in kwargs:
            if not kwargs['use_widget_size']:
                self.size_scaler = kwargs['size_scaler']
            else:
                self.size_scaler = (1,1)
        else:
            self.size_scaler = (1,1)
        kwargs.setdefault('size', 
                          scale_tuple(self.widget.size,self.size_scaler[0],
                                self.size_scaler[1]))
        super(Border2, self).__init__(**kwargs)
        if self.controls is not None:
            if not self.controls.parent:
                self.add_widget(self.controls)
            self.ctrls_height = self.controls.ctrls_buttons_height
        self.add_widget(self.widget)#????
        self.place_widget()
        self.place_controls()
        #self.widget.bring_to_front()
    def shade_of(self,color):
        c = []
        for rgb in color:
            c.append(rgb)
        c[0] = color[2] - 0.01
        c[2] = color[0] - 0.03
        c[3] = 0.78
        #color[0] -= 0.1
        return c
    def place_widget(self):
        self.widget.center = (self.center[0], 
                              self.center[1] + int(self.ctrls_height/5))
        
    def place_controls(self):
        self.controls.place(self.bottomcenter[0],self.bottomcenter[1])
    def collide_widget(self, x, y):
        '''Call this method only after collide_point returns true to see if 
        touch is on widget'''
        if self.widget.collide_point(x,y):
            return True
    def collide_border(self,x,y):
        '''Call this method only after collide_point returns true to see if 
        touch was on the border including control area''' 
        if self.collide_widget(x,y):
            return False
        return True
    def on_touch_down(self, touch):
        self.my_state = 'down'
        x,y = touch.pos
        if self.collide_point(x, y):
            if self.collide_border(x, y):
                touch.grab(self)
                self.my_state = 'dragging'
                touch.userdata['touch_offset'] = Vector(self.pos)-touch.pos
                #check if this touch is no the controls
                if self.controls.on_touch_down(touch):
                    self.my_state = 'controls'
                    print('Down state:%s:Id:%s'%(self.my_state,touch.id))
                else:
                    print('Down state:%s:Id:%s'%(self.my_state,touch.id))
            elif self.collide_widget(x, y):
                if self.widget.on_touch_down(touch):
                    touch.grab(self)
                    self.my_state = 'internal'
            return True
        self.my_state = 'normal'
        print('Down: Ignored')
    def on_touch_move(self, touch):
        if touch.grab_current == self:
            if self.my_state == 'dragging' or self.my_state=='really_dragging':
                self.my_state = 'really_dragging' 
                self.pos = touch.userdata['touch_offset'] + touch.pos
                self.place_widget()
                if self.controls:
                    self.place_controls()
                return True
            elif self.my_state in ['internal', 'internal_dragging']:
                self.my_state = 'internal_dragging'
                return True
            elif self.my_state in ['controls', 'controls_dragging']:
                self.my_state = 'controls_dragging'
                return True
    def on_touch_up(self, touch):
        if touch.grab_current == self:
            print('Up, state: %s   Current: %s:  Id: %s' % \
                  (self.my_state, str(touch.grab_current), touch.id))
            if self.my_state == 'controls':
                self.controls.on_touch_up(touch)
            elif self.my_state == 'internal':
                self.widget.on_touch_up(touch)
            touch.ungrab(self)
            self.my_state = 'normal'
            return True
        print('Up: Ignored')
        
    def draw(self):
        set_color(*self.style['bg-color'])
        drawCSSRectangle(pos=self.pos, size=self.size,style=self.style)
        #self.widget.bring_to_front()
    def on_draw(self):
            self.draw()
            self.widget.dispatch_event('on_draw')
            self.controls.dispatch_event('on_draw')
def trash(w):
    print('Trash')
def minimize(w):
    print('Minimize')
def save(w):
    print('Save')
def fullscreen(w):
    print('Fullscreen')
def close(w):
    print('Close')
def newStory(w):
    _p = MinView(w,None,type_name='Story',name = '',minimized_label='')
    _p.title = '%s: %s' % ('Stories', 'Story')
    _p.parent = w
    _p.size = _p.grid_size #scale_tuple(_p.grid_size,-0.1,-0.1)
    return _p        
def getControls():
    l = []
    b = MTImageButton(
            filename=pymt_icons_dir + 'fullscreen.png',
            cls='innerwindow-fullscreen')
    b.push_handlers(on_release=fullscreen)
    l.append(b)
    b = MTImageButton(
            filename=pymt_icons_dir + 'stop.png',
            cls='innerwindow-close')
    b.push_handlers(on_release=close)
    l.append(b)
    b = MTImageButton(filename=_minimize_icon_path,
                                        scale=1,
                                        cls='innerwindow-close')
    b.my_padding = 5
    b.push_handlers(on_release=minimize)
    l.append(b)
    b = MTImageButton(filename=_trash_icon_path,
                                        scale=1,
                                        cls='innerwindow-close')
    b.my_padding = 12
    b.push_handlers(on_release=trash)
    l.append(b)
    b = MTImageButton(filename=_save_icon_path,
                                        scale=1,
                                        cls='innerwindow-close')
    b.my_padding = 5 
    b.push_handlers(on_release=save)
    l.append(b)
#    b1.push_handlers('on_press', lambda x: x)
    c = Controls(None,l)
    return c
if __name__ == '__main__':
    w = MTWindow()
    w.size = get_min_screen_size()
    #s = MTSlider(size=(500,500),pos=(150,150), cls='storycardcss')
#    ctrl = ProjectCtrl(w, story_parent=None)
#    s = ctrl.view
#    s = MTSlider(cls='storycardcss')
    s = newStory(w)
    #b = BorderWrap(s, pos=(190,190), size_scaler=(-.2,-.3))#, cls='borderwrapcss')
    #b.pos = (200,200)
    #c= MTScatter(size=(250,250), pos=(400,400),cls='storycardcss')
    c = getControls()
#    w.add_widget(c)
    b = Border2(s, ctrls=c,pos=(190,190), size_scaler=(-.2,-.35))
    w.add_widget(b)
    
    runTouchApp()
    
#===============================================================================
# class Controls(MTScatter):
#    def __init__(self,root=None,ctrls=None,**kwargs):
#        self.ctrls_buttons_width = kwargs.setdefault('ctrls_button_width',0)
#        self.ctrls_buttons_height = kwargs.setdefault('ctrls_button_heigth',0)
#        self.control_scale = kwargs.setdefault('control_scale',1)
#        #self.scale = kwargs.setdefault('scale',1)
#        kwargs['cls'] = 'ctrlcss'
#        
#        super(Controls,self).__init__(**kwargs)
#        if root:
#            self.parent = root
#        for b in ctrls:
#            self.add_widget(b)
# #        self.size = scale_tuple(
# #                    (self.ctrls_buttons_width,self.ctrls_buttons_height),-.2)
#        self.update_controls()
#    def add_btn_size(self,btn):
#        try:
#            pad = btn.my_padding
#        except:
#            pad = btn.my_padding = 5
#        self.ctrls_buttons_width += btn.width + pad
#        self.ctrls_buttons_height = max(self.ctrls_buttons_height, 
#                                        btn.height + pad *2) 
#    def del_btn_size(self,btn):
#        try:
#            pad = btn.my_padding
#        except:
#            pad = btn.my_padding = 5
#        self.ctrls_buttons_width -= btn.width + pad
#        self.ctrls_buttons_height = max(self.ctrls_buttons_height, 
#                                        btn.height + pad *2) 
#    def place(self, x,y):
#        self.center = (self.parent.center[0], y + self.height/2)
#    def update_controls(self):
#        ctrl_center = self.center 
#        center_x = ctrl_center[0]
#        center_y = ctrl_center[1]
#        ctrls  = self.children
#        start_pos_x = center_x - (self.ctrls_buttons_width/2)
#            
#        for button in ctrls:
#            button.scale = self.control_scale / self.scale
#            button.pos = self.to_local(start_pos_x,center_y - (button.height / 2))
#            try:
#                pad = button.my_padding
#            except:
#                pad = button.my_padding = 5 # set a default
#            start_pos_x += button.width + pad
#    def on_transform(self, touch):
#        self.update_controls()
#        return True
#    def add_widget(self, w):
#        super(Controls,self).add_widget(w)
#        self.add_btn_size(w)
#        self.size = scale_tuple(
#                    (self.ctrls_buttons_width,self.ctrls_buttons_height),-.2)
#    def remove_widget(self, w):
#        super(Controls,self).remove(w)
#        self.del_btn_size(w)
#        self.size = scale_tuple(
#                    (self.ctrls_buttons_width,self.ctrls_buttons_height),-.2)
#    def to_local(self, x, y, **k):
#        x1,y1  = super(Controls,self).to_local(x,y,**k)
#        if x1 < 0 or y1 < 0:
#            return super(Controls,self).to_local(*self.to_window(x, y),**k)
#        return (x1,y1)
#===============================================================================

#===============================================================================
# class BorderWrap(MyDragableContainer):
#    def __init__(self,widget, **kwargs):
#        #get the widget border color if any
#        #widget.reload_css()
#        kwargs.setdefault('border-color',
#                          widget.style.get('border-color', 
#                            widget.style.get('bg-color',parse_color(CYAN))))
#        kwargs.setdefault('style', {'bg-color':kwargs['border-color'],
#                                'border-color':kwargs['border-color'],
#                                'draw-border': True,
#                                'draw-background': True})
#        kwargs.setdefault('size_scaler', (-1.1,-.1))
#        kwargs['use_widget_size'] = False
#        super(BorderWrap, self).__init__(widget,False,**kwargs)
#    def collide_point(self, x, y):
#        '''Test if the (x,y) is somewhere in the border i.e. not on the 
#        contained widget'''
#        if not self.visible:
#            return False
#        if self.widget.collide_point(x,y):
#            if self.state in ['internal','normal']:#,'internal_dragging']:
#                return True
#            else:
#                return False
#        if super(MyDragableContainer,self).collide_point(x,y):
#            return True
#        
#    def draw(self):
#        set_color(*self.style['bg-color'])
#        drawCSSRectangle(pos=self.pos, size=self.size,style=self.style)
#    def on_draw(self):
#            self.draw()
#            self.widget.dispatch_event('on_draw')
#===============================================================================
        
#===============================================================================
# class Controls1(MTScatter):
#    def __init__(self,ctrls=None,**kwargs):
#        kwargs['cls'] = 'storycardcss1'
#        self.controls = MTWidget()
#        self.ctrls_buttons_width = kwargs.setdefault('ctrls_button_width',0)
#        self.ctrls_buttons_height = kwargs.setdefault('ctrls_button_heigth',0)
#        for b in ctrls:
#            self.controls.add_widget(b)
#            self.add_btn_size(b)
#        self.control_scale = kwargs.setdefault('control_scale',1)
#        super(Controls,self).__init__(**kwargs)
#        super(Controls,self).add_widget(self.controls)
#        self.size = scale_tuple(
#                    (self.ctrls_buttons_width,self.ctrls_buttons_height),-.2)
#        self.update_controls()
#    def add_btn_size(self,btn):
#        try:
#            pad = btn.my_padding
#        except:
#            pad = btn.my_padding = 5
#        self.ctrls_buttons_width += btn.width + pad
#        self.ctrls_buttons_height = max(self.ctrls_buttons_height, 
#                                        btn.height + pad *2) 
#        
#    def update_controls(self):
#        ctrl_center = (self.ctrls_buttons_width/2 * self.control_scale,
#                       self.ctrls_buttons_height/2 * self.control_scale)
#        center_x = ctrl_center[0]
#        center_y = ctrl_center[1]
#        ctrls  = self.controls.children
#        start_pos_x = center_x - (ctrl_center[0]/2)
#            
#        for button in ctrls:
#            button.scale = self.control_scale / self.scale
#            button.pos = start_pos_x,center_y - (button.height / 2)
#            try:
#                pad = button.my_padding
#            except:
#                pad = button.my_padding = 5 # set a default
#            start_pos_x += button.width + pad
#                
#    def add_widget(self, w):
#        self.controls.add_widget(w)
#        self.add_btn_size(w)
#        self.size = scale_tuple(
#                    (self.ctrls_buttons_width,self.ctrls_buttons_height),-.2)
# 
#    def remove_widget(self, w):
#        self.controls.remove(w)
#===============================================================================

#===============================================================================
# class Border1(MTScatter):
#    def __init__(self,widget, **kwargs):
#        #get the widget border color if any
#        self.my_state = 'normal'
#        self.widget_is_dragable = True
#        self.controls = kwargs.get('ctrls', None)
#        kwargs.setdefault('border-color',
#                          widget.style.get('border-color', 
#                            widget.style.get('bg-color',parse_color(CYAN))))
#        kwargs.setdefault('style', {'bg-color':kwargs['border-color'],
#                                'border-color':kwargs['border-color'],
#                                'draw-border': True,
#                                'draw-background': True})
#        kwargs.setdefault('size_scaler', (-1.1,-.1))
#        kwargs['use_widget_size'] = False
#        self.widget = widget
#        if 'use_widget_size' in kwargs:
#            if not kwargs['use_widget_size']:
#                self.size_scaler = kwargs['size_scaler']
#            else:
#                self.size_scaler = (1,1)
#        else:
#            self.size_scaler = (1,1)
#        kwargs.setdefault('size', 
#                          scale_tuple(self.widget.size,self.size_scaler[0],
#                                self.size_scaler[1]))
#        super(Border1, self).__init__(**kwargs)
#        if self.controls is not None:
#            if not self.controls.parent:
#                self.add_widget(self.controls)
#    def move(self,x=0,y=0):
#        #self.pos = interpolate(self.pos,(x,y))
#        self.widget.center = interpolate(self.widget.center,(self.center[0],
#                                                    self.center[1] + 16))
#    def on_update(self):
#        self.move(*self.center)
#        #self.widget.center = self.center#interpolate(self.widget.center,
#        #self.center)
#        if self.size != scale_tuple(self.widget.size,self.size_scaler[0],
#                                self.size_scaler[1]):
#            self.size = interpolate(self.size,
#                        scale_tuple(self.widget.size,self.size_scaler[0],
#                                self.size_scaler[1])) 
#        self.controls.pos = (self.x +10,self.y)
#        #super(Border1, self).on_update()
#        self.widget.on_update()
#    def collide_point(self, x, y):
#        '''Test if the (x,y) is somewhere in the border i.e. not on the 
#        contained widget'''
#        if not self.visible:
#            return False
#        if self.widget.collide_point(x,y):
#            if self.my_state in ['internal','normal']:#,'internal_dragging']:
#                return True
#            else:
#                return False
# #            return True
#        if super(Border1,self).collide_point(x,y):
#            return True
#    def on_touch_down(self, touch):
#        self.my_state = 'down'
#        if self.collide_point(*touch.pos):
#            print('Down: Draggable state: %s:  Id: %s' % (self.my_state,
#                                                                    touch.id))
#            #ceck if this touch is no the controls
#            touch.grab(self)
#            if self.controls.on_touch_down(touch):
#                self.my_state = 'controls'
#                return True
#            else:
#                self.my_state = 'dragging'
#                touch.userdata['touch_offset'] = Vector(self.pos)-touch.pos
#                return True
#        elif self.widget.on_touch_down(touch):
#            touch.grab(self)
#            self.my_state = 'internal'
#            return True
# #        if self.widget_is_dragable and self.my_state == 'dragging':
# #            if self.widget.on_touch_down(touch):
# #                self.my_state = 'internal'
# #            #print('Down: changed state to internal')
# #            return True
#        print('Down: Ignored')
#    def on_touch_move(self, touch):
#        if touch.grab_current == self:
#            if self.my_state == 'dragging' or self.my_state=='really_dragging':
#                self.my_state = 'really_dragging' 
#                self.pos = interpolate(self.pos, 
#                                       touch.userdata['touch_offset'] + touch.pos)
#                self.widget.center = interpolate(self.widget.center,self.center)
#                return True
#            elif self.my_state in ['internal', 'internal_dragging']:
#                self.my_state = 'internal_dragging'
#                return True
#            elif self.my_state in ['controls', 'controls_dragging']:
#                self.my_state = 'controls_dragging'
#                return True
#    def on_touch_up(self, touch):
#        if touch.grab_current == self:
#            print('Up: Draggable state: %s   Current: %s:  Id: %s' % \
#                  (self.my_state, str(touch.grab_current), touch.id))
#            if self.my_state == 'controls':
#                self.controls.on_touch_up(touch)
#            elif self.my_state == 'internal':
# #            if super(Border1,self).on_touch_up(touch):
#                self.widget.on_touch_up(touch)
#            touch.ungrab(self)
#            self.my_state = 'normal'
#            return True
#        print('Up: Ignored')
#        
#    def draw(self):
#        set_color(*self.style['bg-color'])
#        drawCSSRectangle(pos=self.pos, size=self.size,style=self.style)
#    def on_draw(self):
#            self.draw()
#            self.widget.dispatch_event('on_draw')
#            self.controls.dispatch_event('on_draw')
#===============================================================================
