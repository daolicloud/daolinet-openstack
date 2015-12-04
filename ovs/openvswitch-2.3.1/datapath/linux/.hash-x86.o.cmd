cmd_/root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/hash-x86.o := gcc -Wp,-MD,/root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/.hash-x86.o.d  -nostdinc -isystem /usr/lib/gcc/x86_64-redhat-linux/4.8.2/include -I/root/163/openvswitch-2.3.1-allinone-icmp/include -I/root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/compat -I/root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/compat/include -I/usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include -Iarch/x86/include/generated  -Iinclude -I/usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/uapi -Iarch/x86/include/generated/uapi -I/usr/src/kernels/3.10.0-123.13.2.el7.x86_64/include/uapi -Iinclude/generated/uapi -include /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/include/linux/kconfig.h -D__KERNEL__ -Wall -Wundef -Wstrict-prototypes -Wno-trigraphs -fno-strict-aliasing -fno-common -Werror-implicit-function-declaration -Wno-format-security -fno-delete-null-pointer-checks -O2 -m64 -mno-sse -mpreferred-stack-boundary=3 -mtune=generic -mno-red-zone -mcmodel=kernel -funit-at-a-time -maccumulate-outgoing-args -DCONFIG_AS_CFI=1 -DCONFIG_AS_CFI_SIGNAL_FRAME=1 -DCONFIG_AS_CFI_SECTIONS=1 -DCONFIG_AS_FXSAVEQ=1 -DCONFIG_AS_AVX=1 -DCONFIG_AS_AVX2=1 -pipe -Wno-sign-compare -fno-asynchronous-unwind-tables -mno-sse -mno-mmx -mno-sse2 -mno-3dnow -mno-avx -Wframe-larger-than=2048 -fstack-protector-strong -Wno-unused-but-set-variable -fno-omit-frame-pointer -fno-optimize-sibling-calls -g -pg -mfentry -DCC_USING_FENTRY -fno-inline-functions-called-once -Wdeclaration-after-statement -Wno-pointer-sign -fno-strict-overflow -fconserve-stack -DCC_HAVE_ASM_GOTO -DVERSION=\"2.3.1\" -I/root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/.. -I/root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/.. -g -include /root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/kcompat.h  -DMODULE  -D"KBUILD_STR(s)=\#s" -D"KBUILD_BASENAME=KBUILD_STR(hash_x86)"  -D"KBUILD_MODNAME=KBUILD_STR(openvswitch)" -c -o /root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/.tmp_hash-x86.o /root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/hash-x86.c

source_/root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/hash-x86.o := /root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/hash-x86.c

