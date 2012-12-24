#!/usr/bin/env python
import re, os ,sys

funs = []
fun2def = {}

pH = re.compile('^((static|inline)\s)*(\w+)\s+(\w+::)?(\w+)\s*\([^)]*')
p = re.compile('^((static|inline)\s)*(\w+)\s+(\w+::)?(\w+)\s*\(.*\)')
fn = sys.argv[1]
#print 'Parse', fn
f = open(fn, 'r')
while True:
  line = f.readline()
  if not line: break
  m = p.match(line)
  if m:
    #print m.group(0)
    funs.append(m.group(5))
    fun2def[m.group(5)] = m.group(0).strip()
    continue
  #multiline definition
  m = pH.match(line)
  if m:
    #print line.rstrip()
    defstr = line.strip()
    funname = m.group(5)
    funs.append(funname)
    while True:
      line = f.readline()
      if not line:
        fun2def[funname] = defstr
        break
      defstr += line.strip()
      #print line.rstrip()
      if line.rstrip().endswith(')'):
        fun2def[funname] = defstr
        break
    continue
f.close()

#print fun2def
findfun = ''
if len(sys.argv) > 2:
  findfun = sys.argv[2]
if findfun:
  fun2def.setdefault(findfun, '__ERROR_NOT_FOUND__')
  print fun2def[findfun]
else:
  for k,v in fun2def.items():
    print k,v
