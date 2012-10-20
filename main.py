#!/usr/bin/env python
import sqlite3
import sys, os, re
import popen2


DBNAME = 'symbol.db'
CROSS_PREFIX = 'arm-linux-'
KERNEL = '/home/chenyh/os/linux'

conn = sqlite3.connect(DBNAME)
DUMMY_OID = 1

def print_usage():
  print 'Usage: '

class ksymbol:
  sid = 0
  name = ''
  info = ''
  stype = ord('?')
  linenum = 0
  oid = DUMMY_OID #dummy
  solved = False
  __P = re.compile('([\s\w]+)\s([a-zA-Z?])\s([\w.]+)\s?(.*)')
  def __str__(self):
    return chr(self.stype) + ' ' +self.name + '\t' + self.info + '\t' + str(self.linenum)

  @staticmethod
  def from_nm(line):
    o = ksymbol()
    m = ksymbol.__P.match(line)
    if not m:
      return
    o.info = m.group(1).strip()
    o.stype = ord(m.group(2)[0])
    o.name = m.group(3).strip()
    if len(m.group(4)) != 0:
      try:
        t = m.group(4).split(':')
        o.linenum = int(t[1])
      except:
        pass
    if o.stype != ord('U'):
      o.solved = True
    return o

  @staticmethod
  def from_tuple(t):
    o = ksymbol()
    (o.sid, o.name, o.stype, o.oid, o.linenum, o.solved, o.info) = t
    return o

  def is_def(self):
    t = chr(self.stype)
    if t == 't' or t== 'T':
      return True
    else:
      return False

  def __get_sid(self):
    cur = conn.cursor()
    cur.execute('''SELECT * FROM symbols WHERE name=? AND oid=?''', (self.name, self.oid))
    r = cur.fetchone()
    if r:
      return r[0]
    else:
      return -1

  def save(self):
    cur = conn.cursor()
    if self.is_def() and self.oid == DUMMY_OID:
      print 'ERROR: define no oid'
      return

      #FIXME
    try:
      cur.execute('''INSERT INTO symbols VALUES (NULL, ?, ?, ?, ?,?, ?)''',  (self.name, self.stype, self.oid, self.linenum, self.solved, self.info))
    except:
      print 'ERROR:', self.name ,'redefined'

class kobject:
  def __init__(self, path=''):
    (self.path, self.name) = os.path.split(path)
    self.id = 0
    self.syms = []
    self.dependon = []

  def parseFile(self):
    nm = CROSS_PREFIX + 'nm'
    path = os.path.join(self.path, self.name)
    cmd = nm + ' -l ' + '"' + path + '"'
    p = popen2.Popen3(cmd, False)
    lines = []

    while True:
      line = p.fromchild.readline()
      if not line:
        break
      lines.append(line.rstrip())
    exitcode = p.wait()
    if exitcode != 0:
      print 'ERROR:', path
      return 0
    for x in lines:
      o = ksymbol.from_nm(x)
      if not o:
        print 'Failed to parse:', x
        continue
      o.oid = self.id
      self.syms.append(o)
    return len(self.syms)

  def __get_oid(self):
    cur = conn.cursor()
    cur.execute('''SELECT * FROM objects WHERE name=? AND path=?;''', (self.name, self.path))
    r = cur.fetchone()
    if r:
      return r[0]
    else:
      return 0

  @staticmethod
  def from_tuple(t):
    o = kobject()
    (o.oid, o.name, o.path) = t
    return o

  def loadSymbols(self):
    cur = conn.cursor()
    cur.execute('''SELECT * FROM symbols WHERE oid=?''', (self.oid,))
    while True:
      r = cur.fetchone()
      if not r:break
      self.syms.append(ksymbol.from_tuple(r))  

  def save(self):
    cur = conn.cursor()
    oid = self.__get_oid()
    if oid == 0:
      print 'new obj:', self.name
      cur.execute('''INSERT INTO objects VALUES (NULL, ?, ?);''', (self.name, self.path))
      self.oid = self.__get_oid()
      oid = self.oid
    else:
      print 'WARNING:', self.name, 'exists'
      self.oid = oid

    for x in self.syms:
      x.oid = self.oid
      x.save()
    conn.commit()
    pass

  def __str__(self):
    return os.path.join(self.path, self.name) + ' ' + str(len(self.syms))


def create_db():
  print 'Creating Schema...'
  cur = conn.cursor()
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

def loadAll():
  cur = conn.cursor()
  cur.execute('''SELECT * FROM objects''')
  objs = []
  while True:
    r = cur.fetchone()
    if not r:
      break
    objs.append(kobject.from_tuple(r))

  for x in objs:
    x.loadSymbols()

  for x in objs:
    cur.execute('''SELECT dependon_oid from obj_depends WHERE oid=?''', (x.oid,))
    for y in cur.fetchall():
      x.dependon.append(objs[y[0] - DUMMY_OID])
  return objs

def dumpAll():
  objs = loadAll()
  for x in objs:
    print x
    print 'DEPEND_ON:'
    for y in x.dependon:
      print '\t', y
    print 'SYMS:'
    for y in x.syms:
      print '\t', y

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


if __name__ == '__main__':
  if len(sys.argv) < 2:
    print_usage()
    sys.exit()
  cmd = sys.argv[1]
  if cmd == 'create':
    create_db()
  elif cmd == 'index':
    objlist = doIndex(os.path.join(KERNEL, 'drivers/base'))
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
    dumpAll()
  elif cmd == 'solve':
    solveSymbol()
  else:
    print_usage()
  conn.close()
