#!/usr/bin/env python
import os, sys
import re
from parserlib import *

P = re.compile("(.+?):.+?undefined reference to [`'](.+)[`']")


def onesym(listNF, listSNF, listF, symbolname):
  cur = conn.cursor()
  eq = '='
  cur.execute('''SELECT objects.path, objects.name, symbols.src, symbols.linenum, symbols.name FROM objects, symbols
                  WHERE objects.oid=symbols.oid 
                  AND symbols.name=? AND (symbols.type=84 OR symbols.type=116);''', (symbolname,))
  rs = cur.fetchall()
  if len(rs)==0:
    print 'Definition Not Found:', symbolname
    listNF.append(symbolname)
    return
  else:
    for x in rs:
      if x[3]!=0:
        listF.append((symbolname, x))
        return
    return listSNF.append((symbolname, rs[0]))

def NotFound(f, l):
  f.write('''
/* 
 *NotFound: %d
 */
\n''' % (len(l)))
  for x in l:
      f.write('''
/* SYMBOLS: %s */
''' % (x,))
  f.write('\n\n')

def SourceNotFound(f, l):
  f.write('''
/* 
 *SourceNotFound: %d
 */
\n''' % (len(l)))
  for x in l:
      f.write('''
/* SYMBOLS: %s
 * OBJECT: %s
 */\n''' % (x[0], x[1][1]))

  f.write('\n\n')

def Found(f, l):
  f.write('''
/* 
 *Dummies: %d
 */
\n''' % (len(l)))
  sorted(l, key=lambda x:x[1][2])
  for x in l:
    fileName, fileExtension = os.path.splitext(x[1][2])
    if fileExtension == '.c':
      f.write('''
/* SYMBOLS: %s
 * SOURCE: %s:%d
 */\n''' % (x[0], x[1][2], x[1][3]))
      defStat = getFunctionDef(x[1][2], x[1][3])
      ret = ''
      if not defStat.startswith('void'):
        ret = 'return 0;'
      f.write('_DDE_WEAK '+ defStat+'{TRACE;'+ret+'}\n')
    else:
      SourceNotFound(f, [x])
  f.write('\n\n')

def main():
  syms = set()
  f = open(sys.argv[1])
  of = open('__dummy.autogen.c', 'w')
  while True:
    line = f.readline()
    if not line: break
    m = P.match(line)
    if not m:
      continue
    #print m.group(1), m.group(2)
    sn = m.group(2)
    if sn not in syms:
      syms.add(sn)
  f.close()
  print 'SYMBOLS:', len(syms)
  lNF = []
  lSNF = []
  lF = []
  for x in syms:
    onesym(lNF, lSNF, lF, x)

  Found(of, lF)
  SourceNotFound(of, lSNF)
  NotFound(of, lNF)

if __name__ == '__main__':
  if len(sys.argv)<2:
    print 'usage: dummyGenerator.py [link output]'
    sys.exit(0)
  main()

