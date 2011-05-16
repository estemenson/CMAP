# -*- coding: utf-8 -*-
'''
Created on Aug 9, 2010

@author: stevenson
'''

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

# This will cause the configuration to be established from the
# configuration files and the command line. It will also setup
# the asynchronous handling systems for communication with the
# repository and the collaboration server
from agileConfig import Config, AsyncHandler
from async import ON_GITHUBNOTIFICATION
try:
    Log = Config().log.logger
except Exception: #IGNORE:W0703
    from petaapan.utilities.console_logger import ConsoleLogger
    Log = ConsoleLogger('AgiMan')
    
import os.path
from glob     import glob
from Storyapp import artefact_types

class StoryAppModel(object):
    def __init__(self, **kwargs):
        self.artefacts = {}
        self.story_files = []
        self.current_backlog = None
        self.current_project = None
        self.current_release = None
        self.current_sprint = None
        self.current_story = None
        self.current_task = None
        self.path = Config().datastore
        Log.debug('Path to repository: %s' % self.path)

        self.get_local_artefacts()
        self.load_artefacts()
        
    def get_local_artefacts(self):
        '''
        Loads the file names of all local artefacts into a dictionary
        keyed on artefact type
        '''
        Log.debug('path: %s' % self.path)
        self.xmlFiles = {}
        for atype in artefact_types.values():
            self.xmlFiles[atype] = []
            self.xmlFiles[atype].append(f for f in glob(
                                os.path.join(self.datastore, atype, '*.xml')))
        
    def load_artefacts(self):
        for type in artefact_types.values():
            for artefact in self.xmlFiles[type]:
                Log.debug('loading %s' % artefact)
                ctrl = self.getArtefact(artefact ,model=ProjectModel,
                    get_artefact='newProject',
                    name=os.path.splitext(os.path.basename(f))[0])
            self.artefacts[p.Id] = (p,{})
            self.newProject(p)
    def load_projects(self):
        for f in self.xmlFiles[artefact_types[PROJECTS]]:
            Log.debug('load only xmlFile: %s' % f)
            
            p = self.getProject(f,model=ProjectModel,
                    get_artefact='newProject',
                    name=os.path.splitext(os.path.basename(f))[0])
            self.artefacts[p.Id] = (p,{})
            self.newProject(p)
    def load_releases(self):
        if self.checked_for_releases: return
        self.checked_for_releases = True
        for f in self.xmlFiles[artefact_types[RELEASES]]:
            Log.debug('only loading release %s' % f)
            r = self.getRelease(f, model=ReleaseModel,
                    get_artefact='newRelease',name=\
                os.path.splitext(os.path.basename(f))[0])
            self.artefacts[r.Id] = (r,{})
            self.newRelease(r)
    def load_sprints(self):
        if self.checked_for_sprints: return
        self.checked_for_sprints = True
        for f in self.xmlFiles[artefact_types[SPRINTS]]:
            Log.debug('only loading sprint %s' % f)
            s = self.getSprint(f, model=SprintModel, name=\
                os.path.splitext(os.path.basename(f))[0])
            self.artefacts[s.Id] = (s, {})
            self.newSprint(s)
    def load_backlog(self):
        Log.debug('BackLog loading:')
        for f in self.xmlFiles[artefact_types[BACKLOG]]:
            b = self.getBacklog(f)
            self.backlog[b.Id] = (b,{})
            self.newBacklog(b)
        Log.debug('Backlog Done loading')
    def load_stories(self):
        if self.checked_for_stories: return
        self.checked_for_stories = True
        Log.debug('Stories loading: ')
        for f in self.xmlFiles[artefact_types[STORIES]]:
            Log.debug('only loading story %s' % f)
            s = self.getStory(f)
            self.artefacts[s.Id] = (s ,{})
            self.newStory(s)
        Log.debug('Stories Done loading')
    def load_tasks(self):
        if self.checked_for_tasks: return
        self.checked_for_tasks = True
        for f in self.xmlFiles[artefact_types[TASKS]]:
            Log.debug('%s' % f)
            t = self.getTask(f, name=\
                os.path.splitext(os.path.basename(f))[0])
            self.artefacts[t.Id] = (t, {})
            self.newTask(t)

    def trash(self,artefact,atype=None):
        if atype is None:# or type is 'stories':
            btn = self.buttons[artefact.Id]
            lbl = self.labels[artefact.Id]
            self.backlog_list_layout.remove_widget(btn)
            self.story_flow.remove_widget(lbl)
            self.remove_widget(artefact)
            del self.artefacts[artefact.Id]
        else:
            if artefact.Id in self.Artifacts:
                dic = self.Artifacts[artefact.Id][1]
                for l in dic.keys():
                    self.__getattribute__(l).remove_widget(dic[l])
                del self.Artifacts[artefact.Id]
                super(StoryApp,self).remove_widget(artefact.view)
        return
    def close(self,touch=None):
        #close all the artefacts
        for a in self.artefacts.values():
            a[0].close()
        for b in self.backlog.values():
            b[0].close()
        self.add_to_git()
        AsyncHandler().shutdown()
        super(StoryApp, self).close(touch)
    
    @property        
    def Artifacts(self):
        return self.artefacts
    