/*
 * =====================================================================================
 *
 *       Filename:  slab.c
 *
 *    Description:  
 *
 *        Version:  1.0
 *        Created:  10/30/2012 11:16:54 AM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  Chen Yuheng (Chen Yuheng), chyh1990@163.com
 *   Organization:  Tsinghua Unv.
 *
 * =====================================================================================
 */
#include <linux/slab.h>

#include <dde_kit/memory.h>

void *__kmalloc(size_t size, gfp_t flags)
{
  return dde_kit_simple_malloc(size);
}

