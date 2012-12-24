#!/bin/bash

#FUNS=$(./dummySource.py)

LINESTART=$(grep -n '*SourceNotFound' __dummy.autogen.c|sed -r 's/:.*//g')
LINEEND=$(grep -n '*NotFound' __dummy.autogen.c|sed -r 's/:.*//g')

FUNS=$(sed -n "$LINESTART,$LINEEND"p __dummy.autogen.c|grep "SYMBOLS:"|sed 's/\/\* SYMBOLS: //g')
for f in $FUNS
do
  echo "/* " $f "*/"
  OBJ=$(./indexer.py def $f|grep OBJECT|sed 's/OBJECT://g')
  SRC=${OBJ/%.o/.c}
  echo $(./getproto.py $SRC $f) "{TRACE;return 0;}"
  echo 
done
