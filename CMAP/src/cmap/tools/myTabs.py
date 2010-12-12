'''
Created on Aug 9, 2010

@author: stevenson
'''
from pymt.ui.widgets.composed.tabs import MTTabs
from pymt.ui.colors import css_add_sheet
from pymt.parser import parse_color
MyTabsCSS = '''
.tabs1css {
    bg-color: rgba(250, 55, 55, 255);
    color-normal: rgba(250, 55, 55, 255);
    border-color: rgb(180, 120, 120);
    border-width: 5;
    draw-border: True;    
}
.currenttabscss {
    bg-color: rgba(30, 155, 235, 255);
    color-normal: rgba(30, 155, 235, 255);
    border-color: rgb(180, 75, 50);
    border-width: 10;
    draw-border: True;    
}
'''
css_add_sheet(MyTabsCSS)

class MyTabs(MTTabs):
    def __init__(self, **kwargs):
        self.tab_style = \
        {
         'bg-color': parse_color('rgba(185,211,238, 255)'),
#         'bg-color': parse_color('rgba(219, 219, 219, 255)'),
         'border-color': parse_color('rgba(187, 187, 187,255)'),
         'color-normal': parse_color('rgba(0,0,0,255)'),
         'border-width': 5,
         'draw-border': True,    
         'color': parse_color('rgba(0,0,0,255)'),    
         'border-radius': 5,
         'border-radius-precision': .01
        }
        self.active_tab_style = \
        {
 #        'bg-color': parse_color('rgba(185,211,238, 255)'),
         'bg-color': parse_color('rgba(230, 230, 230, 255)'),
         'border-color': parse_color('rgba(150, 205, 205,255)'),
         'color-normal': parse_color('rgba(0,0,0,255)'),
         'border-width': 10,
         'draw-border': True,    
         'color': parse_color('rgba(0,0,0,255)'),
         'border-radius': 10,
         'border-radius-precision': .01
        }
        super(MyTabs, self).__init__(**kwargs)
        self.cur_button = None
        
    def add_widget(self, widget, tab=None):
        
        super(MyTabs,self).add_widget(widget,tab)
        #self.tabs[tab][0].cls = 'tabs1css'
        self.apply_selected(self.tabs[tab][0])
        
    def apply_selected(self,btn,active=False):
        if not active:
            btn.style.update(self.tab_style)
        else:
            btn.style.update(self.active_tab_style)
            

    def select(self, tab, *l):
        if tab not in self.tabs:
            return
        if self.cur_button:
            #self.cur_button.cls = 'tabs1css'
            self.apply_selected(self.cur_button)
        super(MyTabs,self).select(tab, *l)
        self.cur_button = self.tabs[tab][0]
        #self.cur_button.cls = 'currenttabscss'
        self.apply_selected(self.cur_button, True)
    