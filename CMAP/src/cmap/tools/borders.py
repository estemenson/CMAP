# -*- coding: utf-8 -*-
'''
Created on Aug 5, 2010

@author: stevenson
'''
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from agileConfig import Config
from cmap.tools.decorators import MyDragableContainer
from cmap import AGILE_ICONS
from pymt.ui.widgets.composed.vkeyboard import MTVKeyboard
try:
    Log = Config().log.logger
except Exception: #IGNORE:W0703
    from petaapan.utilities.console_logger import ConsoleLogger
    Log = ConsoleLogger('CMAP')


from pymt.ui.widgets.composed.innerwindow import MTInnerWindow
from pymt.ui.window import MTWindow
from pymt.base import runTouchApp
from pymt.ui.colors import css_add_sheet
from pymt.graphx.colors import set_color
from pymt.graphx.draw import drawRoundedRectangle, drawLabel
from pymt.ui.widgets.button import MTImageButton
import os
from cmap.tools.myTools import scale_tuple
from pymt.parser import parse_color

InnerWindowCSS = '''
.type1css {
    bg-color: rgba(192, 192, 192, 255);
    border-width: 30;
    border-color: rgba(192,192,192,255);
    min-border-color:rgba(205,0,0,80);
    font-color: rgba(0,0,0,255);
    draw-border: True;    
    bg-color-move: rgb(45 ,150 ,150);
    bg-color-full: rgb(145 ,180 ,150);
}
.type2css {
    bg-color: rgba(211, 211, 211, 255);
    border-color: rgb(180, 75, 200);
    border-width: 10;
    draw-border: True;    
}
'''

css_add_sheet(InnerWindowCSS)
_iconPath = AGILE_ICONS #os.path.dirname(__file__)
_minimize_icon_path = os.path.join(_iconPath, 'min.png')
_trash_icon_path = os.path.join(_iconPath,'User-trash.png')
_save_icon_path = os.path.join(_iconPath,'save.png')
#_close_icon_oath = os.path.join(_iconPath,'close.png')
#_maximize_icon_path = os.path.join(_iconPath,'maximize.png')
x_ctrl_border_scale = -.1
y_ctrl_border_scale = -.2

class MyInnerWindow(MTInnerWindow):
    def __init__(self, **kwargs):
        ctrl_scale = kwargs.setdefault('control_scale', 1.0)
        self.btn_minimize = MTImageButton(filename=_minimize_icon_path,
                                            scale=ctrl_scale,
                                            cls='innerwindow-close')
        self.btn_minimize.my_padding = 5
        self.isMinimized = False
        sz = self.ctrls_buttons_size = kwargs.setdefault('ctrls_button_size', 
                                                         (0,48*ctrl_scale))
        kwargs['ctrls_button_size'] = (sz[0] + (3* self.btn_minimize.width) + \
                                    2* self.btn_minimize.my_padding , sz[1])
        self.ctrls_buttons_size = kwargs['ctrls_button_size'] 
        super(MyInnerWindow,self).__init__(**kwargs)
        self.minimized_label =kwargs.setdefault('minimized_label','test label')
        self.old_pos = self.pos
        self.old_size = (0,0)
        self.old_minimize_pos = None
        self.ctrl_buttons_width = self.ctrls_buttons_size[0] 
        self.btn_minimize.push_handlers(on_release=self.minimize)
        #remove the close control button and addit again after the minimize
        btn = self.controls.children.pop()
        self.controls.add_widget(self.btn_minimize)
        self.controls.add_widget(btn)
        self.update_controls()
        
    def update_controls(self):
        scaled_border = self.get_scaled_border()
        center_x = self.width/ 2
        center_y = - scaled_border 
        if self.isMinimized:
            center_y = scaled_border
        ctrls  = self.controls.children
        pos =(center_x-self.ctrls_buttons_size[0]/2 -
              (scaled_border/2*self.scale),# if self.scale != 1 else scaled_border,
                   center_y)
        start_pos_x = pos[0]
        for button in ctrls:
            button.scale = self.control_scale / self.scale
            #button.scale = self.scale * self.control_scale
            button.pos = start_pos_x,center_y - (button.height / (2*self.scale))
            try:
                my_padding = button.my_padding
            except Exception: #IGNORE:W0703
                my_padding = button.my_padding = 5 # set a default
            start_pos_x += (button.width + my_padding)
                
       
    def minimize(self, touch=[]):
        if self.isMinimized:
            self.restore()
        else: 
            self.isMinimized = True
            self.container.hide()
            self.old_pos = self.pos
            self.pos = self.get_minimize_pos()
            self.old_size = self.size
            self.size = (self.ctrls_buttons_size[0] * self.scale,
                         self.ctrls_buttons_size[1] * self.scale)
            

    def get_minimize_pos(self):
        if self.old_minimize_pos: return self.old_minimize_pos
        scaled_border = self.get_scaled_border()
        center_x = self.width / 2
        center_y = scaled_border
        return (center_x, center_y) 

        
    def restore(self):
        self.isMinimized = False
        self.container.show()
        self.old_minimize_pos = self.pos
        self.pos = self.old_pos
        self.size = self.old_size
        
        
    def fullscreen(self, *largs, **kwargs):
        if self.isMinimized:
            self.restore()
        super(MyInnerWindow,self).fullscreen(*largs, **kwargs)
        
        
    def draw(self):
        scaled_border = self.get_scaled_border()
        border_color=self.style.get('border-color')
        if not self.isMinimized:
            # select color from number of touch
            if len(self._touches) == 0:
                set_color(*self.style.get('bg-color'))
            elif len(self._touches) == 1:
                border_color = self.style.get('bg-color-move') 
                set_color(*border_color) #IGNORE:W0142
            else:
                border_color = self.style.get('bg-color-full') 
                set_color(*border_color) #IGNORE:W0142

            # draw border
            pos = (-scaled_border, -scaled_border*2*self.scale)
            drawRoundedRectangle(
                pos=pos,
                size=(self.width+scaled_border*2, self.height+scaled_border*3*self.scale),
                #size=(self.width+scaled_border*2, self.height+control_height*2),
                radius=15. / self.scale
            )
            # draw title
            l_pos = ( 40, self.height + 15)
            drawLabel(label=self.minimized_label, pos=l_pos,
                           color=parse_color('rgba(255,0,0,255)'), font_size=18)
