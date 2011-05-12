'''
Created on 2010-10-22

@author: steve
'''
import time
from cmap.tools.myTextInput import MyTextArea
from pymt.ui.widgets.scatter import MTScatter
from cmap.tools.myTools import scale_tuple, get_min_screen_size
from pymt.ui.colors import css_add_sheet
from pymt.vector import Vector
from OpenGL.GL import GL_LINE_LOOP
from pymt.ui.widgets.composed.vkeyboard import MTVKeyboard
from pymt.ui.widgets.sidepanel import MTSidePanel
from pymt.ui.widgets.button import MTImageButton
from pymt.loader import Loader
from pymt.ui.widgets.layout.gridlayout import MTGridLayout
from pymt.parser import parse_color
from cmap import AGILE_ICONS
from agileConfig import Config
try:
    Log = Config().log.logger
except Exception: #IGNORE:W0703
    from petaapan.utilities.console_logger import ConsoleLogger
    Log = ConsoleLogger('CMAP')

from pymt.graphx.draw import drawLine, drawRoundedRectangle
from pymt.utils import curry
from cmap.tools.uniqueID import uuid
ScribbleCSS = '''
.scribbleBordercss {
    border-color: rgb(100, 75, 200);
    border-width: 2;
    draw-border: True;  
    bg-color: rgb(0,0,0);
    draw-background: True;
}
.scribbleKeyboardcss {
    bg-color: rgba(255,255,255,0);
    border-color: rgb(100, 75, 200);
    border-width: 2;
    draw-background: 0;
    draw-border: True;    
    font-size: 16;
}
.scribbleTextAreacss {
    selection-color: rgb(255, 142, 33);
    cursor-color: rgb(215, 15, 15);
}
.mybtn{
    border-color: rgb(130, 130, 130);
    border-color-down: rgb(0, 180, 250);
    color: rgb(230, 230, 230);
    color-down: rgb(255, 255, 255);
    bg-color-down: rgba(0, 80, 160, 240);
    draw-border: 0;
    draw-background: 0;
    draw-alpha-background: 0;
}
.mytextinput {
    color: rgb(255,255,255);
    draw-alpha-background: 0;
    draw-background: 0;
    border-width: 1;
    border-color: rgb(100,100,100);
    border-radius-precision: 1;
    draw-border: 0;
    selection-color: rgb(255, 142, 33);
    cursor-color: rgb(215, 15, 15);

}
'''
css_add_sheet(ScribbleCSS)

from pymt.graphx import set_color
from pymt.ui.widgets.widget import MTWidget


CYAN=parse_color('rgb(0,255,255)')
RED=parse_color('rgb(255,0,0)')
DEFAULT_COLOR=WHITE=parse_color('rgb(255,255,255)')
BLACK=parse_color('rgb(0,0,0)')
DELETED_LINE=parse_color('rgb(30,30,0)')
from os import path
OPEN_SIDE_ICON = path.join(AGILE_ICONS,'arrow-left-double-2.png')
CLOSE_SIDE_ICON = path.join(AGILE_ICONS,'arrow-right-double-2.png')
COLOR_ICON = path.join(AGILE_ICONS,'color_line 48.png')
ERASER_ICON = path.join(AGILE_ICONS,'package_purge 48.png')
PEN_ICON = path.join(AGILE_ICONS,'paint 48.png')


class MySidePanel(MTSidePanel):
    '''
    :Parameters:
        `align` : str, default to 'center'
            Alignement on the side. Can be one of
            'left', 'right', 'top', 'bottom', 'center', 'middle'.
            For information, left-bottom, center-middle, right-top have the
            same meaning.
        `corner_open` : MTWidget object, default to None
            Corner object to use for pulling in the layout. If None
            is provided, the default will be a MTButton() with appropriate
            text label (depend of side)
    '''
    def __init__(self, **kwargs):

        self._close     = None
        self.use_root    = kwargs.get('use_root', True)
        super(MySidePanel, self).__init__(**kwargs)
        self._openImage    = self.corner.image
        self._closeImage = kwargs.get('corner_open', self.corner).image
    def _corner_on_press(self, *largs):
        if self.layout.visible:
            self.corner.image = self._openImage
            self.layout.visible = False
            self.hide()
        else:
            if self._closeImage:
                self.corner.image = self._closeImage
            self.show()
            
        return True

    def get_parent_window(self):
        if not self.use_root:
            return self.parent
        return super(MySidePanel,self).get_parent_window()
    def _get_position_for(self, visible):
        # get position for a specific state (visible or not visible)
        w = self.get_parent_window()
        if not w:
            return

        side = self.side
        x = self.layout.x
        y = self.layout.y
        if visible:
            if side == 'right':
                x = w.width - self.layout.width
            elif side == 'top':
                y = w.height - self.layout.height
            elif side == 'left':
                x = 0
            elif side == 'bottom':
                y = 0
        else:
            if side == 'left':
                x, y = (-self.layout.width, self.y)
            elif side == 'right':
                x, y = (w.width if self.use_root else\
                        self.parent.get_child_pos()[0], self.y) #IGNORE:E1101
            elif side == 'top':
                x, y = (self.x, w.height if self.use_root else\
                        self.parent.get_child_pos()[1]) #IGNORE:E1101
            elif side == 'bottom':
                x, y = (self.x, -self.layout.height)
        return x, y


