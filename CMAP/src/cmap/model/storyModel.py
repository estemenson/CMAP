# -*- coding: utf-8 -*-
'''
Created on Jul 27, 2010

@author: stevenson
'''
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from agileConfig import Config
try:
    Log = Config().log.logger
except Exception: #IGNORE:W0703
    from petaapan.utilities.console_logger import ConsoleLogger
    Log = ConsoleLogger('CMAP')
from cmap.model.baseModel import BaseModel
 
class StoryModel(BaseModel):
    def __init__(self, ctrl, **kwargs):
        kwargs.setdefault('folder','stories')
        kwargs.setdefault('model_str','Story')
        super(StoryModel,self).__init__(ctrl,**kwargs)
        self._As_a = None
        self._Want_to = None
        self._So_that = None
        self._Owner = None
    def _get_as_a(self):
        try:
            return self._As_a
        except Exception: #IGNORE:W0703
            return ''
    def _get_want_to(self):
        try:
            return self._Want_to
        except Exception: #IGNORE:W0703
            return ''
    def _get_so_that(self):
        try:
            return self._So_that
        except Exception: #IGNORE:W0703
            return ''
    def _get_owner(self):
        try:
            return self._Owner
        except Exception: #IGNORE:W0703
            return ''
    @property
    def Tasks(self):
        return self.listData(self.Children, 'Task')
    @property
    def Stories(self):
        return self.listData(self.Children, 'Story')
    def _set_as_a(self, value):
        node = None
        v = value if value else ''
        try:
            self._As_a = v
            self.dirty = True
            node = self.dom.getElementsByTagName('As_a')[0]
        except Exception: #IGNORE:W0703
            node = self.dom.createElement('As_a')
            self._Model.appendChild(node)
            node.appendChild( self.dom.createTextNode(v))
        node.firstChild.data = v
    def _set_want_to(self, value):
        node = None
        v = value if value else ''
        try:
            self._Want_to = v
            self.dirty = True
            node = self.dom.getElementsByTagName('Want_to')[0]
        except Exception: #IGNORE:W0703
            node = self.dom.createElement('Want_to')
            self._Model.appendChild(node)
            node.appendChild( self.dom.createTextNode(v))
        node.firstChild.data = v
    def _set_so_that(self, value):
        node = None
        v = value if value else ''
        try:
            self._So_that = v
            self.dirty = True
            node = self.dom.getElementsByTagName('So_that')[0]
        except Exception: #IGNORE:W0703
            node = self.dom.createElement('So_that')
            self._Model.appendChild(node)
            node.appendChild( self.dom.createTextNode(v))
        node.firstChild.data = v
    def _set_owner(self, value):
        node = None
        v = value if value else ''
        try:
            self._Owner = v
            self.dirty = True
            node = self.dom.getElementsByTagName('Owner')[0]
        except Exception: #IGNORE:W0703
            node = self.dom.createElement('Owner')
            self._Model.appendChild(node)
            node.appendChild( self.dom.createTextNode(v))
        node.firstChild.data = v
    As_a = property(_get_as_a, _set_as_a)
    Want_to = property(_get_want_to, _set_want_to)
    So_that = property(_get_so_that, _set_so_that)
    Owner = property(_get_owner, _set_owner)
