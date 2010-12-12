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
from cmap.model.baseModel import BaseModel
try:
    Log = Config().log.logger
except Exception: #IGNORE:W0703
    from petaapan.utilities.console_logger import ConsoleLogger
    Log = ConsoleLogger('CMAP')
class TaskModel(BaseModel):
    def __init__(self, ctrl,**kwargs):
        kwargs.setdefault('folder','tasks')
        kwargs.setdefault('model_str','Task')
        self.item_list = []
        self.story_list = []
        super(TaskModel,self).__init__(ctrl,**kwargs)

    def createProject(self):
        return self.create_model('Task')
    def _get_assigned(self):
        try:
            return self._Assigned.data
        except Exception: #IGNORE:W0703
            return ''
    def _get_items(self):
        return self.item_list
    def _get_stories(self):
        if self.Children is None:
            return []
        return self.listData(self.Children, 'Story')
    def _set_assigned(self, value):
        node = None
        v = value if value else ''
        try:
            self._Assigned = v
            self.dirty = True
            node = self.dom.getElementsByTagName('Assigned')[0]
        except Exception: #IGNORE:W0703
            node = self.dom.createElement('Assigned')
            self._Model.appendChild(node)
            node.appendChild( self.dom.createTextNode(v))
        node.firstChild.data = v
    def _set_items(self, value):
        node = None
        if value is None: return
        if value in self.item_list:
            return
        self.dirty = True
        self.item_list.append(value)
        try:
            node = self.dom.getElementsByTagName('Items')[0]
        except Exception: #IGNORE:W0703
            node = self.dom.createElement('Items')
            self._Model.appendChild(node)
        e = self.dom.createElement('Item')
        e.appendChild( self.dom.createTextNode(value))
        node.appendChild(e)
    def _set_stories(self, value):
        node = None
        if value is None: return
        if value in self.story_list:
            return
        self.dirty = True
        self.story_list.append(value)
        
        try:
            node = self.dom.getElementsByTagName('Stories')[0]
        except Exception: #IGNORE:W0703
            node = self.dom.createElement('Stories')
            self._Model.appendChild(node)
            e = self.dom.createElement('Story')
            e.appendChild( self.dom.createTextNode(value))
            node.appendChild(e)
    Assigned = property(_get_assigned, _set_assigned)
    Items = property(_get_items, _set_items)
    Stories = property(_get_stories, _set_stories)
    
