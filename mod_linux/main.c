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

void dde_kit_subsys_linux_init(void)
{
  /* invoked in vfs_cache_init in Linux */
  chrdev_init();
  driver_init(); 
}
