MYDIR=`pwd`
LINUXDIR=/home/chenyh/os/linux

cd $LINUXDIR
pwd
export ARCH=arm
export CROSS_COMPILE=arm-eabi-
export CFLAGS=-g
git checkout v3.6
cp config.pandaboard .config
make oldconfig && make -j6

if [[ $? -ne 0 ]]; then
  echo "failed to build kernel"
  exit -1
fi

if [[ ! -f $LINUXDIR/vmlinux ]]; then
  echo "kernel not compiled"
  exit -1
fi

cd $MYDIR
#: > __dummy.autogen.c

KERNEL_OLD_TIMESTAMP=$(cat .kerneldate 2>/dev/null)
KERNEL_TIME=$(stat -c "%Y" $LINUXDIR/vmlinux)

if [[ $KERNEL_TIME -ne $KERNEL_OLD_TIMESTAMP ]] || [ ! -f symbol.db ]; then
  echo $KERNEL_TIME > .kerneldate
  rm -f symbol.db 
  ./indexer.py create
  ./indexer.py index
  ./indexer.py solve
else
  echo "Kernel not updated, skip updating database"
fi

make SRCDIR=mod_base 
make SRCDIR=mod_ddelib
make SRCDIR=mod_linux
