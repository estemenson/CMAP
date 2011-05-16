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
from Storyapp import artifact_types

class StoryAppModel(object):
    def __init__(self, **kwargs):
        self.artifacts = {}
        self.story_files = []
        self.current_backlog = None
        self.current_project = None
        self.current_release = None
        self.current_sprint = None
        self.current_story = None
        self.current_task = None
        self.path = Config().datastore
        Log.debug('Path to repository: %s' % self.path)

        self.get_local_artifacts()
        self.load_atefacts()
        
    def get_local_artifacts(self):
        '''
        Loads the file names of all local artifacts into a dictionary
        keyed on artifact type
        '''
        Log.debug('path: %s' % self.path)
        self.xmlFiles = {}
        for atype in artifact_types.values():
            self.xmlFiles[atype] = []
            self.xmlFiles[atype].append(f for f in glob(
                                os.path.join(self.datastore, atype, '*.xml')))
        
    def load_projects(self):
        for f in self.xmlFiles[artifact_types[PROJECTS]]:
            Log.debug('load only xmlFile: %s' % f)
            
            p = self.getProject(f,model=ProjectModel,
                    get_artifact='newProject',
                    name=os.path.splitext(os.path.basename(f))[0])
            self.artifacts[p.Id] = (p,{})
            self.newProject(p)
    def load_releases(self):
        if self.checked_for_releases: return
        self.checked_for_releases = True
        for f in self.xmlFiles[artifact_types[RELEASES]]:
            Log.debug('only loading release %s' % f)
            r = self.getRelease(f, model=ReleaseModel,
                    get_artifact='newRelease',name=\
                os.path.splitext(os.path.basename(f))[0])
            self.artifacts[r.Id] = (r,{})
            self.newRelease(r)
    def load_sprints(self):
        if self.checked_for_sprints: return
        self.checked_for_sprints = True
        for f in self.xmlFiles[artifact_types[SPRINTS]]:
            Log.debug('only loading sprint %s' % f)
            s = self.getSprint(f, model=SprintModel, name=\
                os.path.splitext(os.path.basename(f))[0])
            self.artifacts[s.Id] = (s, {})
            self.newSprint(s)
    def load_backlog(self):
        Log.debug('BackLog loading:')
        for f in self.xmlFiles[artifact_types[BACKLOG]]:
            b = self.getBacklog(f)
            self.backlog[b.Id] = (b,{})
            self.newBacklog(b)
        Log.debug('Backlog Done loading')
    def load_stories(self):
        if self.checked_for_stories: return
        self.checked_for_stories = True
        Log.debug('Stories loading: ')
        for f in self.xmlFiles[artifact_types[STORIES]]:
            Log.debug('only loading story %s' % f)
            s = self.getStory(f)
            self.artifacts[s.Id] = (s ,{})
            self.newStory(s)
        Log.debug('Stories Done loading')
    def load_tasks(self):
        if self.checked_for_tasks: return
        self.checked_for_tasks = True
        for f in self.xmlFiles[artifact_types[TASKS]]:
            Log.debug('%s' % f)
            t = self.getTask(f, name=\
                os.path.splitext(os.path.basename(f))[0])
            self.artifacts[t.Id] = (t, {})
            self.newTask(t)

    def trash(self,artifact,atype=None):
        if atype is None:# or type is 'stories':
            btn = self.buttons[artifact.Id]
            lbl = self.labels[artifact.Id]
            self.backlog_list_layout.remove_widget(btn)
            self.story_flow.remove_widget(lbl)
            self.remove_widget(artifact)
            del self.artifacts[artifact.Id]
        else:
            if artifact.Id in self.Artifacts:
                dic = self.Artifacts[artifact.Id][1]
                for l in dic.keys():
                    self.__getattribute__(l).remove_widget(dic[l])
                del self.Artifacts[artifact.Id]
                super(StoryApp,self).remove_widget(artifact.view)
        return
    def close(self,touch=None):
        #close all the artifacts
        for a in self.artifacts.values():
            a[0].close()
        for b in self.backlog.values():
            b[0].close()
        self.add_to_git()
        AsyncHandler().shutdown()
        super(StoryApp, self).close(touch)
    
    @property        
    def Artifacts(self):
        return self.artifacts
    