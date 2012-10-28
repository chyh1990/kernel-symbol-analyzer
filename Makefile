CROSS_COMPILE ?= arm-linux-
CC:=$(CROSS_COMPILE)gcc
LD:=$(CROSS_COMPILE)ld
AR:=$(CROSS_COMPILE)ar
SRCDIR?=working
DRIVERS=drivers

KERNEL:=/home/chenyh/os/linux

CFLAGS+=-I$(KERNEL)/arch/arm/mach-omap2/include
CFLAGS+=-I$(KERNEL)/arch/arm/plat-omap/include
CFLAGS+=-I$(KERNEL)/arch/arm/include/generated
CFLAGS+=-I$(KERNEL)/arch/arm/include -I$(KERNEL)/include 
CFLAGS+=-D__KERNEL__ -D__KERN__ -D__LINUX_ARM_ARCH__
CFLAGS+=-include $(KERNEL)/include/linux/kconfig.h
CFLAGS+=-march=armv7-a
CFLAGS+=-DDEBUG

include $(SRCDIR)/Makefile.inc
MOD_NAME?=unknown

OBJS:=$(CSRC:.c=.o)
OBJS+=$(ASMSRC:.S=.o)
OBJS:=$(addprefix $(SRCDIR)/, $(OBJS))

all: $(SRCDIR)/lib$(MOD_NAME).a $(SRCDIR)/_module.o drivers

%.o: %.S
	$(CC) -c $(CFLAGS) -D__ASSEMBLY__ -o $@ $<

$(SRCDIR)/_module.o: $(OBJS)
	$(LD) -r -o $@ $(OBJS)

$(SRCDIR)/lib$(MOD_NAME).a: $(OBJS)
	$(AR) rcs $@ $(OBJS)

.PHONY: drivers clean

DRIVEROBJ:=char_example.o

DRIVEROBJ:=$(addprefix $(DRIVERS)/, $(DRIVEROBJ))
drivers: _drivers.o

_drivers.o: __dummy.autogen.c __dummy.o $(DRIVEROBJ)
	$(LD) -r -o $@ __dummy.o $(DRIVEROBJ)

clean:
	rm -f $(OBJS) *.o $(DRIVEROBJ) $(SRCDIR)/_module.o $(SRCDIR)/lib$(MOD_NAME).a
