#!/usr/bin/env python
import re, os ,sys

pH = re.compile('^((static|inline)\s)*(\w+)\s+(\w+::)?(\w+)\([^)]*')
p = re.compile('^((static|inline)\s)*(\w+)\s+(\w+::)?(\w+)\(.*\)')
fn = sys.argv[1]
print 'Parse', fn
f = open(fn, 'r')
iscomm = False
while True:
  line = f.readline()
  if not line: break
  if line.startswith('/* <<CN'):
    print ''
    iscomm = True
  if iscomm and line.find('*/')>=0:
    print ' */'
    iscomm = False
  if iscomm==True:
    print line.rstrip()
    continue
  m = p.match(line)
  if m:
    print m.group(0)
    continue
  #multiline definition
  m = pH.match(line)
  if m:
    print line.rstrip()
    while True:
      line = f.readline()
      if not line:break
      print line.rstrip()
      if line.rstrip().endswith(')'):
        break
    continue
f.close()
