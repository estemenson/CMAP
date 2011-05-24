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
from random import choice
try:
    Log = Config().log.logger
except Exception: #IGNORE:W0703
    from petaapan.utilities.console_logger import ConsoleLogger
    Log = ConsoleLogger('CMAP')


# Determine maximum physical screen size
from cmap.view.baseViews import minimal_size
from cmap.tools.myTools import get_min_screen_size, scale_tuple
#from cmap.controller.storyapp import Storyapp

min_size = get_min_screen_size()


from pymt.ui.window import MTWindow
from cmap.tools.mvc.mvc import Observer, Subject
from pymt.base import runTouchApp

class ArtefactController(Subject,Observer):
    def __init__(self, main, defn=None, **kwargs):
        super(ArtefactController,self).__init__()
        self.root = main
        self._view = None
        self._view_image = None
        self.story_view_size = None
        self.origin_size = scale_tuple(self.root.size,0.25)
        self.isMinimal = True
        self._mini_view_type = kwargs['mini_view_type']
        self._view_type = kwargs['view_type']
        self._view_type_name = kwargs['view_type_name']
        self._p_artefact = kwargs.setdefault('p_artefact',None)
        self._x_range = range(int(self.root.x + int(minimal_size[0]/2)), 
                              int(self.root.width - minimal_size[0]))
        self._y_range = range(int(self.root.y + 100), 
                              int(self.root.height - minimal_size[1]))
        self.isNew = not defn
        self._model = None
        self.createModel(defn, **kwargs)
        if defn is None:
            self._name = ''
            self._description = ''
    def save(self, touch=None): #IGNORE:W0613
        try:
            self._model.save()
        except Exception: #IGNORE:W0703
            pass
        finally:
            if self.isNew:
                self.view.add_new_artefact(self, )
                self.isNew = False
            
    def internalSave(self, fn):
        self._model.internalSave(fn)
    def close(self):
        try:
            self._model.close()
        except Exception: pass #IGNORE:W0703
    def trash(self):
        if self.Id:
            self._model.trash()
            from cmap.controller.storyapp import Storyapp
            self.root.trash(self, Storyapp().artefacts)
#        for o in self.observers:
#            try:
#                o.trash(self.view)
#                pass
#            except:
#                pass        
    def createModel(self,defn, **kwargs):
        kwargs['p_artefact'] = self._p_artefact
        self.Model = kwargs['model'](self, **kwargs)
        self._model.load_from_disk(defn)
    def scribble_text_change(self, text):
        text['Dom'] = False
        self.Model.scribble_text_change(text)
    def add_scribble(self, scribble):
        scribble['Dom'] = False
        self.Model.add_scribble(scribble)
    def remove_scribble(self, ident):
        self.Model.remove_scribble(ident)
    def newDialog(self, minv):
        _p = (self._mini_view_type if minv else self._view_type)(self,self,
                            type_name=self._view_type_name,
                            name=self.Name, id=self.Id)
        #if minv: _p.size = minimal_size  
        _p.pos = self.get_new_random_position()
        self._view = _p
        return _p        
    def app_btn_pressed(self):
        #toggle the story
        self.view.minimize()
    def get_story_size(self):
        if self.story_view_size is None \
        or self.story_view_size != self.origin_size:
            self.story_view_size = self.origin_size
        return self.story_view_size
    def switch_view(self, minv):
        self.isMinimal = minv
        self.root.remove_widget(self.view)
        self.root.add_widget(self,self.view)
    def get_new_random_position(self):
        return (choice(self._x_range),choice(self._y_range))
    @property
    def view(self):
        if self._view is None:
            self.newDialog(True)
        return self._view
    
    def get_image(self):
        return self._view_image
    def set_image(self, im):
        pass
    image = property(get_image, set_image)
    
    @property
    def Id(self): return self._model.Id
    @property
    def Scribbles(self): 
        return self._model.Scribbles
    @property
    def TextFields(self):
        return self._model.TextFields
    def _get_name(self):
        if self.Id is None:
            return self._model.Name 
        return self._model.Name   
    def _set_name(self, value):
        if self._model.Name != value: 
            self._model.Name = value
            for o in self.observers:
                try:
                    o.update_story_btn_name(self.view)
                except Exception: #IGNORE:W0703
                    pass
    Name = property(_get_name, _set_name)
    def _get_description(self):
        if self.Id is None: return self._description 
        return self._model.Description
    def _set_description(self, value):
        if self.Id is None:
            self._description = value
        else: 
            self._model.Description = value
    Description = property(_get_description, _set_description)
    def _get_start_date(self): return self._model.StartDate  
    def _set_start_date(self, value): 
        self._model.StartDate = value
    StartDate = property(_get_start_date, _set_start_date)
    def _get_estimate_date(self): return self._model.EstimateFinishDate
    def _set_estimate_date(self, value): 
        self._model.EstimateFinishDate = value
    EstimateDate = property(_get_estimate_date, _set_estimate_date)
    def _get_estimate_hours(self): return self._model.EstimateHours
    def _set_estimate_hours(self, value): 
        self._model.EstimateHours = value
    EstimateHours = property(_get_estimate_hours, _set_estimate_hours)
    def _get_actual_date(self): return self._model.ActualFinish
    def _set_actual_date(self, value): self._model.ActualFinish = value
    ActualDate = property(_get_actual_date, _set_actual_date)
    def _get_actual_hours(self): return self._model.ActualHours
    def _set_actual_hours(self, value): self._model.ActualHours = value
    ActualHours = property(_get_actual_hours, _set_actual_hours)
    def _get_model(self):
        return self._model
    def _set_model(self, value):
        self._model = value
    Model = property(_get_model, _set_model)
    def _get_parent(self): return self._model.Parent
    def _set_parent(self, value): 
        self._model.Parent = value
    Parent = property(_get_parent, _set_parent)
    def _get_children(self): return self._model.Children
    def _set_children(self, value):
        self._model.Children = value
    Children = property(_get_children, _set_children)
    @property
    def ArtefactType(self): return self._model.ArtefactType
    @property
    def dom(self): return self._model.dom
    



if __name__ == '__main__':
    root = MTWindow()
    project = ArtefactController(root)
    runTouchApp()