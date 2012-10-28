#!/usr/bin/env python
from parserlib import *

if __name__ == '__main__':
  if len(sys.argv)<2:
    print 'usage: checkCollision.py [f1] [f1]...'
    sys.exit(0)
  o = []
  for x in xrange(1,len(sys.argv)):
    obj = kobject(sys.argv[x])
    if obj.parseFile()>0:
      o.append(obj)
  syms = set()
  for x in o:
    for s in x.syms:
      if s.name=='':
        continue
      if s.stype==ord('T'):
        if s.name in syms:
          print s.name
        else:
          syms.add(s.name)
        
