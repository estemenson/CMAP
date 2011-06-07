# -*- coding: utf-8 -*-
'''
Created on 2010-10-02

@author: jonathan
'''

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import Queue
import httplib

import pymt.base
import pymt.event
from petaapan.utilities.gitmanager import GitManager, SAVE, COMMIT, MV,\
                                          RM, GIT_RESPONSE, SHUTDOWN,\
                                          VERSION, EXEC_PATH
from petaapan.publishsubscribeclient.fromCollaboration\
               import FROM_COLLABORATION, ServerManager
from petaapan.publishsubscribeclient.toCollaboration\
               import TO_COLLABORATION, SUBSCRIPTION_RESPONSE, ToCollaboration
from petaapan.publishsubscribeserver.pssDef import GITHUB_NOTIFICATION
from agileConfig import Config
Log = Config().log.logger

ON_GITSAVE = 'on_gitsave'
ON_GITSHUTDOWN = 'on_gitshutdown'
ON_GITCOMMIT = 'on_gitcommit'
ON_GITMV = 'on_gitmv'
ON_GITRM = 'on_gitrm'
ON_GITVERSION = 'on_gitversion'
ON_GITPATH = 'on_gitpath'
ON_GITHUBNOTIFICATION = 'on_githubnotification'
ON_SUBSCRIPTION_RESPONSE = 'on_subscriptionresponse'
GIT_PUBLISHER = 'github'
git_version = None
git_path = None



SHUTDOWN_TIMEOUT = 15

handler_mapper = {GIT_RESPONSE: {SAVE: ON_GITSAVE,
                                 COMMIT: ON_GITCOMMIT,
                                 MV: ON_GITMV,
                                 RM: ON_GITRM,
                                 VERSION: ON_GITVERSION,
                                 EXEC_PATH: ON_GITPATH},
                  FROM_COLLABORATION:\
                                  {GITHUB_NOTIFICATION: ON_GITHUBNOTIFICATION},
                  TO_COLLABORATION:\
                              {SUBSCRIPTION_RESPONSE: ON_SUBSCRIPTION_RESPONSE}
                 }


