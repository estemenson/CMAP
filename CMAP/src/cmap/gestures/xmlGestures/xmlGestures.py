'''
Created on Jun 3, 2010

@author: stevenson
'''
from xml.dom import minidom

class Gestures:
    def __init__(self, xmlFile):
        self.dom = minidom.parse(xmlFile)
        self.gestureHash = {}
        #self.gestureList = self.dom.getElementsByTagName('Gesture')
        for gesture in self.dom.getElementsByTagName('Gesture'):
            xid =  self.getText(gesture.getElementsByTagName('Id')[0].childNodes)
            self.gestureHash[xid] = Gesture(
                    self.getText(gesture.getElementsByTagName('Label')[0].childNodes),
                    xid,
                    self.getText(gesture.getElementsByTagName('StringRep')[0].childNodes))
            
        #=======================================================================
        # for gesture in doc.getElementsByTagName('Gesture'):
        #    print self.getText(gesture.getElementsByTagName('Label')[0].childNodes)
        #    print self.getText(gesture.getElementsByTagName('Id')[0].childNodes)
        #    print self.getText(gesture.getElementsByTagName('StringRep')[0].childNodes)
        #=======================================================================
        
    def getGestureStrRep(self, id):
        return self.gestureHash[id].getStringRep() #(gesture.getElementsByTagName('StringRep')[0].childNodes)
        
    
    def getText(self,nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

class Gesture:
    def __init__(self, label, id, strRep):
        self.label = label
        self.id = id
        self.strRep = strRep
        
    def setLabel(self, value):
        self.label = value
    def getLabel(self):
        return self.label
    def setId(self, value):
        self.id = value
    def getId(self):
        return self.id
    def setStringRep(self, value):
        self.strRep = value
    def getStringRep(self):
        return self.strRep

#print doc.toxml()
#===============================================================================
# for gesture in doc.getElementsByTagName('Gesture'):
#    print getText(gesture.getElementsByTagName('Label')[0].childNodes)
#    print getText(gesture.getElementsByTagName('Id')[0].childNodes)
#    print getText(gesture.getElementsByTagName('StringRep')[0].childNodes)
#===============================================================================
