# -*- coding: utf-8 -*-
'''
Created on Sep 26, 2010

@author: stevenson
'''
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from agileConfig import Config
from cmap.model.baseModel import BaseModel
try:
    Log = Config().log.logger
except Exception:
    from petaapan.utilities.console_logger import ConsoleLogger
    Log = ConsoleLogger('CMAP')

class ReleaseModel(BaseModel):
    def __init__(self, ctrl,**kwargs):
        kwargs.setdefault('folder','releases')
        kwargs.setdefault('model_str','Release')
        self.sprint_list = []
        super(ReleaseModel,self).__init__(ctrl,**kwargs)
    @property
    def Sprints(self):
        return self.listData(self.Children, 'Sprint')
    def close(self):
        super(ReleaseModel,self).close()
    def save(self, closing=False):
        super(ReleaseModel,self).save()
