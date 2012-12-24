#!/usr/bin/env python

import os, re, sys
f = open('__dummy.autogen.c', 'r')
while True:
  line = f.readline()
  if not line: break
  if line.find('*SourceNotFound:')!=-1:
    break

p = re.compile('.*SYMBOLS:\s(\w+).*')
while True:
  line = f.readline()
  if not line: break
  m = p.match(line)
  if m:
    print m.group(1).strip()

