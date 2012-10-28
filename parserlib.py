import sqlite3
import sys, os, re
import popen2
import linecache
from collections import deque

CROSS_PREFIX = 'arm-linux-'
KERNEL = '/home/chenyh/os/linux'
DUMMY_OID = 1
DBNAME = 'symbol.db'
conn = sqlite3.connect(DBNAME)

def getConnection():
  return conn 

class ksymbol:
  sid = 0
  name = ''
  info = ''
  stype = ord('?')
  linenum = 0
  oid = DUMMY_OID #dummy
  solved = False
  src = ''
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
        o.src = t[0]
        o.linenum = int(t[1])
      except:
        pass
    if o.stype != ord('U'):
      o.solved = True
    return o

  @staticmethod
  def from_tuple(t):
    o = ksymbol()
    (o.sid, o.name, o.stype, o.oid, o.linenum, o.solved, o.info, o.src) = t
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
      cur.execute('''INSERT INTO symbols VALUES (NULL, ?, ?, ?, ?,?, ?, ?)''',  (self.name, self.stype, self.oid, self.linenum, self.solved, self.info, self.src))
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

  @staticmethod
  def from_oid(oid):
    cur = conn.cursor()
    cur.execute('''SELECT * FROM objects WHERE oid=?''', (oid,))
    r = cur.fetchone()
    if not r:
      return None
    return kobject.from_tuple(r)

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
    pass

  def __str__(self):
    return os.path.join(self.path, self.name) + ' ' + str(len(self.syms))


def loadAll(cur):
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

def dumpModule(name=None):
  cur = conn.cursor()
  cur.execute('''SELECT * FROM objects''')
  objs = loadAll(cur)
  for x in objs:
    if name and (x.name.find(name) == -1):
      continue
    print x
    print 'DEPEND_ON:'
    for y in x.dependon:
      print '\t', y
    print 'SYMS:'
    for y in x.syms:
      print '\t', y

def getFunctionDef(fn, ln):
  fileName, fileExtension = os.path.splitext(fn)
  if fileExtension != '.c':
    return linecache.getline(fn, ln).strip()
  line = ''
  while True:
    line += linecache.getline(fn, ln).strip()
    ln += 1
    if line=='': break 
    if line.count('(') == line.count(')'):
      break
    line += ' '

  line.replace('{','')
  line.replace('}','')
  return line.rstrip()


def findDefine(symbolname):
  cur = conn.cursor()
  eq = '='
  cur.execute('''SELECT objects.path, objects.name, symbols.src, symbols.linenum, symbols.name FROM objects, symbols
                  WHERE objects.oid=symbols.oid 
                  AND symbols.name LIKE ? AND (symbols.type=84 OR symbols.type=116);''', (symbolname,))
  rs = cur.fetchall()
  if len(rs)==0:
    print 'Definition Not Found:', symbolname
  else:
    for x in rs:
      print 'SYMBOL:', x[4]
      print 'OBJECT:', os.path.join(x[0], x[1])
      print 'SOURCE:', x[2]+':'+str(x[3])
      line = getFunctionDef(x[2], x[3])
      if line == '':
        print 'Source unavailable'
      else:
        print line
      print ''
 