#            pos = ((self.width/2 - control_width/2),
#                   -scaled_border * 2)
#            size=(control_width, 
#                  control_height) 
#            corners=(True, True, False, False)
        else:
            pos = (0,-scaled_border)
            size=scale_tuple(self.size,-.1,-.5)
            l_pos = (size[0]/2, size[1] - 15 - scaled_border)
            corners=(True, True, True, True)
            c = self.style.get('min-border-color') 
            border_color=parse_color(c if c is not None else 'rgba(192,192,192,255)')
            # draw control background
            drawRoundedRectangle(
               pos=pos,
                size=size,
                radius=15. / self.scale,
                corners=corners, color=border_color
            )
            c = self.style.get('font-color')
            drawLabel(label=self.minimized_label, pos=l_pos, 
                      color=parse_color(c if c is not None else 'rgba(255,0,0,255)'),
                      font_size=14)
        #self.update_controls()
        

    def collide_point(self,x,y):
        return super(MyInnerWindow,self).collide_point(x,y) or \
                self.collide_controls(x,y)       
    def collide_controls(self, x,y):
        scaled_border = self.get_scaled_border()
        if not self.isMinimized:
            #now calculate the rectangle size and pos of the rectangle that
            #surrounds the controls based on their size
#            _ctrl_w,_ctrl_h= ((self.width/2)-(control_size[0]/2),\
#                   -scaled_border * 2)
#            _ctrl_x,_ctrl_y=scale_tuple(control_size, x_ctrl_border_scale,
#                                        y_ctrl_border_scale) 
            #now calculate the bounding box using the controls rectangle
            #and the innerWindow's position
            x,y = super(MyInnerWindow, self).to_local(x, y)  
            _x,_y =(-scaled_border, -scaled_border*2*self.scale)
            _w,_h =(self.width+scaled_border*2, self.height+scaled_border*3*self.scale)
#            _x = self.x + _ctrl_x -scaled_border*2 -2
#            _w = _ctrl_w + scaled_border*2
#            _y = self.y + _ctrl_h
#            _h = abs(_ctrl_h) +scaled_border
        else:
            _x = self.x #-scaled_border*2 -2
            _w = self.width + scaled_border*2
            _y = self.y #+ self.height
            _h = abs(self.height) +scaled_border
            
        if x >= _x \
                and x <= (_x + _w) \
                and y >= _y \
                and y <= (_y + _h):
            return True
        return False 

    
class MyDragebleInnerWindow(MyInnerWindow):
    def __init__(self, **kwargs):
        self.drag_widget = MyDragableContainer(self,False)
        self.ctrl_buttons_width = None
#        self.btn_save = MTImageButton(filename=_save_icon_path,
#                                            scale=1,
#                                            cls='innerwindow-close')
#        sz = self.ctrls_buttons_size = kwargs.setdefault('ctrls_button_size',
#                                                         (0,48))
#        kwargs['ctrls_button_size'] = (sz[0] + self.btn_save.width, sz[1])
#        self.ctrls_buttons_size = kwargs['ctrls_button_size'] 
        super(MyDragebleInnerWindow,self).__init__(**kwargs)
        self.update_controls()

    def on_update(self):
        self.drag_widget.update()
        super(MyDragebleInnerWindow,self).on_update()
    
    
