'''
Created on Jul 28, 2010

@author: stevenson
'''
class Subject(object):
    def __init__(self):
        self.observers = []
    def deregister_observer(self, value):
        if value in self.observers:
            self.observers.remove(value)
            
    def register_observer(self,value):
        if value not in self.observers:
            self.observers.append(value)

class Observer(object):
    def __init__(self):
        self.subjects = []
    def subscribe(self,subject):
        if not subject in self.subjects:
            subject.register_observer(self)
            self.subjects.append(subject)
    def unsuscribe(self, subject):
        if subject in self.subjects:
            subject.deregister_observer(self)
            self.subjects.remove(subject)