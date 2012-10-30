MOD_NAME:=ddelinux
CSRC+=misc.c
CSRC+=lock.c
CSRC+=main.c
CSRC+=timer.c
CSRC+=slab.c

CFLAGS+= -I/home/chenyh/os/ucore_plus/ucore/src/kern-ucore/glue-ucore
