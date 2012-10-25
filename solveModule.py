#!/usr/bin/env python
from parserlib import *

if __name__ == '__main__':
  o = kobject(sys.argv[1])
  o.parseFile()
  print o
  for x in o.syms:
    t = chr(x.stype)
    if t=='u' or t=='U':
      findDefine(x.name)