class ScribbleText(MyTextArea):
    def __init__(self, **kwargs):
        kwargs.setdefault('padding_x', 3)
        kwargs.setdefault('autosize', True)
        kwargs.setdefault('cls', 'mytextinput')
        kwargs.setdefault('style',{'font-size': kwargs['font-size']})
        super(ScribbleText, self).__init__(**kwargs)
        self.orig = (0, 0)
        self.label_obj.options['font_size'] = self.style['font-size']
        self.label_obj.refresh()
    def _recalc_size(self):
        # We could do this as .size property I suppose, but then we'd
        # be calculating it all the time when .size is accessed.
        num = len(self.lines)
        if not num:
            return
        # The following two if statements ensure that the textarea remains
        # easily clickable even if there's no content.
        if self.autosize or self.autoheight:
            self.height = num * self.line_height + self.line_spacing * (num - 1)
        if (self.autosize or self.autowidth):
            self.width = max(label.content_width for label in self.line_labels) +20

    def on_press(self, touch):
        self.orig = Vector(self.to_window(*touch.pos))

    def on_release(self, touch):
        final = Vector(self.to_window(*touch.pos))
        if self.orig.distance(final) <= 4:
            if not self.is_active_input:
                self.parent.disable_all() #IGNORE:E1101
                self._can_deactive = True
            super(ScribbleText, self).on_release(touch)
#    def show_keyboard(self):
#        super(MyTextArea,self).show_keyboard()
#        to_root = self.keyboard_to_root
#        if(to_root):
#            w = self.get_root_window() if to_root else self.get_parent_window()
#            w.remove_widget(self.keyboard)
#            #we want to add this keyboard to the innerwindow border
#            #self.parent.parent.parent.parent.show_keyboard(self.keyboard)
#            self.parent.parent.parent.parent.add_widget(self.keyboard)
#            #self.keyboard.pos = self.to_window(self.pos[0], self.pos[1] - self.height  - self.keyboard.height) #position of the text input field
#
#
#                                
#    def hide_keyboard(self):
#        if self._is_active_input:
#            self.parent.parent.parent.parent.set_button_image() 
#        super(ScribbleText, self).hide_keyboard()
#        p = self.parent
#        if(p):
#            pp = p.parent
#            if(pp):
#                ppp = pp.parent
#                if(ppp):
#                    p4 = ppp.parent
#                    if(p4):
#                        #p4.hide_keyboard(self.keyboard)
#                        p4.remove_widget(self.keyboard)

    def on_touch_down(self, touch):
        super(ScribbleText, self).on_touch_down(touch)
        return False


