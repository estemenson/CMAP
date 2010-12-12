# -*- coding: utf-8 -*-
'''
Created on 2010-12-01

@author: jonathan
'''

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pymt.ui.widgets.button import MTImageButton
from pymt.graphx.draw import drawTexturedRectangle

class MyImageButton(MTImageButton):
    '''
    classdocs
    '''


    def __init__(self, **kwargs):
        '''
        Constructor
        '''
        super(MyImageButton, self).__init__(**kwargs)
        
    def draw(self):
        drawTexturedRectangle(texture=self.image.texture, pos=self.pos,
                              size=(100, 100))
