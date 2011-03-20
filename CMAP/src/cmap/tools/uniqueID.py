'''
Created on Jul 30, 2010

@author: stevenson
'''
## {{{ http://code.activestate.com/recipes/213761/ (r1)
import time, random, md5
import socket

def uuid( *args ):
    """
        Generates a universally unique ID.
        Any arguments only create more randomness.
    """
    t = long( time.time() * 1000 )
    r = long( random.random()*100000000000000000L )
    a = None
    try:
        a = socket.gethostbyname( socket.gethostname() )
    except:
        # if we can't get a network address, just imagine one
        a = random.random()*100000000000000000L
    data = str(t)+' '+str(r)+' '+str(a)+' '+str(args)
    data = md5.md5(data).hexdigest()
    return data
## end of http://code.activestate.com/recipes/213761/ }}}
