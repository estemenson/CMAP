'''
Created on 2011-06-09

@author: hotsoft
'''
import itertools

if __name__ == '__main__':
    i = itertools.chain(range(3), range(4), range(5))
    print list(i)
    def f(): 
        t = (1,2)
        return t[0],t[1]
    print f()
    x,y = 0,0
#    if x > 0:
#        if y > 100:
#            raise ValueError("Value for y is too large.")
#        else:
#            return y
#    else:
#        if x == 0:
#            return False
#        else:
#            raise ValueError("Value for x cannot be negative.")
    if x == 0: print False
    if x < 0: raise ValueError("Value for x cannot be negative.")
    if y > 100: raise ValueError("Value for y is too large.")
    print y    