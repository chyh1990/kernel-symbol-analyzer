#!/bin/bash

FUNS=$(./dummySource.py)

for f in $FUNS
do
  echo $f
  OBJ=$(./indexer.py def $f|grep OBJECT|sed 's/OBJECT://g')
  SRC=${OBJ/%.o/.c}
  ./getproto.py $SRC |grep -A 3 $f
  echo 
done
