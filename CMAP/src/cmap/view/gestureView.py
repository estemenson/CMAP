'''
Created on 2011-05-13

@author: hotsoft
'''

class GestureView(MTScatter):
    def __init__(self, **kwargs):
        gdb = myGestures()
        defnition_path =  kwargs['xmlGestures']
        self.captureWidget(gdb)