class MyInnerWindowWithTrash(MyInnerWindow):
    def __init__(self, **kwargs):
        self.btn_trash = MTImageButton(filename=_trash_icon_path,
                                            scale=1,
                                            cls='innerwindow-close')
        self.btn_trash.my_padding = 12
        sz = self.ctrls_buttons_size = kwargs.setdefault('ctrls_button_size', 
                                                         (0,48))
        kwargs['ctrls_button_size'] = (sz[0] + self.btn_trash.width + \
                                       self.btn_trash.my_padding, sz[1])
        self.ctrls_buttons_size = kwargs['ctrls_button_size'] 
        super(MyInnerWindowWithTrash,self).__init__(**kwargs)
        self.btn_trash.scale = self.control_scale
        self.btn_trash.push_handlers(on_release=self.trash)
        self.controls.add_widget(self.btn_trash)
        self.update_controls()
       
    def trash(self, touch=None, *largs, **kwargs):
        pass
            
class MyInnerWindowWithSaveAndTrash(MyInnerWindowWithTrash):
    def __init__(self, **kwargs):
        self.ctrl_buttons_width = None
        self.btn_save = MTImageButton(filename=_save_icon_path,
                                            scale=1,
                                            cls='innerwindow-close')
        self.btn_save.my_padding = 5
        sz = self.ctrls_buttons_size = kwargs.setdefault('ctrls_button_size',
                                                         (0,48))
        kwargs['ctrls_button_size'] = (sz[0] + self.btn_save.width +
                                       self.btn_save.my_padding, sz[1])
        self.ctrls_buttons_size = kwargs['ctrls_button_size'] 
        super(MyInnerWindowWithSaveAndTrash,self).__init__(**kwargs)
        self.btn_save.scale = self.control_scale
        self.btn_save.push_handlers(on_release=self.save)
        self.controls.add_widget(self.btn_save)
        self.update_controls()
       
    def save(self, touch=None):
        pass

class MyInnerWindowWithKeyboard(MyInnerWindowWithSaveAndTrash):
    def update_controls(self):
        scaled_border = self.get_scaled_border()
        center_x = self.width/ 2
        center_y = - scaled_border 
        if self.isMinimized:
            center_y = scaled_border
        ctrls  = self.controls.children
        pos =(center_x-self.ctrls_buttons_size[0]/2 -
              (scaled_border/2*self.scale),# if self.scale != 1 else scaled_border,
                   center_y)
        start_pos_x = pos[0]
        keyboard = None
        for button in ctrls:
            if (isinstance(button, MTVKeyboard)):
                keyboard = button 
                continue
            button.scale = self.control_scale / self.scale
            #button.scale = self.scale * self.control_scale
            button.pos = start_pos_x,center_y - (button.height / (2*self.scale))
            try:
                my_padding = button.my_padding
            except Exception: #IGNORE:W0703
                my_padding = button.my_padding = 5 # set a default
            start_pos_x += (button.width + my_padding)
        if(keyboard):
            keyboard.pos = (pos[0], pos[1] - 55)
    def show_keyboard(self,keyboard):
        self.ctrls_buttons_size = (self.ctrls_buttons_size[0],self.ctrls_buttons_size[1] + keyboard.height) 
        self.controls.add_widget(keyboard)
    def hide_keyboard(self, keyboard):
        self.ctrls_buttons_size = (self.ctrls_buttons_size[0],self.ctrls_buttons_size[1] - keyboard.height) 
        self.controls.remove_widget(keyboard)
    def save(self, touch=None):
        pass
    
if __name__ == '__main__':
    w = MTWindow()
    w.size = (1100,800)
#    b = MyInnerWindow(size=(600,600), pos=(100,150), control_scale=0.7, \
#                      cls='type1css')
#    w.add_widget(b)
#    b = MTInnerWindow(size=(300,300), pos=(40,40), control_scale=0.7, \
#                      cls='type1css')
#    w.add_widget(b)
#    t = MyInnerWindowWithTrash(size=(300,300), pos=(300,425), \
#                control_scale=0.7, cls='type1css')
#    w.add_widget(t)
    cw = MyInnerWindowWithSaveAndTrash(size=(600,600), pos=(100,100), 
                                      control_scale=1, cls='type1css')
    w.add_widget(cw)
#    d = MyDragebleInnerWindow(size=(300,300), pos=(100,200), control_scale=0.7,
#                                        cls='type1css')
#    d1 = MyDragableContainer(d,False)
#    w.add_widget(d1)
    runTouchApp()
