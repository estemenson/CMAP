'''
Created on 2011-05-13

@author: hotsoft
'''
class GestureController(object):
    def __init__(self, **kwargs):
        self.canvas = MTScatter(cls='gesturecss') 
        self.canvas.size = self.root_window.size
        self.canvas.pos = (0,0)
        super(StoryApp,self).add_widget(self.canvas)
        if not self.canvas:
            print("No canvas in gestures ")
        capture = MyCaptureWidget(gdb, self)
        capture.size = self.canvas.size
        if not capture:
            print("No capture device in gestures")
        self.canvas.add_widget(capture)
        