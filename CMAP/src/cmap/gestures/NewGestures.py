# -*- coding: utf-8 -*-
#    Created on May 26, 2010
#    @author: stevenson


from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
#try:
#    from myGestures import myGestures
#except:
#    from cmap.gestures.myGestures import myGestures
from os import path
from cmap.tools.borders import MyInnerWindow
import logging
try:
    from agileConfig import Config
    Log = Config().log.logger
except:
    Log = logging.getLogger()
    Log.setLevel(logging.DEBUG)
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'NewGesture tester'
PLUGIN_AUTHOR = 'Stevenson Gossage'
PLUGIN_DESCRIPTION = 'test new gestures'

from pymt import * #@UnusedWildImport
from cmap.gestures.xmlGestures.xmlGestures import Gestures
from cmap.gestures.myGestures import myGestures
MyCustomFormcss = '''
form.MyCustomForm {
    bg-color: rgba(100, 155, 255, 255);
    border-width: .5;
    border-radius: 1;
    border-radius-precision: .1;
    draw-border: 0;
}
'''
css_add_sheet(MyCustomFormcss)

class MyCustomForm(MTModalWindow):
    '''A simple implementation of a popup. based on modalpopup pymt example

    :Parameters:
        `title` : str, default is 'Information'
            Title of popup
    '''
    def __init__(self,parrent=None, **kwargs):
        kwargs.setdefault('title', 'Information')
        super(MyCustomForm, self).__init__(**kwargs)
        self.title = kwargs.get('title')
        self.parrent = parrent
        #create the form                                                                               style={'color-down': (1,0,1), 'font-size': 16, 'bg-color': (0,0,0)}) 
        self.popup = MyInnerWindow(cls='MyCustomForm',pos=(100,100),\
                id='customPopupForm_id')
        self.form = MTGridLayout(padding=20,spacing=20, cols=2, rows=5, 
                                     uniform_height=True)#, style={'border-radius':30, 'bg-color': (0,190,0)})
        #self.form.add_widget(MTFormLabel(label=self.title, halign='center', style={'border-radius':30}))
        self.form.add_widget(MTLabel(label='Save this gesture', \
                                         halign='right'))
        self.chk_savegesture = MTToggleButton(halign='left', \
                                              id='chk_savegesture')
        self.form.add_widget(self.chk_savegesture)
        #Gesture Label  -- add an input field with keyboard and label
        self.form.add_widget(MTLabel(label='New Gesture\'s label',\
                                          halign='right'))
        self.newGestureLabel = MTTextInput(halign='left', id='inpt_label')
        self.form.add_widget(self.newGestureLabel)
        #Gesture ID -- add an input field with keyboard and label
        self.form.add_widget(MTLabel(label='New Gesture\'s ID',\
                                          halign='right'))
        self.newGestureId = MTTextInput(halign='left', id='inpt_id')
        self.form.add_widget(self.newGestureId)
        #replace if exists????
        self.form.add_widget(MTLabel(label='Replace gesture if it exists',\
                                          halign='right'))
        self.chk_replace_gesture = MTToggleButton(halign='left', \
                                                  id='chk_replace_gesture')
        self.form.add_widget(self.chk_replace_gesture)
        
        self.submit = MTButton(label='Submit')
        self.form.add_widget(self.submit)
        self.cancel = MTButton(label='CANCEL')
        self.form.add_widget(self.cancel)

        #add handlers
        self.chk_savegesture.push_handlers(on_press=self.action_save_gesture)
        #self.chk_savegesture.push_handlers(on_touch_up=self.on_touch_up)
        self.chk_replace_gesture.push_handlers(\
                                        on_press=self.action_replace_gesture)
        if parrent:
            self.submit.push_handlers(\
                                    on_release=self.parrent.action_close_popup)
        else:
            self.submit.push_handlers(on_release=self.action_close_popup)

        self.cancel.push_handlers(on_press=self.action_cancel_popup)
        self.clear_gesture_data()
        #super(MyCustomForm, self).add_widget(self.form)
        self.add_widget(self.form)


    # getters
    def get_myForm(self):
        return self.form
    def get_save_gesture(self):
        return self.save_gesture
    def get_gesture_label(self):
        return self.gesture_label
    def get_replace_gesture(self):
        return self.replace_gesture
    def get_gesture_id(self):
        return self.gesture_id

    #handle events
 
    def action_cancel_popup(self, *largs):
        self.remove_widget(self.form)
        self.parent.remove_widget(self)
    def action_close_popup(self, *largs):
        if self.parrent:
            #call the  calling objects method
            self.parrent.action_close_popup(self.form)
        else:
            Log.debug("saving form")
            #if self.save_gesture:
            self.gesture_label = self.newGestureLabel._get_value()
            self.gesture_id = self.newGestureId._get_value()
            Log.debug('Label: ' + self.gesture_label)
            Log.debug('ID: ' + self.gesture_id )
            p = self.parent
            Log.debug(p)
            largs.userdata = {'label':self.gesture_label, 'id':self.gesture_id,\
                     'save':self.save_gesture, 'replace':self.replace_gesture}
            #p.remove_widget(self)
        
    def action_save_gesture(self,checked):
        Log.debug("we are in action_save_gesture !!!") #w.set_fullscreen(checked)
        self.save_gesture = checked

    def action_replace_gesture(self,checked):
        Log.debug("we are in action_replace_gesture !!!")
        self.replace_gesture = checked

    def clear_gesture_data(self):
        self.save_gesture = False
        self.gesture_label = ''
        self.gesture_id = ''
        self.replace_gesture = False
    def draw(self):
        w = self.get_parent_window()
        if self.form.x == 0:
            x = (w.width - self.form.width) / 2
            y = (w.height - self.form.height) / 2
            self.form.pos = (x, y)
        super(MyCustomForm, self).draw()



