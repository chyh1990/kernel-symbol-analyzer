CROSS_COMPILE ?= arm-linux-
CC:=$(CROSS_COMPILE)gcc
LD:=$(CROSS_COMPILE)ld
SRCDIR?=working

KERNEL:=/home/chenyh/os/linux

CFLAGS+=-I$(KERNEL)/arch/arm/mach-omap2/include
CFLAGS+=-I$(KERNEL)/arch/arm/plat-omap/include
CFLAGS+=-I$(KERNEL)/arch/arm/include/generated
CFLAGS+=-I$(KERNEL)/arch/arm/include -I$(KERNEL)/include 
CFLAGS+=-D__KERNEL__ -D__KERN__ -D__LINUX_ARM_ARCH__
CFLAGS+=-include $(KERNEL)/include/linux/kconfig.h
CFLAGS+=-march=armv7-a

include $(SRCDIR)/Makefile.inc

OBJS:=$(CSRC:.c=.o)
OBJS+=$(ASMSRC:.S=.o)
OBJS:=$(addprefix $(SRCDIR)/, $(OBJS))

all: $(SRCDIR)/_module.o

%.o: %.S
	$(CC) -c $(CFLAGS) -D__ASSEMBLY__ -o $@ $<

$(SRCDIR)/_module.o: $(OBJS)
	$(LD) -r -o $@ $(OBJS)

clean:
	rm -f $(OBJS) _module.o
