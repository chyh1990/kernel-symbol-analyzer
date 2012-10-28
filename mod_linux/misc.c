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