class CaptureGesture(MTGestureWidget): 
    def __init__(self, gdb, bgcolor=(.4,.4,.4, .8)):
        super(CaptureGesture, self).__init__()
        self.gdb = gdb
        self.bgcolor = bgcolor
        self.gesture = None
        self.lastgesture = None
        self.lastbest = None
        self.labeltext2 = None

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return
        super(CaptureGesture, self).on_touch_down(touch)
        return True

    def on_touch_move(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return
        super(CaptureGesture, self).on_touch_move(touch)
        return True

    def on_touch_up(self, touch):
        super(CaptureGesture, self).on_touch_up(touch)
        if not self.collide_point(touch.x, touch.y):
            return
        return True
    def action_close_popup(self,form):
        Log.debug("saving form")
        if self.mtform.save_gesture:
            self.newGesture.label = self.mtform.newGestureLabel._get_value()
            self.newGesture.id = self.mtform.newGestureId._get_value()
            Log.debug('Label: ' + self.newGesture.label)
            Log.debug('ID: ' + self.newGesture.id )
            tmp = self.gdb.pull_gesture_from_shelf(self.newGesture.label)
            tmp = tmp if tmp else self.gdb.pull_gesture_from_shelf(\
                                                    self.newGesture.id)
            if self.mtform.replace_gesture:
                if tmp:
                    self.labeltext2 = "Gesture: %s was replaced", \
                        self.newGesture.label
                    Log.debug("Gesture: %s was replaced" % self.newGesture.label)
                    self.gdb.remove_gesture_from_shelf(tmp) 
            if tmp:
                self.labeltext2 = \
                "Gesture: %s was loaded from persistent storage", \
                    self.newGesture.label
                Log.debug("Gesture: %s was loaded from persistent storage" % \
                    self.newGesture.label)
                self.newGesture = tmp
            else:
                self.labeltext2 = "Gesture: %s was Created" % \
                    self.newGesture.label
                Log.debug("Gesture: %s was Created" % self.newGesture.label)
            
            self.gdb.push_gesture_to_shelf(self.newGesture)
            Log.debug('New Gesture created: %s' % self.newGesture.label)
            self.lastgesture = self.newGesture
            #self.update()
        #close and remove the popup 
        self.parent.remove_widget(self.mtform)

    def not_gesture(self, gesture, touch):
        #global w
        #self.hide()
        self.newGesture = gesture
        self.mtform = MyCustomForm(self, title='Save new Gesture?')
        self.parent.add_widget(self.mtform)
        
    def on_gesture(self, gesture, touch):
        # try to find gesture from database
        best = self.gdb.find(gesture, minscore=0.8)
        if not best:
            Log.debug(
            'No gesture found\nString version of your last gesture :%s\n' %\
             self.gdb.gesture_to_str(gesture))
            self.not_gesture(gesture, touch)
        else:
            Log.debug('Gesture found, score %s:%s' % (best[0], best[1].label))
        self.lastgesture = gesture
        self.lastbest = best

    def draw(self):
        # draw background
        set_color(*self.bgcolor)
        drawRectangle(pos=self.pos, size=self.size)

        # draw current trace
        set_color(1,1,1)
        for trace in self.points:
            l = []
            for p in self.points[trace]:
                l.append(p[0])
                l.append(p[1])
            drawLine(l)

        # draw last gesture
        scoretext = ''
        if self.lastbest:
            if self.lastbest[0] < 0.8:
                set_color(1, 0.2, .2, .8)
                scoretext = 'bad'
            elif self.lastbest[0] < 0.9:
                set_color(1, 0.5, .0, .8)
                scoretext = 'medium'
            elif self.lastbest[0] < 0.95:
                set_color(0.2, 0.8, .2, .8)
                scoretext = 'good'
            else:
                set_color(0.2, 1, .2, .8)
                scoretext = 'excellent !'
        else:
            set_color(.3, .3, .3, .8)
        s = self.width * 0.1
        drawRectangle(pos=(self.pos[0], self.pos[1] + self.height),\
                       size=(s*2, s*2))
        set_color(1,1,1,.8)
        if self.lastgesture:
            l = []
            for p in self.lastgesture.strokes[0].points:
                l.append(self.pos[0] + s + p.x * s)
                l.append(self.pos[1] + s + self.height + p.y * s)
            drawLine(l)
            set_color(1,1,1,.4)
            l = []
            for p in self.lastgesture.strokes[0].screenpoints:
                l.append(p[0])
                l.append(p[1])
            drawLine(l)

        if self.lastbest:
            labeltext = 'Gesture found : %s' % self.lastbest[1].label
            labeltext2 = 'Score is %f, %s' % (self.lastbest[0], scoretext)
        else:
            labeltext = 'No gesture found'
            labeltext2 = self.labeltext2 if self.labeltext2 else '' 
        drawLabel(label=labeltext, pos=(self.pos[0] + s*3, self.pos[1] + \
                            self.height + s * 0.8 + self.height * 0.07),
                font_size=self.height * 0.07, center=False)
        drawLabel(label=labeltext2, pos=(self.pos[0] + s*3, self.pos[1] + \
                                         self.height + s * 0.7),
                font_size=self.height * 0.07, center=False)
        self.labeltext2 = None

class GestureUI(MTWidget):
    def __init__(self, gdb, **kwargs):
        super(GestureUI, self).__init__(**kwargs)
        self.gdb = gdb
        self.capture = CaptureGesture(gdb)
        self.add_widget(self.capture)
        self.title = MTLabel(label='NewGesture Recognition', autosize=True,
                             font_size=42)
        self.add_widget(self.title)

    def on_draw(self):
        if not self.parent:
            return
        w, h = self.parent.size
        self.capture.pos = 0.1 * w, 0.1 * h
        self.capture.size = 0.8 * w, 0.5 * h
        self.title.font_size = h * 0.07
        self.title.pos = w/2-self.title.width/2, h - self.title.height - 20
        super(GestureUI, self).on_draw()

def get_and_or_store_gesture(gdb, name, label=None, file=None):
    file = file if file else path.abspath(path.curdir + \
                                    '\\xmlGestures\\gestures.xml')# + \
                        #'\\examples\\xmlGestures\\gestures.xml'
    Log.debug('path: %s' % file)
    gestures = Gestures(file)
    g = gdb.pull_gesture_from_shelf(name)
    if not g:
        id = label if label else name
        g = gdb.str_to_gesture(gestures.getGestureStrRep(id))
        g.label = name
        g.id = id
        gdb.push_gesture_to_shelf(g)
    if not gdb.find(g):
        gdb.add_gesture(g)
    return g

def pymt_plugin_activate(root, ctx):
    gdb = myGestures()
    # Circle
#    get_and_or_store_gesture(gdb, 'Circle', 'circle')
#    # Square up_left, bottom_left, bottom_right, up_right
#    get_and_or_store_gesture(gdb, 'Square', 'square')
#    # Up
#    get_and_or_store_gesture(gdb, 'Up', 'up')
#    # NUI-wave
#    get_and_or_store_gesture(gdb, 'NUI-wave', 'nui-wave')
#    #A (without cross-bar)
#    get_and_or_store_gesture(gdb, 'A (no cross-bar)', 'a (no cross-bar)')
#    #X up_letf, bottom_right, top_right, bottom_left
#    get_and_or_store_gesture(gdb, 'X', 'x')
#    #S draw an S
#    get_and_or_store_gesture(gdb, 'New Story', 'New_Story')
    try:
        get_and_or_store_gesture(gdb, 'New Story', 'New_Story')
        get_and_or_store_gesture(gdb, 'Projects', 'Projects')
        get_and_or_store_gesture(gdb, 'Projects1', 'Projects1')
        get_and_or_store_gesture(gdb, 'Releases', 'Releases')
        get_and_or_store_gesture(gdb, 'Releases1', 'Releases1')
        #get_and_or_store_gesture(gdb, 'Sprints', 'Sprints')
        #get_and_or_store_gesture(gdb, 'Sprints1', 'Sprints1')
        get_and_or_store_gesture(gdb, 'Sprints2', 'Sprints2')
        get_and_or_store_gesture(gdb, 'Tasks', 'Tasks')
        get_and_or_store_gesture(gdb, 'Tasks1', 'Tasks1')
        #get_and_or_store_gesture(gdb, 'Tasks2', 'Tasks2')
        get_and_or_store_gesture(gdb, 'Square', 'square')
        get_and_or_store_gesture(gdb, 'X', 'x')
    except:
        pass
    
    canvas = MTScatterPlane() 
    canvas._set_size(root._get_size())
    canvas.add_widget(GestureUI(gdb))
    ctx.ui = canvas 
    root.add_widget(ctx.ui)

def pymt_plugin_deactivate(root, ctx):
    root.remove_widget(ctx.ui)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
# Register all base widgets
MTWidgetFactory.register('MyCustomForm', MyCustomForm)
