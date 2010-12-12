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
try:
    Log = Config().log.logger
except Exception:
    from petaapan.utilities.console_logger import ConsoleLogger
    Log = ConsoleLogger('CMAP')


from cmap.model.baseModel import BaseModel
class ProjectModel(BaseModel):
    def __init__(self, ctrl,**kwargs):
        kwargs.setdefault('folder','projects')
        kwargs.setdefault('model_str','Project')
        self._ProjectBackLog = []
        self._Owner = None
        self._ScrumMaster = None
        self._Status = None
        super(ProjectModel,self).__init__(ctrl,**kwargs)
    def createProject(self):
        return self.create_model('Project')
    def _get_backlog(self):
        if self._ProjectBackLog is None:
            return []
        return self.listData(self._ProjectBackLog)
    @property
    def Releases(self):
        return self.listData(self.Children, 'Release')
    def _get_owner(self):
        try:
            return self._Owner
        except Exception:
            return ''
    def _get_scrum_master(self):
        try:
            return self._ScrumMaster
        except Exception:
            return ''
    def _get_status(self):
        try:
            return self._Status.data
        except Exception:
            return ''
    def _set_backlog(self,  value):
        try:
            node = None
            if value is None: return
            if self._ProjectBackLog is not None and \
                                                value in self._ProjectBackLog:
                return
            self.dirty = True
            if self._ProjectBackLog is None:
                self._ProjectBackLog = []
            self._ProjectBackLog.append(value)
            node = self.dom.getElementsByTagName('ProjectBackLog')[0]
            e = self.dom.createElement('BackLog')
            e.appendChild( self.dom.createTextNode(value))
            node.appendChild(e)
        except Exception:
            node = self.dom.createElement('ProjectBackLog')
            self._Model.appendChild(node)
            e = self.dom.createElement('BackLog')
            e.appendChild( self.dom.createTextNode(value))
            node.appendChild(e)
    def _set_owner(self, value):
        node = None
        v = value if value else ''
        try:
            self._Owner = v
            self.dirty = True
            node = self.dom.getElementsByTagName('Owner')[0]
        except Exception:
            node = self.dom.createElement('Owner')
            self._Model.appendChild(node)
            node.appendChild( self.dom.createTextNode(v))
        node.firstChild.data = v
    def _set_scrum_master(self, value):
        node = None
        v = value if value else ''
        try:
            self._ScrumMaster = v
            self.dirty = True
            node = self.dom.getElementsByTagName('ScrumMaster')[0] 
        except Exception:
            node = self.dom.createElement('ScrumMaster')
            self._Model.appendChild(node)
            node.appendChild( self.dom.createTextNode(v))
        node.firstChild.data = v
    def _set_status(self, value):
        node = None
        v = value if value else ''
        try:
            self._Status = value
            self.dirty = True
            node = self.dom.getElementsByTagName('Status')[0]
        except Exception:
            node = self.dom.createElement('Status')
            self._Model.appendChild(node)
            node.appendChild( self.dom.createTextNode(v))
        node.firstChild.data = v
    
    ProjectBackLog = property(_get_backlog, _set_backlog)
    Owner = property(_get_owner, _set_owner)
    ScrumMaster = property(_get_scrum_master, _set_scrum_master)
    Status = property(_get_status, _set_status)
    def close(self):
        super(ProjectModel,self).close()
