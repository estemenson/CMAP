# -*- coding: utf-8 -*-
'''
Created on 2010-10-04

@author: steve
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
from cmap.model.baseModel import BaseModel

class SprintModel(BaseModel):
    def __init__(self, ctrl,**kwargs):
        kwargs.setdefault('folder','sprints')
        kwargs.setdefault('model_str','Sprint')
        super(SprintModel,self).__init__(ctrl,**kwargs)
    @property
    def Stories(self):
        return self.listData(self.Children, 'Story')
    @property
    def Tasks(self):
        return self.listData(self.Children, 'Task')
