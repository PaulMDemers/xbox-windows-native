#ifndef memory_layout_h
#define memory_layout_h

/* a retail Xbox has 64 MB of RAM */
#define RAMSIZE (64 * 1024*1024)
/* parameters for the Linux kernel have to be here */
#define KERNEL_SETUP   0x90000
#define KERNEL_HDR_SIZE (4 * 1024)
/* command line must not be overwritten, place it in unused setup area */
#define CMD_LINE_LOC (KERNEL_SETUP+0x0800)
/* place GDT at 0xA0000 */
#define GDT_LOC 0xA0000
/* place IDT at 0xB0000 */
#define IDT_LOC 0xB0000
/* the protected mode part of the kernel has to reside at 1 MB in RAM */
#define KERNEL_PM_CODE     0x00100000
/* Linux 6.18 needs more decompressor/init scratch space than older kernels. */
#define KERNEL_PM_CODE_END 0x01000000
#define KERNEL_LOAD_TMP    0x01000000

/*
 * The legacy allocator always manages 16 MB, ignoring its length argument.
 * Its heap starts at 22 MB and ends at 38 MB. Keep the initrd at 40 MB so
 * live USB allocations cannot overwrite it while FATX files are loading.
 */
#define INITRD_START       0x02800000
#ifdef XWN_HD_RESERVATION
#define MAX_INITRD_END     0x03700000
#else
#define MAX_INITRD_END     0x03800000
#endif

#define MAX_KERNEL_SIZE    (KERNEL_PM_CODE_END - KERNEL_PM_CODE)
#define MAX_INITRD_SIZE    (MAX_INITRD_END - INITRD_START)

/* parameters for ReactOS have to be here */
#define FREELDR_LOAD_AREA  (u8 *)0x00001000
#define FREELDR_MAX_SIZE   0x80000

/*
 * Reserve the full 16 MB actually used by t_malloc (1024 x 16 KB blocks).
 */
#define MEMORYMANAGERSTART 0x01600000
#define MEMORYMANAGEREND   0x02600000
#define MEMORYMANAGERSIZE  (MEMORYMANAGEREND - MEMORYMANAGERSTART)

#define STACK_TOP 0x02800000

/* the size of the framebuffer (defaults to 4 MB) */
#ifdef XWN_HD_RESERVATION
#define FB_SIZE 0x00900000
#else
#define FB_SIZE 0x00400000
#endif
/* the start of the framebuffer */
#define FB_START (0xf0000000 | (RAMSIZE - FB_SIZE))

/* let's reserve 4 MB at the top for the framebuffer */
#define RAMSIZE_USE (RAMSIZE - FB_SIZE)

//#define LPCFlashadress 0xFFF00000
#define LPCFlashadress 0xFF000000

#endif /* #ifndef memory_layout_h */
