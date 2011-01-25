'''
Created on 2010-09-12

@author: steve
'''
from pymt.ui.widgets.composed.textinput import MTTextInput
from pymt.ui.widgets.composed.textarea import MTTextArea
from pymt.parser import parse_color
class MyTextInput(MTTextInput):
    def __init__(self,**kwargs):
        kwargs.setdefault('place_keyboard_by_control', False)
        kwargs.setdefault('get_initial_keyboard_rotation_from', None)
        super(MyTextInput, self).__init__(**kwargs)
        self.place_keyboard_by_control = kwargs.get('place_keyboard_by_control')
        self.get_initial_keyboard_rotation_from =kwargs.get(\
                                        'get_initial_keyboard_rotation_from')
    
#    def on_press(self, touch):
#        if not self.is_active_input:
#            self.show_keyboard()
    def show_keyboard(self):
        super(MyTextInput,self).show_keyboard()
        if(self.place_keyboard_by_control == 'True'): # should we place the keyboard near to the text input control
#            self.keyboard.pos = self.to_window(self.pos[0] + (self.width /2),\
#                self.pos[1] - (self.height / 2) - (self.keyboard.height / 2)) #position of the text input field
            self.keyboard.pos = self.to_window(self.pos[0],\
                self.pos[1] - self.height  - self.keyboard.height) #position of the text input field
        if(self.get_initial_keyboard_rotation_from != None):
            self.keyboard.rotation = \
                                self.get_initial_keyboard_rotation_from.rotation
class MyTextArea(MTTextArea):
    def __init__(self,**kwargs):
        super(MyTextArea,self).__init__(**kwargs)
        styles = self.style if self.style else {}
        styles.setdefault('selection-color', parse_color('rgb(255, 142, 33)'))
        styles.setdefault('cursor-color',parse_color('rgb(215, 15, 15)'))
        kwargs.setdefault('place_keyboard_by_control', False)
        kwargs.setdefault('get_initial_keyboard_rotation_from', None)
        self.place_keyboard_by_control = kwargs.get('place_keyboard_by_control')
        self.get_initial_keyboard_rotation_from =kwargs.get(\
                                        'get_initial_keyboard_rotation_from')
        
    def show_keyboard(self):
        super(MyTextArea,self).show_keyboard()
        if(self.place_keyboard_by_control == 'True'): # should we place the keyboard near to the text input control
#            self.keyboard.pos = self.to_window(self.pos[0] + (self.width /2),\
#                self.pos[1] - (self.height / 2) - (self.keyboard.height / 2)) #position of the text input field
            self.keyboard.pos = self.to_window(self.pos[0],\
                self.pos[1] - self.height  - self.keyboard.height) #position of the text input field
        if(self.keyboard_to_root):
            self.keyboard.pos = self.to_window(self.pos[0], self.pos[1] - self.height  - self.keyboard.height) #position of the text input field

        if(self.get_initial_keyboard_rotation_from != None):
            self.keyboard.rotation = \
                                self.get_initial_keyboard_rotation_from.rotation
