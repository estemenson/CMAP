# -*- coding: utf-8 -*-
'''
Created on 2010-09-16

@author: steve
'''
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from cmap.gestures.NewGestures import CaptureGesture
from agileConfig import Config
try:
    Log = Config().log.logger
except:
    from petaapan.utilities.console_logger import ConsoleLogger
    Log = ConsoleLogger('CMAP')

from pymt.graphx.colors import set_color
from pymt.graphx.draw import drawRectangle, drawLine, drawLabel
class MyCaptureWidget(CaptureGesture):
    def __init__(self,gdb,storyApp):
        self.StoryApp = storyApp
        super(MyCaptureWidget,self).__init__(gdb)
    def action_close_popup(self,form):
        return True
    def not_gesture(self,gesture, touch):
        return True
    def on_gesture(self, gesture, touch):
        # try to find gesture from database
        best = self.gdb.find(gesture, minscore=0.8)
        if best:
            Log.debug('Gesture detected %s:%s' %\
                      (best[0],best[1].label))
            self.lastbest = best
            if best[1].label in ['Backlog','Backlog1', 'Backlog2']:
                self.StoryApp.flow_pressed('backlog_flow_open',
                                        self.StoryApp.dragable_backlog_flow)
            elif best[1].label in ['Projects','Projects1', 'Projects2']:
                self.StoryApp.flow_pressed('projects_flow_open',
                                        self.StoryApp.dragable_project_flow)
            elif best[1].label in ['Sprints','Sprints1', 'Sprints2']:
                self.StoryApp.flow_pressed('sprint_flow_open',
                                        self.StoryApp.dragable_sprint_flow)
            elif best[1].label in ['New Story']:
                self.StoryApp.new_story_pressed(None, pos=gesture.strokes[0].screenpoints[-1])
            elif best[1].label in ['Releases','Releases1', 'Releases2']:
                self.StoryApp.flow_pressed('releases_flow_open',
                                        self.StoryApp.dragable_release_flow)
            elif best[1].label in ['Tasks','Tasks1', 'Tasks2']:
                self.StoryApp.flow_pressed('task_flow_open',
                                            self.StoryApp.dragable_task_flow)
            elif best[1].label in ['Square', 'square']:
                self.StoryApp.flow_pressed('story_flow_open',
                                            self.StoryApp.dragable_story_flow)
            elif best[1].label in ['X', 'x']:
                self.StoryApp.unfullscreen()
        else:
            self.lastbest = None
    def draw(self):
        # draw background
        set_color(*self.bgcolor)
        drawRectangle(pos=self.pos, size=self.size)

        # draw current trace
        set_color(1,1,1)
        for trace in self.points:
            l = []
            for p in self.points[trace]:
                l.append(p[0])
                l.append(p[1])
            drawLine(l)
        labeltext = ''
        if self.lastbest:
            labeltext = 'Creating : %s' % self.lastbest[1].label
        
        s = self.width *.1
        drawLabel(label=labeltext, pos=(self.pos[0] + s*3, self.pos[1] + \
                            self.height + s * 0.8 + self.height * 0.07),
                font_size=self.height * 0.07, center=False)
    