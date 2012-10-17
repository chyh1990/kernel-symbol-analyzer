#!/usr/bin/env python
import sqlite3
import sys, os, re

DBNAME = 'symbol.db'

def print_usage():
  print 'Usage: '

def create_db():
  print 'Creating Schema...'
  conn = sqlite3.connect(DBNAME)
  cur = conn.cursor()
#objects
  cur.execute('''CREATE TABLE objects(
                  oid INTEGER PRIMARY KEY,
                  name TEXT NOT NULL,
                  path TEXT
                  );''')
  cur.execute('''CREATE INDEX object_name_idx ON objects(name);''')
#symbols
  cur.execute('''CREATE TABLE symbols(
                  sid INTEGER PRIMARY KEY,
                  name TEXT NOT NULL,
                  type INTEGER,
                  oid INTEGER,
                  linenum INTEGER,
                  CONSTRAINT fk_symbols_objs
                    FOREIGN KEY (oid) REFERENCES objects(oid)
                  );''')
  cur.execute('''CREATE UNIQUE INDEX name_UNIQUE ON symbols(name);''')


#sym_depends
  cur.execute('''CREATE TABLE sym_depends(
                  sid INTEGER NOT NULL,
                  dependon_sid INTEGER NOT NULL,
                  CONSTRAINT fk_depends_sym0
                    FOREIGN KEY(sid) REFERENCES symbols(sid),
                  CONSTRAINT fk_depends_sym1
                    FOREIGN KEY(dependon_sid) REFERENCES symbols(sid)
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
  else:
    print_usage()
  pass