class ScribbleTextWidget(MTScatter):
    def __init__(self, **kwargs):
        kwargs.setdefault('size',(20,20))
        kwargs.setdefault('pos',(0,0))
        self.Id = kwargs.get('Id',uuid())
        kwargs.setdefault('keyboard_to_root', True)
        super(ScribbleTextWidget, self).__init__(**kwargs)
        self.editmode = True
        kwargs.setdefault('color',[1.0,1.0,1.0,1.0])
        kwargs.setdefault('font-size',kwargs['size'][1]/1.1)
        self.cdata = kwargs.get('label','')
        del kwargs['size']
        del kwargs['pos']
        self.label = ScribbleText(**kwargs)
        self.label.push_handlers(on_text_change=self.on_text_change)
        self.add_widget(self.label)
        self.size = self.label.size
        self.label.center = self.to_local(*self.center)
        self.register_event_type('on_text_change')
    def on_text_change(self,value):
        self.cdata = value.value
        self.parent.dispatch_event('on_text_change', self.to_dic())
        return True
    def to_dic(self):
        return {
                'Id':self.Id,
                'Color': self.label.color,  
                'Font-Size':self.label.font_size,
                'Cdata':self.cdata, 
                'pos':self.pos,
                'size':self.size
                }
    def disable_all(self):
        self.parent.disable_all() #IGNORE:E1101

    def disable(self):
        self.label.hide_keyboard()

    def enable(self):
        self.label.show_keyboard()

    def draw(self):
        '''
        set_color(.509, .407, .403, .95)
        drawRoundedRectangle(size=self.size)
        set_color(.298, .184, .192, .95)
        drawRoundedRectangle(size=self.size, linewidth=2, style=GL_LINE_LOOP)
        '''
        self.width = max(20, self.label.width)
        self.height = max(20,self.label.height)
        #set_color(.435, .749, .996)
        set_color(*self.style['bg-color'])
        drawRoundedRectangle(size=self.size)
        #set_color(.094, .572, .858)
        set_color(*self.style['border-color'])
        drawRoundedRectangle(size=self.size, linewidth=2, style=GL_LINE_LOOP)
