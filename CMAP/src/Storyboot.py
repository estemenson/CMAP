# -*- coding: utf-8 -*-
'''
Created on 2010-09-06

@author: jonathan
'''

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


import sys
import pprint
pprint.pprint(sys.path)
from petaapan.utilities.console_logger import ConsoleLogger
Log = ConsoleLogger('CMAP')


def main():
    global Log
    # This must be done BEFORE trying to import any PYMT stuff since PyMT
    # messes with the arguments
    from agileConfig import AgiConfig
    config = AgiConfig(Log)
    if config.noDatastore:
        Log.critical('No data store defined or accessible')
        sys.exit(2)
    if config.pymtUnavailable:
        Log.critical('PyMT is not available')
        sys.exit(2)
    if config.args.loglevel:
        Log.level = config.args.loglevel
    from agileConfig import AsyncHandler
    from pymt.ui.window import MTWindow
    from pymt.base import runTouchApp, stopTouchApp
    from cmap.controller.storyapp import StoryApp
    from cmap.tools.myTools import get_min_screen_size, scale_tuple
    from cmap.view.stories.storyViews import TestController
    import os
    
    
    Log.debug('current directory: %s' % os.path.abspath(os.path.curdir))
    if config.args.startdir:
        os.chdir(config.args.startdir)
        Log.debug('current directory: %s' % os.path.abspath(os.path.curdir))
    # Get the PyMT window    
    w = MTWindow()

    
    b = None
    try:
        if config.args.storycard:
            if config.args.storycard == 'flow':
                from pymt.ui.widgets.coverflow import MTCoverFlow
                from glob import glob
                from pymt.ui.widgets.button import MTImageButton
                from pymt.loader import Loader
                base_image = os.path.join(os.path.dirname(__file__),'examples',
                                           'framework','images')
                coverflow = MTCoverFlow(size=w.size)
                for filename in glob(os.path.join(base_image, '*.png')):
                    button = MTImageButton(image=Loader.image(filename))
                    button.title = os.path.basename(filename)
                    coverflow.add_widget(button)
            
                runTouchApp(coverflow)
                return
            else:            
                Log.debug('Testing stories only...')
                b = TestController(w, config.args.storycard)
        elif not config.args.fullscreen:
            Log.debug('Running in non fullscreen mode...')
            #Setup our application window
            size = get_min_screen_size()
            w.size = scale_tuple(size,0.045)
            scale = .13
            size = scale_tuple(w.size, scale)
            pos = (w.size[0] - (size[0] +55), w.size[1] - (size[1] +35))
            b = StoryApp(root_window=w,size=size, pos=pos,
                                   control_scale=0.7)
        else:
            Log.debug('Fullscreen mode...')
            b = StoryApp(root_window=w,size=w.size, pos=(0,0), 
                                  control_scale=0.7).view
        w.add_widget(b)
        b.fullscreen()
        # Run the application
        Log.debug("About to run CMAP")
        runTouchApp()
        b.close(None)
        Log.debug('CMAP normal exit')
        return
    except Exception:
        Log.exception('Exception causing premature CMAP exit')
        # We need to make sure that everything shuts down cleanly
        stopTouchApp()
        if AsyncHandler() is not None:
            AsyncHandler().shutdown()
        Log.debug('CMAP exception exit')
        raise
    
    
if __name__ == '__main__':
    main()
    exit(0)
