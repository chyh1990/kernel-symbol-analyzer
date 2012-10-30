/*
 * =====================================================================================
 *
 *       Filename:  misc.c
 *
 *    Description:  
 *
 *        Version:  1.0
 *        Created:  10/28/2012 04:41:33 PM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  Chen Yuheng (Chen Yuheng), chyh1990@163.com
 *   Organization:  Tsinghua Unv.
 *
 * =====================================================================================
 */
#include <linux/kernel.h>

#include <dde_kit/printf.h>

/* basic functions */
int printk(const char *s, ...)
{
  va_list ap;
  va_start(ap, s);
  int cnt = dde_kit_vprintf(s, ap);
  va_end(ap);
  return cnt;
}

void panic(const char *fmt, ...)
{
  dde_kit_print("DDEPANIC");
  while(1);
}


void warn_slowpath(const char *file, int line, const char *fmt, ...)
{
  va_list ap;
  va_start(ap, fmt);
  kprintf("kernel panic in %s:%d:\n    ", file, line);
  vkprintf(fmt, ap);
  kprintf("\n");
  va_end(ap);
}

void __attribute__((noreturn)) __bug(const char *file, int line)
{
  printk(KERN_CRIT"kernel BUG at %s:%d!\n", file, line);
  panic("0");
  /* Avoid "noreturn function does return" */
  for (;;);
}

int sprint_symbol(char *buffer, unsigned long address)
{
  char *modname;
  const char *name;
  unsigned long offset, size;
  int len;

  //name = kallsyms_lookup(address, &size, &offset, &modname, buffer);
  name = NULL;
  if (!name)
    return sprintf(buffer, "0x%lx", address);

  if (name != buffer)
    strcpy(buffer, name);
  len = strlen(buffer);
  buffer += len;

  if (modname)
    len += sprintf(buffer, "+%#lx/%#lx [%s]",
        offset, size, modname);
  else
    len += sprintf(buffer, "+%#lx/%#lx", offset, size);

  return len;
}

/* Look up a kernel symbol and print it to the kernel messages. */
void __print_symbol(const char *fmt, unsigned long address)
{
  printk("__print_symbol: %s, 0x%08x\n", fmt, address);
}

/* 
 * Optimised C version of memzero for the ARM.
 */
void __memzero(void *s, __kernel_size_t n)
{
  union { void *vp; unsigned long *ulp; unsigned char *ucp; } u;
  int i;

  u.vp = s;

  for (i = n >> 5; i > 0; i--) {
    *u.ulp++ = 0;
    *u.ulp++ = 0;
    *u.ulp++ = 0;
    *u.ulp++ = 0;
    *u.ulp++ = 0;
    *u.ulp++ = 0;
    *u.ulp++ = 0;
    *u.ulp++ = 0;
  }

  if (n & 1 << 4) {
    *u.ulp++ = 0;
    *u.ulp++ = 0;
    *u.ulp++ = 0;
    *u.ulp++ = 0;
  }

  if (n & 1 << 3) {
    *u.ulp++ = 0;
    *u.ulp++ = 0;
  }

  if (n & 1 << 2)
    *u.ulp++ = 0;

  if (n & 1 << 1) {
    *u.ucp++ = 0;
    *u.ucp++ = 0;
  }

  if (n & 1)
    *u.ucp++ = 0; 
}

char *kstrdup(const char *s, gfp_t gfp)
{
  size_t len;
  char *buf;

  if (!s)
    return NULL;

  len = strlen(s) + 1;
  buf = __kmalloc(len, gfp);
  if (buf)
    memcpy(buf, s, len);
  return buf;
}
EXPORT_SYMBOL(kstrdup);


