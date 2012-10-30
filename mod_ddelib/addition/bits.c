/*
 * =====================================================================================
 *
 *       Filename:  bits.c
 *
 *    Description:  
 *
 *        Version:  1.0
 *        Created:  10/30/2012 11:06:38 AM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  Chen Yuheng (Chen Yuheng), chyh1990@163.com
 *   Organization:  Tsinghua Unv.
 *
 * =====================================================================================
 */

#include <linux/bitops.h>

void __attribute__((weak)) _set_bit(int bit, volatile unsigned long *p)
{
        unsigned long mask = 1UL << (bit & 31);
        p += bit >> 5;
        *p |= mask;
}

void __attribute__((weak)) _clear_bit(int bit, volatile unsigned long *p)
{
        unsigned long mask = 1UL << (bit & 31);
        p += bit >> 5;
        *p &= ~mask;
}
