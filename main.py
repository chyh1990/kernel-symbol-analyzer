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
  name = ''
  info = ''
  stype = ord('?')
  linenum = 0
  oid = DUMMY_OID #dummy
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

    if self.is_def():
      sid = self.__get_sid()
      if not (sid == DUMMY_OID or sid == -1):
        print 'ERROR:', self.name ,'redefined'
        return 
      if sid == -1:
        cur.execute('''INSERT INTO symbols VALUES (NULL, ?, ?, ?, ?, ?)''',  (self.name, self.stype, self.oid, self.linenum, self.info))
      else:
        cur.execute('''UPDATE symbols SET oid=? WHERE name=? AND oid=?''', (self.oid, self.name, DUMMY_OID))
    else:
      self.oid = DUMMY_OID
      sid = self.__get_sid()
      if sid == -1:
        cur.execute('''INSERT INTO symbols VALUES (NULL, ?, ?, ?, ?, ?)''',  (self.name, self.stype, self.oid, self.linenum, self.info))
      else:
        pass

class kobject:
  def __init__(self, path):
    (self.path, self.name) = os.path.split(path)
    self.id = 0
    self.syms = []

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
      if x.is_def():
        x.oid = self.oid
      x.save()
    conn.commit()
    pass

  def __str__(self):
    return self.name + ' ' + str(len(self.syms))


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
                  info TEXT,
                  CONSTRAINT fk_symbols_objs
                    FOREIGN KEY (oid) REFERENCES objects(oid)
                  );''')
  cur.execute('''CREATE INDEX name_idx ON symbols(name);''')
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

  print 'Filling...'
  print 'DONE'

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print_usage()
    sys.exit()
  cmd = sys.argv[1]
  if cmd == 'create':
    create_db()
  elif cmd == 'test':
    syms = kobject(os.path.join(KERNEL, 'drivers', 'base', 'core.o'))
    syms.parseFile()
    print syms
    syms.save()
  else:
    print_usage()
  pass
