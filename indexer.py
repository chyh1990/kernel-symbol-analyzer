#!/usr/bin/env python
import sqlite3
import sys, os, re
import popen2
import linecache
from collections import deque

from parserlib import *

def print_usage():
  print 'Usage: '


def create_db():
  cur = conn.cursor()
  print 'Deleting Old Table...'
  cur.execute('''DROP TABLE IF EXISTS objects;'''); 
  cur.execute('''DROP TABLE IF EXISTS symbols;'''); 
  cur.execute('''DROP TABLE IF EXISTS obj_depends;'''); 
  print 'Creating Schema...'
#objects
  cur.execute('''CREATE TABLE objects(
                  oid INTEGER PRIMARY KEY,
                  name TEXT NOT NULL,
                  path TEXT
                  );''')
  cur.execute('''CREATE INDEX object_name_idx ON objects(name);''')
#dummy entry, oid == 1
  cur.execute('''INSERT INTO objects VALUES (NULL, '__dummy.o', '')''')
#symbols
  cur.execute('''CREATE TABLE symbols(
                  sid INTEGER PRIMARY KEY,
                  name TEXT NOT NULL,
                  type INTEGER,
                  oid INTEGER,
                  linenum INTEGER,
                  solved BOOLEAN,
                  info TEXT,
                  src  TEXT,
                  CONSTRAINT fk_symbols_objs
                    FOREIGN KEY (oid) REFERENCES objects(oid)
                  );''')
  cur.execute('''CREATE INDEX name_idx ON symbols(name);''')
  cur.execute('''CREATE INDEX s_oid_idx ON symbols(oid);''')
  cur.execute('''CREATE UNIQUE INDEX name_oid_UNIQUE ON symbols(name,oid);''')


#sym_depends
  cur.execute('''CREATE TABLE obj_depends(
                  oid INTEGER NOT NULL,
                  dependon_oid INTEGER NOT NULL,
                  CONSTRAINT fk_depends_sym0
                    FOREIGN KEY(oid) REFERENCES objects(oid),
                  CONSTRAINT fk_depends_sym1
                    FOREIGN KEY(dependon_oid) REFERENCES objects(oid)
                    );''');
  cur.execute('''CREATE INDEX objd_oid_idx ON obj_depends(oid)''')
  cur.execute('''CREATE UNIQUE INDEX objd_idx_UNQ ON obj_depends(oid, dependon_oid)''')
  conn.commit()

  print 'Filling...'
  print 'DONE'

def solveSymbol():
  cur = conn.cursor()
  curw = conn.cursor()
  cur.execute('''SELECT oid FROM objects''')
  objs = []
  robjs = cur.fetchall()
  for r in robjs:
    cur1 = conn.cursor()
    cur1.execute('''SELECT * FROM symbols WHERE oid=? AND type=84''', (r[0],))
    exportSyms = cur1.fetchall()
    for x in exportSyms:
      o = ksymbol.from_tuple(x)
      cur1.execute('''SELECT oid FROM symbols WHERE name=? AND (type=85 OR type=117)''', (o.name,))
      while True:
        r1 = cur1.fetchone()
        if not r1: break
        try:
          curw.execute('''INSERT INTO obj_depends VALUES (?,?)''', (r1[0], r[0]))
        except sqlite3.IntegrityError:
          pass
      curw.execute('''UPDATE symbols SET solved=1 WHERE name=? AND (type=85 OR type=117)''', (o.name,))
  #unsolvable
  for r in robjs:
    cur1.execute('''SELECT * FROM symbols WHERE oid=? AND (type=85 OR type=117) AND solved=0''', (r[0],))
    if cur1.fetchone():
      curw.execute('''INSERT INTO obj_depends VALUES (?,?)''', (r[0], DUMMY_OID))

  conn.commit()
  print 'Done'

def getObjectFileList(root):
  objlist = []
  for root, dirs, files in os.walk(root):
    if root:
      for x in files:
        if x.endswith('.o') and x != 'built-in.o':
          objlist.append(kobject(os.path.join(root, x)))
  return objlist

from Queue import Queue
from threading import Thread

indexQueue = Queue()
def indexWorker():
  while True:
    objfile = indexQueue.get()
    print 'new job:', str(objfile)
    objfile.parseFile()
    #objfile.save()
    indexQueue.task_done() 

def doIndex(root):
  objlist = getObjectFileList(root)
  num_worker_threads = 1
  for i in xrange(num_worker_threads):
    t = Thread(target=indexWorker)
    t.daemon = True
    t.start()

  for x in objlist:
    indexQueue.put(x)
  indexQueue.join()
#save all objects
  for x in objlist:
    x.save()
  conn.commit()

def calcFullDependency(modulename):
  if not modulename.endswith('.o'):
    modulename += '.o'
  cur = conn.cursor()
  cur.execute('''SELECT * FROM objects WHERE name=?''', (modulename,))
  robj = cur.fetchone()
  if not robj:
    print modulename, 'Not Found'
    return
  obj = kobject.from_tuple(robj)
  foundnodes= set()
  q = deque()
  q.append(obj.oid)
  foundnodes.add(obj.oid)
  print obj
  while len(q) > 0:
    n = q.popleft()
    cur.execute('''SELECT dependon_oid FROM obj_depends WHERE oid=?''', (n,))
    for x in cur.fetchall():
      if x[0] in foundnodes:
        continue
      foundnodes.add(x[0])
      q.append(x[0])

  print 'Depend:', len(foundnodes)
  for x in foundnodes:
    print '\t',kobject.from_oid(x)
  #obj.loadSymbols()



if __name__ == '__main__':
  if len(sys.argv) < 2:
    print_usage()
    sys.exit()
  cmd = sys.argv[1]
  if cmd == 'create':
    create_db()
  elif cmd == 'index':
    objlist = doIndex(os.path.join(KERNEL, 'drivers'))
    objlist = doIndex(os.path.join(KERNEL, 'arch'))
    objlist = doIndex(os.path.join(KERNEL, 'net'))
    objlist = doIndex(os.path.join(KERNEL, 'kernel'))
    objlist = doIndex(os.path.join(KERNEL, 'mm'))
    objlist = doIndex(os.path.join(KERNEL, 'lib'))
    objlist = doIndex(os.path.join(KERNEL, 'init'))
    objlist = doIndex(os.path.join(KERNEL, 'fs'))
    objlist = doIndex(os.path.join(KERNEL, 'block'))
  elif cmd == '__test':
    #syms = kobject(os.path.join(KERNEL, 'drivers', 'base', 'core.o'))
    #syms.parseFile()
    #print syms
    #syms.save()
    objlist = getObjectFileList(os.path.join(KERNEL, 'drivers/'))
    for x in objlist:
      x.parseFile()
      print x
      x.save()
  elif cmd == 'dump':
    if len(sys.argv) < 3 or sys.argv[2]=='':
      dumpModule()
    else:
      dumpModule(sys.argv[2])
  elif cmd == 'depend':
    if len(sys.argv) < 3 or sys.argv[2]=='':
      print_usage()
    else:
      calcFullDependency(sys.argv[2])
  elif cmd == 'solve':
    solveSymbol()
  elif cmd == 'def' or cmd=='deflike':
    if len(sys.argv) < 3 or sys.argv[2]=='':
      print_usage()
    else:
      findDefine(sys.argv[2])
  else:
    print_usage()
  conn.close()