deps_/root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/hash-x86.o := \
    $(wildcard include/config/x86.h) \
  /root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/kcompat.h \
  include/generated/uapi/linux/version.h \
  /root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/compat/include/linux/hash.h \
  include/linux/hash.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/uapi/asm/types.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/include/uapi/asm-generic/types.h \
  include/asm-generic/int-ll64.h \
  include/uapi/asm-generic/int-ll64.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/uapi/asm/bitsperlong.h \
  include/asm-generic/bitsperlong.h \
    $(wildcard include/config/64bit.h) \
  include/uapi/asm-generic/bitsperlong.h \
  /root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/compat/include/asm/hash.h \
  /root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/compat/include/linux/compiler.h \
  include/linux/compiler.h \
    $(wildcard include/config/sparse/rcu/pointer.h) \
    $(wildcard include/config/trace/branch/profiling.h) \
    $(wildcard include/config/profile/all/branches.h) \
    $(wildcard include/config/enable/must/check.h) \
    $(wildcard include/config/enable/warn/deprecated.h) \
    $(wildcard include/config/kprobes.h) \
  /root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/compat/include/linux/compiler-gcc.h \
  include/linux/compiler-gcc.h \
    $(wildcard include/config/arch/supports/optimized/inlining.h) \
    $(wildcard include/config/optimize/inlining.h) \
  include/linux/compiler-gcc4.h \
    $(wildcard include/config/arch/use/builtin/bswap.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/processor.h \
    $(wildcard include/config/x86/vsmp.h) \
    $(wildcard include/config/x86/32.h) \
    $(wildcard include/config/smp.h) \
    $(wildcard include/config/x86/64.h) \
    $(wildcard include/config/cc/stackprotector.h) \
    $(wildcard include/config/paravirt.h) \
    $(wildcard include/config/m486.h) \
    $(wildcard include/config/x86/debugctlmsr.h) \
    $(wildcard include/config/xen.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/processor-flags.h \
    $(wildcard include/config/vm86.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/uapi/asm/processor-flags.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/vm86.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/ptrace.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/segment.h \
    $(wildcard include/config/tracing.h) \
    $(wildcard include/config/x86/32/lazy/gs.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/include/uapi/linux/const.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/cache.h \
    $(wildcard include/config/x86/l1/cache/shift.h) \
    $(wildcard include/config/x86/internode/cache/shift.h) \
  include/linux/linkage.h \
  include/linux/stringify.h \
  include/linux/export.h \
    $(wildcard include/config/have/underscore/symbol/prefix.h) \
    $(wildcard include/config/modules.h) \
    $(wildcard include/config/modversions.h) \
    $(wildcard include/config/unused/symbols.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/linkage.h \
    $(wildcard include/config/x86/alignment/16.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/page_types.h \
  /root/163/openvswitch-2.3.1-allinone-icmp/include/linux/types.h \
  /root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/compat/include/linux/types.h \
  include/linux/types.h \
    $(wildcard include/config/uid16.h) \
    $(wildcard include/config/lbdaf.h) \
    $(wildcard include/config/arch/dma/addr/t/64bit.h) \
    $(wildcard include/config/phys/addr/t/64bit.h) \
  include/uapi/linux/types.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/include/uapi/linux/posix_types.h \
  /root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/compat/include/linux/stddef.h \
  include/linux/stddef.h \
  include/uapi/linux/stddef.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/posix_types.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/uapi/asm/posix_types_64.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/include/uapi/asm-generic/posix_types.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/page_64_types.h \
    $(wildcard include/config/physical/start.h) \
    $(wildcard include/config/physical/align.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/uapi/asm/ptrace.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/uapi/asm/ptrace-abi.h \
  include/linux/init.h \
    $(wildcard include/config/broken/rodata.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/paravirt_types.h \
    $(wildcard include/config/x86/local/apic.h) \
    $(wildcard include/config/x86/pae.h) \
    $(wildcard include/config/paravirt/debug.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/desc_defs.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/kmap_types.h \
    $(wildcard include/config/debug/highmem.h) \
  include/asm-generic/kmap_types.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/pgtable_types.h \
    $(wildcard include/config/kmemcheck.h) \
    $(wildcard include/config/compat/vdso.h) \
    $(wildcard include/config/proc/fs.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/pgtable_64_types.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/sparsemem.h \
    $(wildcard include/config/sparsemem.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/spinlock_types.h \
    $(wildcard include/config/paravirt/spinlocks.h) \
    $(wildcard include/config/nr/cpus.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/rwlock.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/asm.h \
  include/asm-generic/ptrace.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/uapi/asm/vm86.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/math_emu.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/sigcontext.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/uapi/asm/sigcontext.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/current.h \
  /root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/compat/include/asm/percpu.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/percpu.h \
    $(wildcard include/config/x86/64/smp.h) \
    $(wildcard include/config/x86/cmpxchg64.h) \
  /root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/compat/include/linux/kernel.h \
  include/linux/kernel.h \
    $(wildcard include/config/preempt/voluntary.h) \
    $(wildcard include/config/debug/atomic/sleep.h) \
    $(wildcard include/config/prove/locking.h) \
    $(wildcard include/config/ring/buffer.h) \
    $(wildcard include/config/ftrace/mcount/record.h) \
  /usr/lib/gcc/x86_64-redhat-linux/4.8.2/include/stdarg.h \
  include/linux/bitops.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/bitops.h \
    $(wildcard include/config/x86/cmov.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/alternative.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/cpufeature.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/required-features.h \
    $(wildcard include/config/x86/minimum/cpu/family.h) \
    $(wildcard include/config/math/emulation.h) \
    $(wildcard include/config/x86/use/3dnow.h) \
    $(wildcard include/config/x86/p6/nop.h) \
    $(wildcard include/config/matom.h) \
  include/asm-generic/bitops/find.h \
    $(wildcard include/config/generic/find/first/bit.h) \
  include/asm-generic/bitops/sched.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/arch_hweight.h \
  include/asm-generic/bitops/const_hweight.h \
  include/asm-generic/bitops/le.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/uapi/asm/byteorder.h \
  include/linux/byteorder/little_endian.h \
  include/uapi/linux/byteorder/little_endian.h \
  include/linux/swab.h \
  include/uapi/linux/swab.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/uapi/asm/swab.h \
  include/linux/byteorder/generic.h \
  include/asm-generic/bitops/ext2-atomic-setbit.h \
  /root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/compat/include/linux/log2.h \
  include/linux/log2.h \
    $(wildcard include/config/arch/has/ilog2/u32.h) \
    $(wildcard include/config/arch/has/ilog2/u64.h) \
  include/linux/typecheck.h \
  include/linux/printk.h \
    $(wildcard include/config/early/printk.h) \
    $(wildcard include/config/printk.h) \
    $(wildcard include/config/dynamic/debug.h) \
  include/linux/kern_levels.h \
  include/linux/dynamic_debug.h \
  include/uapi/linux/kernel.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/include/uapi/linux/sysinfo.h \
  include/asm-generic/percpu.h \
    $(wildcard include/config/debug/preempt.h) \
    $(wildcard include/config/have/setup/per/cpu/area.h) \
  include/linux/threads.h \
    $(wildcard include/config/base/small.h) \
  include/linux/percpu-defs.h \
    $(wildcard include/config/debug/force/weak/per/cpu.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/page.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/page_64.h \
    $(wildcard include/config/debug/virtual.h) \
    $(wildcard include/config/flatmem.h) \
  include/linux/range.h \
  include/asm-generic/memory_model.h \
    $(wildcard include/config/discontigmem.h) \
    $(wildcard include/config/sparsemem/vmemmap.h) \
  include/asm-generic/getorder.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/msr.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/uapi/asm/msr.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/uapi/asm/msr-index.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/include/uapi/linux/ioctl.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/uapi/asm/ioctl.h \
  include/asm-generic/ioctl.h \
  include/uapi/asm-generic/ioctl.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/uapi/asm/errno.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/include/uapi/asm-generic/errno.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/include/uapi/asm-generic/errno-base.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/cpumask.h \
  /root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/compat/include/linux/cpumask.h \
  include/linux/cpumask.h \
    $(wildcard include/config/cpumask/offstack.h) \
    $(wildcard include/config/hotplug/cpu.h) \
    $(wildcard include/config/debug/per/cpu/maps.h) \
    $(wildcard include/config/disable/obsolete/cpumask/functions.h) \
  include/linux/bitmap.h \
  include/linux/string.h \
    $(wildcard include/config/binary/printf.h) \
  include/uapi/linux/string.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/string.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/string_64.h \
  /root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/compat/include/linux/bug.h \
  include/linux/bug.h \
    $(wildcard include/config/generic/bug.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/bug.h \
    $(wildcard include/config/bug.h) \
    $(wildcard include/config/debug/bugverbose.h) \
  include/asm-generic/bug.h \
    $(wildcard include/config/generic/bug/relative/pointers.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/paravirt.h \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/nops.h \
    $(wildcard include/config/mk7.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/special_insns.h \
  include/linux/personality.h \
  include/uapi/linux/personality.h \
  include/linux/cache.h \
    $(wildcard include/config/arch/has/cache/line/size.h) \
  include/linux/math64.h \
    $(wildcard include/config/arch/supports/int128.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/div64.h \
  include/asm-generic/div64.h \
  /root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/compat/include/linux/err.h \
  include/linux/err.h \
  include/linux/irqflags.h \
    $(wildcard include/config/trace/irqflags.h) \
    $(wildcard include/config/irqsoff/tracer.h) \
    $(wildcard include/config/preempt/tracer.h) \
    $(wildcard include/config/trace/irqflags/support.h) \
  /usr/src/kernels/3.10.0-123.13.2.el7.x86_64/arch/x86/include/asm/irqflags.h \
    $(wildcard include/config/debug/lock/alloc.h) \

/root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/hash-x86.o: $(deps_/root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/hash-x86.o)

$(deps_/root/163/openvswitch-2.3.1-allinone-icmp/datapath/linux/hash-x86.o):