class MyScribbleWidget(MTWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('cls', 'scribbleBordercss')
        super(MyScribbleWidget,self).__init__(**kwargs)
        self.session = uuid()
        self.is_pen_active = True
        self.sessions = kwargs.setdefault('sessions',{self.session:{}})
        self.press_and_hold_distance = \
            kwargs.setdefault('activate_keyboard_distance',10 /1000.0)
        self.delete_distance = kwargs.setdefault('delete_distance',12)
        self.potential_deleted_lines  = None
        self.potential_deleted_text  = None
        self.touch_time = {}
        self.old_touches = {}
        self.old_colors = {}
        self.touch_positions = {}
        self.touch_keys = {}
        self.touch_positions = kwargs.get('scribbles',{})
        self.travel_limit = 5
        self.keyboard = MTVKeyboard()
        tf = kwargs.get('TextFields', {})
        if tf:
            args = {'group':self.session,
                    'keyboard':self.keyboard,
                    'cls':'scribbleKeyboardcss'}
            for txt in tf.values():
                # we need to create and add the following textfields
                args['Id']=txt['Id'] 
                args['pos']=eval(txt['pos'])
                args['size']=eval(txt['size'])
                args['color']=txt['Color']
                args['font-size']=eval(txt['Font-Size'])
                args['label']=txt['Cdata']
                stw = ScribbleTextWidget(**args) #IGNORE:W0142
                stw.push_handlers(on_transform=curry(self.on_transform,stw))
                self.add_widget(stw)
        self.ctrls_container = MySidePanel(layout=MTGridLayout(cols=1),
                                           use_root=False,#duration=0.1,
                                        corner=MTImageButton(padding=5,
                                image=Loader.image(OPEN_SIDE_ICON),
                                                        size=(48,48)),
                                        corner_open=MTImageButton(padding=5,
                                image=Loader.image(CLOSE_SIDE_ICON),
                                                        size=(48,48)),
                                        align='middle',
                                        side='right',
                                        pos=(0,0),cls='mybtn')
        btn_pen = MTImageButton(padding=5,image=Loader.image(PEN_ICON))
        btn_pen.connect('on_press', self.pen)
        self.ctrls_container.add_widget(btn_pen)
        btn_erase = MTImageButton(padding=5,image=Loader.image(ERASER_ICON))
        btn_erase.connect('on_press', self.eraser)
        self.ctrls_container.add_widget(btn_erase)
        btn_color = MTImageButton(padding=5,image=Loader.image(COLOR_ICON))
        btn_color.connect('on_press', self.color)
        self.ctrls_container.add_widget(btn_color)
        self.add_widget(self.ctrls_container)
        self.current_color = DEFAULT_COLOR
        self.bg_color = self.style['bg-color']
        self.new_color = None
        self.border_color = self.style['border-color']
        self.border_width = self.style['border-width']
        self.register_event_type('on_change')
        self.register_event_type('on_text_change')
    def pen(self,w): #IGNORE:W0613
        self.is_pen_active = True 
        self.current_color = DEFAULT_COLOR if not self.new_color \
                                                        else self.new_color
        self.style['border-color'] = self.border_color
        self.style['border-width'] = self.border_width
    def eraser(self,w): #IGNORE:W0613
        self.is_pen_active = False
        self.current_color = self.bg_color
        self.style['border-color'] = RED
        self.style['border-width'] = 7
    def color(self,w):
        pass
    def get_child_pos(self):
        return self.to_parent(self.width, self.height, True)
    def collide_point(self, x, y):
#        x1,y1 = self.to_local(x, y, True)
        x1,y1 =x,y
        return super(MyScribbleWidget,self).collide_point(x1,y1)
    def disable_all(self):
        for w in self.children:
            if not isinstance(w, ScribbleTextWidget):
                continue
            w.disable()
    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            if not self.is_pen_active:
                #eraser is active we need to check if there is something to 
                #erase
                if self.erase_scribble(touch):
                    return True
                if self.erase_text_filed(touch):
                    return True
                if not self.current_color == self.bg_color:
                    self.current_color = self.bg_color
            if super(MyScribbleWidget,self).on_touch_down(touch):
                return True
            self.touch_time[touch.id] = (time.time(),touch)
            touch.grab(self)
            Log.debug('Scribble: on_touch_down: touch id:%s grabbed @ pos(%d,%d)' % 
                       (touch.id, touch.x,touch.y))
            idu = self.touch_keys[touch.id] = uuid()
            self.touch_positions[idu]= {'Id':idu, 'Color':self.current_color,
                                       'Cdata':[touch.pos]}
            self.touch_positions[idu]['moved'] = 0
            return True
    def on_touch_move(self, touch):
        if touch.grab_current == self:# or touch.id in self.touch_positions:
            if self.collide_point(touch.x, touch.y):
                idu = self.touch_keys[touch.id]
                try:
                    self.touch_positions[idu]['Cdata'].append(touch.pos)
                    Log.debug('Scribble: on_touch_move: touch id:%s id:%s @ pos(%d,%d)' % 
                       (touch.id, idu, touch.x,touch.y))
                except Exception: #IGNORE:W0703
                    Log.debug('Scribble: on_touch_move FAILED: touch id:%s id:%s @ pos(%d,%d)' % 
                       (touch.id, idu, touch.x,touch.y))
                if not self.is_pen_active:
                    self.erase_point(*touch.pos) #IGNORE:W0142
                    return True
                self.dispatch_event('on_change', #IGNORE:W0142
                                    *(idu,self.touch_positions))
                self.touch_positions[idu]['moved'] += 1
                return True

    def on_touch_up(self, touch):
        if touch.grab_current == self:# or touch.id in self.touch_positions:
            touch.ungrab(self)
            if self.collide_point(touch.x, touch.y):
                Log.debug('Scribble: on_touch_up: touch id:%s pos(%d,%d)' % 
                       (touch.id, touch.x,touch.y))
                self.parent.parent.set_button_image()
                
                idu = self.touch_keys[touch.id]
                self.touch_positions[idu]['Cdata'].append(touch.pos)
                if self.is_pen_active:
                    if self.drawTextInput(touch):
                        del self.touch_positions[idu]
                else:
                    del self.touch_positions[idu]
                self.dispatch_event('on_change',  #IGNORE:W0142
                                    *(idu,self.touch_positions))
            return True
    def on_text_change(self,value):pass
    def drawTextInput(self,touch):
        start, pos = self.touch_time[touch.id]
        start = start if start else time.time() 
        elaspsed_time = time.time() -  start
        idu = self.touch_keys[touch.id]
        Log.debug('Elapsed time:%s' % elaspsed_time)
        if elaspsed_time >= 1:
            distance = Vector.distance( Vector(pos.sx, pos.sy),
                                        Vector(touch.osxpos, touch.osypos))
            Log.debug('Screen coordinate Distance:%f vs %f' % (distance,self.press_and_hold_distance))
            _l = len(self.touch_positions[idu]['Cdata'])
            Log.debug('Num points:%d' % _l)
            _vd = Vector.distance(\
                            Vector(*self.touch_positions[idu]['Cdata'][0]),\
                            Vector(*self.touch_positions[idu]['Cdata'][_l-1]))
            Log.debug('touch distance :%f and %d' % (_vd, int(_vd)))
            if distance <= self.press_and_hold_distance and\
                        (_l < self.travel_limit or int(_vd) < self.travel_limit):                                            
                
                txt = ScribbleTextWidget(pos=touch.pos, group=self.session,
                                                   keyboard=self.keyboard,
                                                   cls='scribbleKeyboardcss')
                txt.push_handlers(on_transform=curry(self.on_transform,txt))
                self.add_widget(txt) 
                self.disable_all()
                txt.enable()
                d = txt.to_dic()
                self.dispatch_event('on_text_change', d)
                return True
    def on_transform(self,txtwidget, touch, *args, **kwargs): #IGNORE:W0613
        self.dispatch_event('on_text_change', txtwidget.to_dic())
    def erase_point(self,x,y):
        for k in self.touch_positions.keys():
            if self.touch_positions[k]['Color'] is self.bg_color:
                continue
            d_list = []
            for v in self.touch_positions[k]['Cdata']:
                if self.should_delete((x,y), v):
                    d_list.append(v)
            for v in  d_list: 
                self.touch_positions[k]['Cdata'].remove(v)
                self.dispatch_event('on_change',  #IGNORE:W0142
                                    *(k,self.touch_positions))
            if not self.touch_positions[k]['Cdata']:
                del self.touch_positions[k]
                self.dispatch_event('on_change', #IGNORE:W0142
                                    *(k,self.touch_positions)) 
    def erase_text_filed(self,touch):
        d_txt = None
        for c in self.children:
            if isinstance(c,ScribbleTextWidget) and c.collide_point(*touch.pos):
                d_txt = c
                break
        if d_txt:
            if not self.potential_deleted_text:
                self.potential_deleted_text = d_txt
                d_txt.style['bg-color'] = RED
                d_txt.style['border-color'] = BLACK
            else:
                self.remove_widget(d_txt)
                d = {'Id': d_txt.Id}
                self.dispatch_event('on_text_change', d)
                self.potential_deleted_text = None
#                id = self.touch_keys[touch.id]
#                self.dispatch_event('on_change', *(id,self.touch_positions))
            return True
        if self.potential_deleted_text:
            d_txt = self.potential_deleted_text
            self.potential_deleted_text = None
            d_txt.reload_css()
    def erase_scribble(self,touch):
        pos = touch.pos
        _del = False
        k = None
        for k in self.touch_positions.keys():
            for v in self.touch_positions[k]['Cdata']:
                if self.should_delete(pos, v):
                    _del = True
                    break
            if _del: break
        if _del:
            if self.potential_deleted_lines == k:
                del self.touch_positions[k]
                self.potential_deleted_lines = None
                self.dispatch_event('on_change', #IGNORE:W0142
                                    *(k,self.touch_positions)) 
            else:
                if not self.potential_deleted_lines:
                    self.potential_deleted_lines = k
                    self.old_colors[k] = self.touch_positions[k]['Color'] 
                else:
                    k = self.potential_deleted_lines 
                    self.touch_positions[k]['Color'] = self.old_colors[k]
                    self.potential_deleted_lines = None
            return True
        elif self.potential_deleted_lines:
            k = self.potential_deleted_lines 
            self.touch_positions[k]['Color'] = self.old_colors[k]
            self.potential_deleted_lines = None
            return True
    def should_delete(self,touch_p, line_p):    
        distance = Vector.distance( Vector(*line_p), #IGNORE:W0142
                                    Vector(*touch_p)) #IGNORE:W0142
        if distance <= self.delete_distance:
            return True
        
    def on_change(self, idu,points):
        pass
    def draw(self):
        super(MyScribbleWidget,self).draw()
#        set_color(1, 1, 1)
        d_txt = self.potential_deleted_text 
        if d_txt:
            x = int(time.time()) % 2
            if x == 0:
                b_col = d_txt.style['bg-color'] 
                d_txt.style['bg-color'] = d_txt.style['border-color'] 
                d_txt.style['border-color'] = b_col
        _del_list = []
        for k in self.touch_positions.keys():
            _points = self.touch_positions[k]['Cdata']
            if not len(_points):
                _del_list.append(k)
                continue
            _colour = self.touch_positions[k]['Color'] 
            if self.potential_deleted_lines == k:
                x = int(time.time()) % 2
                if x == 0: 
                     _colour = DELETED_LINE 
                else:
                    self.touch_positions[k]['Color'] = RED 
            set_color(*_colour)
            drawLine(_points)
        for k in _del_list:
            del self.touch_positions[k]
if __name__ == '__main__':
    
    from pymt.ui.window import MTWindow
    from pymt.base import runTouchApp
    mw = MTWindow()
    mw.size = scale_tuple(get_min_screen_size(),.1)
    mw.add_widget(MyScribbleWidget(size= scale_tuple(mw.size,.3),pos=(100,100),
                                  cls='scribbleBordercss'))
    runTouchApp()