class Async(pymt.event.EventDispatcher):


    def __init__(self):
        self._git = None
        self._collaborationFrom = None
        self._collaborationTo = None
        self._no_collaboration = False
        self._localrepo = Config().datastore if Config().datastore else None
        self._response_queue = Queue.Queue(0)
        pymt.event.EventDispatcher.__init__(self)
        self._outstanding_events = 0
        
        # Create the asynchronous objects
        if self._localrepo:
            self._git = GitManager(self._localrepo,
                                   not Config().sharedRepoNotAvailable,
                                   self._response_queue,
                                   log=Log)
        if not Config().collaborationNotAvailable:
            self._collaborationFrom = ServerManager(\
                                           response_queue=self._response_queue,
                                           host='0.0.0.0',
                                           port=Config().local_port,
                                           log=Log)
            self._collaborationTo = ToCollaboration(\
                                           self._response_queue,
                                           host='0.0.0.0',
                                           port=Config().collaboration_port,
                                           log=Log)
        else:
            self._no_collaboration = True
        # These are the events we will dispatch
        self.register_event_type(ON_GITSAVE)
        self.register_event_type(ON_GITCOMMIT)
        self.register_event_type(ON_GITMV)
        self.register_event_type(ON_GITRM)
        self.register_event_type(ON_GITVERSION)
        self.register_event_type(ON_GITPATH)
        self.register_event_type(ON_GITHUBNOTIFICATION)
        self.register_event_type(ON_SUBSCRIPTION_RESPONSE)
        # We will get notified from the main event loop on each loop
        # iteration
        pymt.base.getWindow().push_handlers(self)
        # Start the asynchronous processing threads
        if self._localrepo:
            self._git.start()
            self._git.version()
            self._git.exec_path()
        if not self._no_collaboration:
            self._collaborationFrom.start()
            self._collaborationTo.start()
            self.subscribe(True)

    
    def logAsyncInfo(self, ret):
        if ret is None:
            return
        msg = ret[1]
        # Log stdout messages
        if len(msg) <= 1:
            pass
        if msg[1]:
            for l in msg[1]:
                Log.info(l)
        # Log stderr messages
        if msg[2]:
            for l in msg[2]:
                if msg[0] == 0:
                    Log.info(l)
                else:
                    Log.error(l)
                    
            
    def on_gitsave(self, ret):
        self._outstanding_events -= 1
        Log.debug('Git save completed - outstanding events %s'\
                   % self._outstanding_events)
        assert(self._outstanding_events >= 0)
        self.logAsyncInfo(ret)
            
    def on_gitcommit(self, ret):
        self._outstanding_events -= 1
        Log.debug('Git commit completed - outstanding events %s'\
                   % self._outstanding_events)
        assert(self._outstanding_events >= 0)
        self.logAsyncInfo(ret)
            
    def on_gitmv(self, ret):
        self._outstanding_events -= 1
        Log.debug('Git mv completed - outstanding events %s'\
                   % self._outstanding_events)
        assert(self._outstanding_events >= 0)
        self.logAsyncInfo(ret)
            
    def on_gitrm(self, ret):
        self._outstanding_events -= 1
        Log.debug('Git rm completed - outstanding events %s'\
                   % self._outstanding_events)
        assert(self._outstanding_events >= 0)
        self.logAsyncInfo(ret)
        
    def on_gitversion(self, ret):
        self._outstanding_events -= 1
        Log.debug('Git --version completed - outstanding events %s'\
                  % self._outstanding_events)
        assert(self._outstanding_events <= 0)
        self.logAsyncInfo(ret)
        
    def on_gitpath(self, ret):
        self._outstanding_events -= 1
        Log.debug('Git --exec-path completed - outstanding events %s'\
                  % self._outstanding_events)
        assert(self._outstanding_events <= 0)
        self.logAsyncInfo(ret)
        
    def on_githubnotification(self, ret):
        msg = ret[1]
        Log.debug('Handle Github notification')
        user = Config().collaborationUser
        need_pull = False
        for c in msg['commits']:
            if user != c['author']['email']:
                need_pull = True
        if need_pull:
            self.save(None, 'Received notification of new content from Github')
        
    def on_subscriptionresponse(self, ret):
        self._outstanding_events -= 1
        assert(self._outstanding_events >= 0)
        msg = ret[1]
        Log.debug('Got subscription response: %s'\
                   % 'accepted' if msg[0] == httplib.OK else 'rejected')
        if msg[0] != httplib.OK:
            if len(msg) > 2 and len(msg[2]) > 2 and msg[2][2] is not None:
                Log.error('Problematic HTTP response: %s' % str(msg[2]))
            else:
                Log.error('Subscription call failed:  result: %i  reason: %s'
                          % (msg[0], str(msg[1])))
        
    def on_update(self):
        '''
        The main event loop is telling us to check if we have anything
        queued from any of our asynchronous processes.
        If so let our subscribers know
        '''
        try:
            while True: # drain the event queue
                ret = self._response_queue.get(False)
                # Dispatch the event to the registered handlers
                Log.debug('About to dispatch %s' % str(ret))
                self.dispatch_event(handler_mapper[ret[0]][ret[1][0]], ret[1])
        except Queue.Empty:
            pass
        
    def isEmpty(self):
        return self._response_queue.empty()

    def save(self, files, message):
        if not self._localrepo:
            return # Local repo not present - don't do anything Git related
        self._outstanding_events += 1
        self._git.save(files, message)
        
    def commit(self, files, message):
        if not self._localrepo:
            return
        self._outstanding_events += 1
        Log.debug('About to run Git commit: %s' % self._outstanding_events)
        self._git.commit(files, message)
        
    def mv(self, old, new):
        self._outstanding_events += 1
        Log.debug('About to run Git mv: %s' % self._outstanding_events)
        self._git.mv(old, new)
        
    def rm(self, target):
        self._outstanding_events += 1
        Log.debug('About to run Git rm: %s' % self._outstanding_events)
        self._git.rm(target)
        
    def subscribe(self, on):
        if self._no_collaboration:
            return
        msg = self._collaborationTo.constructSubscriptionMsg(\
                        on, Config().gitSubscription,
                        Config().collaborationResponseUrl,
                        Config().local_port, 
                        Config().collaborationUser,
                        testing=Config().testingServer)
        Log.debug('About to change subscription status %s' % on)
        self._outstanding_events += 1
        self._collaborationTo.subscribe(msg, Config().collaborationServerUrl,
                                        Config().collaboration_port,
                                        Log.warning)

    def shutdown(self):
        # We need to handle any outstanding events before we shutdown
        try:
            if self._collaborationTo:
                # Unsubscribe from the collaboration server
                self.subscribe(False)
                while self._git and self._outstanding_events > 0:
                    try:
                        ret = self._response_queue.get(True, SHUTDOWN_TIMEOUT)
                        Log.debug('Async return in shutdown: %s' % str(ret))
                        if not ret or not ret[1]:
                            continue
                        if ret[1][0] == SHUTDOWN:
                            continue # No event handler for shutdown
                        self.dispatch_event(handler_mapper[ret[0]][ret[1][0]],
                                            ret[1])
                    except Queue.Empty:
                        self._outstanding_events = 0
        finally:
            if self._collaborationFrom and not self._collaborationFrom.broken:
                self._collaborationFrom.server.shutdown()
                self._collaborationFrom = None
            if self._collaborationTo:
                self._collaborationTo.shutdown()
                self._collaborationTo = None
            if self._git:
                ret = self._git.shutdown()
                self._git = None # Prevent recursive shutdown
                if ret is not None:
                    self.logAsyncInfo(ret[1])
                    self._outstanding_events = 0
