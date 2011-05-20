'''
Created on Oct 9, 2010

@author: stevenson
'''
from agileConfig import Config, AsyncHandler
try:
    Log = Config().log.logger
except Exception: #IGNORE:W0703
    from petaapan.utilities.console_logger import ConsoleLogger
    Log = ConsoleLogger('CMAP')

from cmap.tools.mvc.mvc import Observer, Subject
from xml.dom import minidom
from cmap.tools.uniqueID import uuid
#from cmap.controller.storyapp import Storyapp
from os.path import abspath, join, dirname, basename, exists, splitext
import os
os.environ.setdefault("GIT_PYTHON_TRACE", "full")
class BaseModel(Observer, Subject):
    def __init__(self, ctrl,**kwargs):
        super(BaseModel,self).__init__()
        Subject.__init__(self)
        self.register_observer(ctrl)
        self.dirty = False
        self.file = None
        self._dom = None
        self._Scribbles = {}
        self._TextWidgets = {}
        self._Children = []
        self._Parent = None
        self._Model = None
        self._Id = None
        self._Name = None
        self._Description = None
        self._StartDate = None
        self._EstimateFinishDate = None
        self._EstimateHours = None
        self._ActualFinish = None
        self._ActualHours = None
        self._schema = kwargs['model_str']
        self.datapath = abspath(join(Config().datastore,kwargs['type']))
        if not os.path.exists(self.datapath):
            os.mkdir(self.datapath)
        Log.debug('Creating skeleton %s' % self._schema)
        self.processXml(self.create_model(self._schema))
        self.Id = uuid()
        self.Name = kwargs.setdefault('name','')
        self.Description = kwargs.setdefault('description',' ')
        Log.debug( self._dom.toxml())
        self.dirty = True
    def processXml(self, xmlFile):
        self._dom = minidom.parse(xmlFile)
        self._Model = self._dom.getElementsByTagName(self._schema)[0]
        for element in [n for n in self._Model.childNodes \
                  if n.nodeType == minidom.Node.ELEMENT_NODE]:
            self.parse(element)
        
    def load_from_disk(self,xmlFile):
        if xmlFile is None: return
        self.dirty = False
        self.file = basename(xmlFile)
        _path = dirname(xmlFile)
        if self.datapath != _path:
            Log.info('Importing: %s from: %s' % (self.file,_path))
            self.dirty = True
        else: 
            Log.debug('Loading: %s from: %s' % (self.file,_path))
        self.processXml(xmlFile)
        Log.debug( self._dom.toxml())
    def add_scribble(self,scribble):
        self.Scribbles = scribble #this is actually a property that will take 
        #the contents of this dictionary
    def remove_scribble(self,idu):
        if idu in self.Scribbles:
            del self.Scribbles[idu]
    def scribble_text_change(self, text):
        self.TextFields = text
    def _get_text_widgets(self):
        try:
            return self._TextWidgets
        except Exception: #IGNORE:W0703
            self._TextWidgets = {}
            return self._TextWidgets
    def _get_scribbles(self):
        try:
            return self._Scribbles
        except Exception: #IGNORE:W0703
            self._Scribbles = {} 
            return self._Scribbles
    def _get_id(self):
        try:
            return self._Id
        except Exception: #IGNORE:W0703
            return ''
    def _get_name(self):
        try:
            return self._Name  
        except Exception: return '' #IGNORE:W0703
    def _get_description(self):
        try:
            return self._Description
        except Exception: return '' #IGNORE:W0703
    def _get_start_date(self):
        try:
            return self._StartDate
        except Exception: return '' #IGNORE:W0703
    def _get_estimate_date(self):
        try:
            return self._EstimateFinishDate
        except Exception: return '' #IGNORE:W0703
    def _get_estimate_hours(self):
        try:
            return self._EstimateHours
        except Exception: return '' #IGNORE:W0703
    def _get_actual_hours(self):
        try:
            return self._ActualHours
        except Exception: return '' #IGNORE:W0703
    def _get_parent(self):
        try:
            return self._Parent
        except Exception: return '' #IGNORE:W0703
    def _get_children(self):
        try:
            return self._Children
        except Exception: return [] #IGNORE:W0703
    def _get_actual_date(self):
        try:
            return self._ActualFinish
        except Exception: return '' #IGNORE:W0703
    def _set_id(self,value):
        node = None
        v = value if value else ''
        try:
            self._Id = v
            self.dirty = True
            node = self._dom.getElementsByTagName('Id')[0]
        except Exception: #IGNORE:W0703
            node = self._dom.createElement('Id')
            self._Model.appendChild(node)
            node.appendChild( self._dom.createTextNode(v))
        node.firstChild.data = v
    def _set_name(self, value):
        node = None
        v = value if value else ''
        try:
            self._Name = v
            self.dirty = True
            node = self._dom.getElementsByTagName('Name')[0]
        except Exception: #IGNORE:W0703
            node = self._dom.createElement('Name')
            self._Model.appendChild(node)
            node.appendChild( self._dom.createTextNode(v))
        node.firstChild.data = v
    def _set_description(self, value):
        node = None
        v = value if value else ''
        try:
            self._Description = v
            self.dirty = True
            node = self._dom.getElementsByTagName('Description')[0]
        except Exception: #IGNORE:W0703
            node = self._dom.createElement('Description')
            self._Model.appendChild(node)
            node.appendChild( self._dom.createTextNode(v))
        node.firstChild.data = v
    def _set_start_date(self, value):
        node = None
        v = value if value else ''
        try:
            self._StartDate = v
            self.dirty = True
            node = self._dom.getElementsByTagName('StartDate')[0]
        except Exception: #IGNORE:W0703
            node = self._dom.createElement('StartDate')
            self._Model.appendChild(node)
            node.appendChild( self._dom.createTextNode(v))
        node.firstChild.data = v
    def _set_estimate_date(self, value):
        node = None
        v = value if value else ''
        try:
            self._EstimateFinishDate = v
            self.dirty = True
            node = self._dom.getElementsByTagName('EstimateFinishDate')[0]
        except Exception: #IGNORE:W0703
            node = self._dom.createElement('EstimateFinishDate')
            self._Model.appendChild(node)
            node.appendChild( self._dom.createTextNode(v))
        node.firstChild.data = v
    def _set_estimate_hours(self, value):
        node = None
        v = value if value else ''
        try:
            self._EstimateHours = v
            self.dirty = True
            node = self._dom.getElementsByTagName('EstimateHours')[0]
        except Exception: #IGNORE:W0703
            node = self._dom.createElement('EstimateHours')
            self._Model.appendChild(node)
            node.appendChild( self._dom.createTextNode(v))
        node.firstChild.data = v
    def _set_actual_date(self, value):
        node = None
        v = value if value else ''
        try:
            self._ActualFinish = v
            self.dirty = True
            node = self._dom.getElementsByTagName('ActualFinish')[0]
        except Exception: #IGNORE:W0703
            node = self._dom.createElement('ActualFinish')
            self._Model.appendChild(node)
            node.appendChild( self._dom.createTextNode(v))
        node.firstChild.data = v
    def _set_actual_hours(self, value):
        node = None
        v = value if value else ''
        try:
            self._ActualHours = v
            self.dirty = True
            node = self._dom.getElementsByTagName('ActualHours')[0]
        except Exception: #IGNORE:W0703
            node = self._dom.createElement('ActualHours')
            self._Model.appendChild(node)
            node.appendChild( self._dom.createTextNode(v))
        node.firstChild.data = v
    def _set_parent(self, value):
        '''
        Setter for the parent of an artefact
        The attribute is the actual artefact object that is the parent of this
        artefact.
        The value argument is the artefact object of the parent
        The XML element for Parent has two attributes
        a) The type of the parent - this is the name of the XML Document
           element for the parent
        b) The Id of the actual parent
        '''
        if value is self or value is self._Parent:
            return #Can not be parent of self
        self.dirty = True
        pe = None
        try:
            pe = self._dom.getElementsByTagName('Parent')[0]
        except Exception: #IGNORE:W0703
            pe = self._dom.createElement('Parent')
        if value:
            pe.setAttribute('Id', value)
        else:
            if pe.hasAttribute('Id'):
                pe.removeAttribute('Id')
        self._Parent = value
        
    def _set_children(self, value):
        if value is None: return
        self.dirty = True
        if value not in self._Children:
            self._Children.append(value)
        ce = None
        try:
            ce = self.dom.getElementsByTagName('Children')[0]
        except Exception: #IGNORE:W0703
            ce = self.dom.createElement('Children')
            ce.setAttribute('List', '')
            self._Model.appendChild(ce)
        for c in ce.childNodes:
            if c.nodeName == '#text':
                continue
            if c.hasAttribute('Id') and c.getAttribute('Id') == value:
                return # Already in XML - don't duplicate
        e = self.dom.createElement('Child')
        e.setAttribute('Id', value)
        ce.appendChild(e)
    def _set_scribbles(self,value):
        if not value or not value.get('Id',None): return
        idu = value['Id']
        self.dirty = True
        if not idu in self._Scribbles:
            self._Scribbles[idu] = {}
        for k,v in value.iteritems():
            if not k in ['Id','Dom']:
                if k in ['Color', 'Cdata'] and isinstance(v, unicode):
                    self._Scribbles[idu][k] = eval(v)
                else:
                    self._Scribbles[idu][k] = v
        if value['Dom']:return #we are parsing the xml file no need to continue
        #this is new Data
        ce = None
        try:
            ce = self.dom.getElementsByTagName('Scribbles')[0]
        except Exception: #IGNORE:W0703
            ce = self.dom.createElement('Scribbles')
            self._Model.appendChild(ce)
        scrib = self.find_child(idu, ce)
        if not scrib:
            #we need to create this as anew Scribble
            e = self.dom.createElement('Scribble')
            e.setAttribute('Id', idu)
            ce.appendChild(e)
        scrib.setAttribute('Color', str(value['Color']))
        s = str(value['Cdata'])
        if scrib.firstChild:
            scrib.firstChild.data = s
        else:
            scrib.appendChild(self.dom.createCDATASection(s))
        try:
            print('changes:%s' % self._dom.toxml())
        except Exception: #IGNORE:W0703
            pass
    def _set_text_widgets(self,value):
        if not value or not value.get('Id',None): return
        idu = value['Id']
        if not 'pos' in value and not value['Dom']:
            #delete this textWidget from DOM
            return self.removeTextWidget(idu)
        self.dirty = True
        if not idu in self._TextWidgets:
            self._TextWidgets[idu] = {}
        for k,v in value.iteritems():
            if not k in ['Dom']:
                if k in ['Color'] and isinstance(v, unicode):
                    self._TextWidgets[idu][k] = eval(v)
                else:
                    self._TextWidgets[idu][k] = v
        if value['Dom']:return #we are parsing the xml file no need to continue
        #this is new Data
        ce = None
        try:
            ce = self.dom.getElementsByTagName('TextFields')[0]
        except Exception: #IGNORE:W0703
            ce = self.dom.createElement('TextFields')
            self._Model.appendChild(ce)
        scrib = self.find_child(idu, ce)
        if not scrib:
            #we need to create this as anew Scribble
            scrib = self.dom.createElement('Scribble')
            scrib.setAttribute('Id', idu)
            ce.appendChild(scrib)
        scrib.setAttribute('Color', str(value['Color']))
        scrib.setAttribute('Font-Size', str(value['Font-Size']))
        scrib.setAttribute('size', str(value['size']))
        scrib.setAttribute('pos', str(value['pos']))
        s = value['Cdata']
        if scrib.firstChild:
            scrib.firstChild.data = s
        else:
            scrib.appendChild(self.dom.createCDATASection(s))
        try:
            print('changes:%s' % self._dom.toxml())
        except Exception: #IGNORE:W0703
            pass
    def removeTextWidget(self,idu):
        try:
            if idu in self._TextWidgets:
                del self._TextWidgets[idu]
            te = self.dom.getElementsByTagName('TextFields')[0]
        except Exception: #IGNORE:W0703
            return
        t = self.find_child(idu, te)
        if t:
            te.removeChild(t)
    def find_child(self,idu, parent):
        for t in parent.childNodes:
            if t.nodeName == '#text':
                continue
            if t.getAttribute('Id') == idu:
                return t
        return None
    def _get_dom(self): return self._dom
    def _set_dom(self, value):
        self._dom = value
    dom = property(_get_dom, _set_dom)
    @property
    def ArtefactType(self):
        return self._dom.documentElement.nodeName
        
    Id = property(_get_id, _set_id)    
    Name = property(_get_name, _set_name)
    TextFields = property(_get_text_widgets,_set_text_widgets)
    Scribbles = property(_get_scribbles, _set_scribbles)
    Description = property(_get_description, _set_description)
    StartDate = property(_get_start_date, _set_start_date)
    EstimateFinishDate = property(_get_estimate_date, _set_estimate_date)
    EstimateHours = property(_get_estimate_hours, _set_estimate_hours)
    ActualFinish = property(_get_actual_date, _set_actual_date)
    ActualHours = property(_get_actual_hours, _set_actual_hours)
    Parent = property(_get_parent, _set_parent)
    Children = property(_get_children, _set_children)
    
    def removeChild(self, value):
        if value is None: return
    
    def create_model(self, atype):
        self.dirty = True
        return abspath(join(Config().xmlTemplates,('%s.xml' % atype)))
    def parse(self,node):
        numChildren = len(node.childNodes)
        if numChildren == 0 and not node.hasAttribute('List'):
            if node.hasAttribute('Id') or node.firstChild:
                self.__setattr__(node.nodeName, node.firstChild.data\
                                                if not node.hasAttribute('Id')\
                                                else node.getAttribute('Id'))
        elif numChildren == 1 and node.firstChild.nodeName == '#text':
            self.__setattr__(node.nodeName, node.firstChild.data)
        else:
            self.parseList(node)
    def parseList(self,node):
        for c in node.childNodes:
            if c.nodeName == '#text':
                continue
            value = None
            if c.hasAttribute('Id') and c.tagName not in['Scribble','TextArea']:
                value = c.getAttribute('Id')
            else:
                if c.firstChild and c.tagName not in ['Scribble', 'TextArea']:
                    value = c.firstChild.data
                else:
                    if not c.firstChild : continue
                    value = {'Dom': True, 'Cdata': c.firstChild.data}
                    for a in c._attrs: #IGNORE:W0212
                        value[a]=c.getAttribute(a)
            try:
                self.__setattr__(node.nodeName, value)
            except Exception: #IGNORE:W0703
                pass
    def listData(self, target, atype):
        ret = []
        from cmap.controller.storyapp import Storyapp
        for c in target:
            aro = Storyapp().artefacts[c]
            if aro.ArtefactType == atype:
                ret.append(c)
        return ret
    def trash(self):
        if self.file is None: return
        f = join(self.datapath, self.file)
        if exists(f):
            AsyncHandler().rm(f)
            
    def close(self):
        Log.debug('closing: %s' % join(self.datapath, self.file))
        self.save(True)
    def createFileName(self):
        self.file = '%s.xml' % self.Id
        self.dirty = True
    def save(self, closing=False):
        fn = [] # Will hold the list of files that were saved to persistent storage
        # Save all our dirty relatives to persistent storage
        self.internalSave(fn)
        # Put all the changes into the repository
        if len(fn):
            if closing:
                AsyncHandler().save(fn, 'changes made to %s' % self.Id)
            else:
                AsyncHandler().commit(fn, 'changes made to %s' % self.Id)
            
    def internalSave(self, fnp):
        if self.dirty:
            if not self.Id: return
            if self.file is None:
                self.createFileName()
            s = splitext(self.file)[0] #strip off the extension
            if s != self.Id:
                #name has changed, the id of this model is also the name
                #of the xml file holding the data, if the original file does not
                #exist then we can simply create a new file, and commit it to 
                #the repository otherwise we use git to rename the file
                of = join(self.datapath, self.file)
                self.createFileName()
                nf = join(self.datapath, self.file)
                if exists(of):
                    AsyncHandler().mv(of, nf)
            fn = join(self.datapath, self.file)
            with open(fn, 'w') as f:
                self._dom.writexml(f)
            fnp.append(fn)
            self.dirty = False
            # Save our dirty parents
            from cmap.controller.storyapp import Storyapp
            p = Storyapp().artefacts
            if self.Parent:
                try:
                    p[self.Parent][0].internalSave(fnp)
                except KeyError:
                    pass
            # Save our dirty children
            if self.Children:
                for c in self.Children:
                    try:
                        p[c][0].internalSave(fnp)
                    except KeyError:
                        pass
           
        