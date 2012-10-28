#!/usr/bin/env python
import os, sys
import re
from parserlib import *

P = re.compile('(.+?):.+?undefined reference to [`'](.+)[`']')

def main():
  syms = set()
  f = open(sys.argv[1])
  while True:
    line = f.readline()
    if not line: break
    m = P.match(line)
    if not m:
      continue
    print m[2]
  f.close()

if __name__ == '__main__':
  if len(sys.argv)<2:
    print 'usage: dummyGenerator.py [link output]'
    sys.exit(0)
  main()

