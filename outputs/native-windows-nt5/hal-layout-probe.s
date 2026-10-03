	.file	"xwn-abi-layout.c"
	.text
	.globl	_xwn_trap_exception_list_offset
	.section .rdata,"dr"
	.align 4
_xwn_trap_exception_list_offset:
	.long	76
	.globl	_xwn_trap_eflags_offset
	.align 4
_xwn_trap_eflags_offset:
	.long	112
	.globl	_xwn_trap_eip_offset
	.align 4
_xwn_trap_eip_offset:
	.long	104
	.globl	_xwn_thread_header_debug_active_offset
	.align 4
_xwn_thread_header_debug_active_offset:
	.long	3
	.globl	_xwn_thread_size
	.align 4
_xwn_thread_size:
	.long	440
	.globl	_xwn_prcb_size
	.align 4
_xwn_prcb_size:
	.long	3796
	.globl	_xwn_ktrap_frame_size
	.align 4
_xwn_ktrap_frame_size:
	.long	140
	.globl	_xwn_fast_mutex_size
	.align 4
_xwn_fast_mutex_size:
	.long	32
	.globl	_xwn_dispatch_dma_adapter_offset
	.align 4
_xwn_dispatch_dma_adapter_offset:
	.long	60
	.globl	_xwn_dispatch_size
	.align 4
_xwn_dispatch_size:
	.long	68
	.globl	_xwn_private_size
	.align 4
_xwn_private_size:
	.long	48
	.globl	_xwn_prcb_current_thread_offset
	.align 4
_xwn_prcb_current_thread_offset:
	.long	4
	.globl	_xwn_prcb_major_version_offset
	.align 4
_xwn_prcb_major_version_offset:
	.long	2
	.globl	_xwn_prcb_build_type_offset
	.align 4
_xwn_prcb_build_type_offset:
	.long	18
	.globl	_xwn_pcr_prcb_offset
	.align 4
_xwn_pcr_prcb_offset:
	.long	32
	.globl	_xwn_prcb_major_version
	.align 4
_xwn_prcb_major_version:
	.long	1
	.globl	_xwn_hal_private_dispatch_version
	.align 4
_xwn_hal_private_dispatch_version:
	.long	1
	.globl	_xwn_hal_dispatch_version
	.align 4
_xwn_hal_dispatch_version:
	.long	2
	.globl	_xwn_hal_build_type
	.align 4
_xwn_hal_build_type:
	.long	2
	.globl	_xwn_dbg
	.align 4
_xwn_dbg:
	.space 4
	.globl	_xwn_ntddi
	.align 4
_xwn_ntddi:
	.long	83886080
	.ident	"GCC: (RosBE-Unix) 8.4.0"
