#!/usr/bin/env python

import os, sys
import re, popen2
import shutil

KERNEL =  '/home/chenyh/os/linux'
#WORKDIR = './working'
WORKDIR = sys.argv[1]

def need_copy(name):
  if os.path.isdir(name):
    return True
  if name.endswith('.h'):
    return True
  if name.endswith('.c') or name.endswith('.S'):
    if os.path.isfile(name[:-2] + '.o'):
      return True
  return False

def copytree(src, dst, symlinks=False):
    names = os.listdir(src)
    os.makedirs(dst)
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        if not need_copy(srcname):
          continue
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks)
            else:
                print 'copy', name
                shutil.copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
    if errors:
      print errors
      raise Exception(errors)

def copy34(relp):
  tp = os.path.join(WORKDIR, relp)
  sp = os.path.join(KERNEL, relp)
  copytree(sp, tp)

def genMakefile(modname, parent):
  f = open(os.path.join(WORKDIR, 'Makefile.inc'),'w')
  f.write('MOD_NAME:= '+modname+'\n\n')
  clist = []
  asmlist = []
  for root, dirs, files in os.walk(parent):
    if root:
      if root.startswith(WORKDIR):
        root = root[len(WORKDIR):]
        if root.startswith('/'):
          root = root[1:]
      for x in files:
        if x.endswith('.c'):
          clist.append(os.path.join(root, x))
        if x.endswith('.S'):
          asmlist.append(os.path.join(root, x))
  for x in asmlist:
    f.write('ASMSRC+=' + x + '\n')
  f.write('\n')
  for x in clist:
    f.write('CSRC+=' + x +'\n')

  f.close()

def copyone(name):
  d = os.path.split(name)[0]
  try:
    os.makedirs(os.path.join(WORKDIR,d))
  except:
    pass
  shutil.copy2(os.path.join(KERNEL, name), os.path.join(WORKDIR, name))

def arch_arm():
  copy34('arch/arm/common')
  copy34('arch/arm/mach-omap2')
  copy34('arch/arm/plat-omap')
  copy34('arch/arm/include')
  genMakefile('arm', WORKDIR)

def drivers_base():
  copy34('drivers/base')
  copyone('fs/internal.h')
  copyone('fs/char_dev.c')
  copyone('kernel/resource.c')
  copyone('kernel/smpboot.h')
  copyone('kernel/cpu.c')
  genMakefile('base', WORKDIR)

def main():
#  drivers_base()
  arch_arm()

if __name__ == '__main__':
  main()
