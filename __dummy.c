/*
 * =====================================================================================
 *
 *       Filename:  __dummy.cpp
 *
 *    Description:  
 *
 *        Version:  1.0
 *        Created:  10/28/2012 02:53:35 PM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  Chen Yuheng (Chen Yuheng), chyh1990@163.com
 *   Organization:  Tsinghua Unv.
 *
 * =====================================================================================
 */

#include <linux/pm_qos.h>
#include <linux/sched.h>
#include <linux/spinlock.h>
#include <linux/slab.h>
#include <linux/time.h>
#include <linux/fs.h>
#include <linux/device.h>
#include <linux/miscdevice.h>
#include <linux/string.h>
#include <linux/platform_device.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/kexec.h>
#include <linux/irq.h>

#include <linux/uaccess.h>
#include <linux/export.h>

#define DDE_DUMMY_VERBOSE

#ifdef DDE_DUMMY_VERBOSE
#define TRACE dde_kit_printf("[%s] called, not implemented\n", __PRETTY_FUNCTION__)
#else
#define TRACE
#endif

#ifdef DDE_DUMMY_SKIP_VERBOSE
#endif

#define _DDE_WEAK __attribute__((weak))

#include "__dummy.autogen.c"

/* unknown */
/* define in asm in linux */
_DDE_WEAK void mutex_unlock(struct mutex *lock){TRACE;}

_DDE_WEAK unsigned long __copy_from_user(void *to, const void *from, unsigned long n){TRACE;return 0;}

_DDE_WEAK unsigned long __copy_to_user(void *to, const void *from, unsigned long n){TRACE;return 0;}

/* variables */
#ifdef CONFIG_OUTER_CACHE
struct outer_cache_fns outer_cache __read_mostly;
EXPORT_SYMBOL(outer_cache);
#endif

struct device_type part_type = {
         .name           = "partition",
};

note_buf_t* crash_notes;
struct lock_class_key __lockdep_no_validate__;
struct kset *module_kset;

///////////
_DDE_WEAK int autoremove_wake_function(wait_queue_t *wait, unsigned mode, int sync, void *key){TRACE;return 0;}
_DDE_WEAK int blocking_notifier_chain_unregister(struct blocking_notifier_head *nh,
		struct notifier_block *n){TRACE;return 0;}
void module_put(struct module *module){TRACE; return;};
_DDE_WEAK int blocking_notifier_chain_register(struct blocking_notifier_head *nh,
		struct notifier_block *n){TRACE;return 0;}
_DDE_WEAK void finish_wait(wait_queue_head_t *q, wait_queue_t *wait){TRACE;return 0;}
_DDE_WEAK int bitmap_scnlistprintf(char *buf, unsigned int buflen,
	const unsigned long *maskp, int nmaskbits){TRACE;return 0;}
void lockdep_init_map(struct lockdep_map *lock, const char *name,
		      struct lock_class_key *key, int subclass){TRACE;return;}
_DDE_WEAK int sysfs_schedule_callback(struct kobject *kobj, void (*func)(void *),
		void *data, struct module *owner){TRACE;return 0;}
_DDE_WEAK int get_option (char **str, int *pint){TRACE;return 0;}

