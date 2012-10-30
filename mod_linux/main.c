/*
 * =====================================================================================
 *
 *       Filename:  main.c
 *
 *    Description:  
 *
 *        Version:  1.0
 *        Created:  10/29/2012 01:58:06 PM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  Chen Yuheng (Chen Yuheng), chyh1990@163.com
 *   Organization:  Tsinghua Unv.
 *
 * =====================================================================================
 */

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>

#ifdef DEBUG
#define _TODO_() printk(KERN_ALERT "TODO %s\n", __func__)
#else 
#define _TODO_() 
#endif

/* Provided by the linker */
extern const struct kernel_symbol __start___ksymtab[];
extern const struct kernel_symbol __stop___ksymtab[];
extern const struct kernel_symbol __start___ksymtab_gpl[];
extern const struct kernel_symbol __stop___ksymtab_gpl[];
extern const struct kernel_symbol __start___ksymtab_gpl_future[];
extern const struct kernel_symbol __stop___ksymtab_gpl_future[];
extern const struct kernel_symbol __start___ksymtab_gpl_future[];
extern const struct kernel_symbol __stop___ksymtab_gpl_future[];
extern const unsigned long __start___kcrctab[];
extern const unsigned long __start___kcrctab_gpl[];
extern const unsigned long __start___kcrctab_gpl_future[];
#ifdef CONFIG_UNUSED_SYMBOLS
extern const struct kernel_symbol __start___ksymtab_unused[];
extern const struct kernel_symbol __stop___ksymtab_unused[];
extern const struct kernel_symbol __start___ksymtab_unused_gpl[];
extern const struct kernel_symbol __stop___ksymtab_unused_gpl[];
extern const unsigned long __start___kcrctab_unused[];
extern const unsigned long __start___kcrctab_unused_gpl[];
#endif



extern initcall_t __initcall_start[], __initcall_end[];

static void do_initcalls()
{
  int i;
  int cnt = __initcall_end - __initcall_start;
  pr_debug("do_initcalls() %08x %08x %d calls, begin...\n", __initcall_start, __initcall_end,cnt);
  for(i=0;i < cnt; i++){
    pr_debug("  calling 0x%08x\n", __initcall_start[i]);
    __initcall_start[i]();
  }
  pr_debug("do_initcalls() end!\n");
}

/*
int request_module(const char *fmt, ...)
{
  return -EINVAL;
}*/

static void loadable_module_init()
{
  int i;
  int cnt = __stop___ksymtab - __start___ksymtab ;
  for(i=0;i<cnt;i++){
    pr_debug("%d\t%08x\t%s\n", i, __start___ksymtab[i].value,
      __start___ksymtab[i].name);
  }
}

void dde_kit_subsys_linux_init(void)
{
  /* invoked in vfs_cache_init in Linux */
  chrdev_init();
  driver_init(); 

  do_initcalls();
}

