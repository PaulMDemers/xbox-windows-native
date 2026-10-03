	.file	"xwn-abi-layout.c"
	.text
	.globl	_xwn_ktrap_frame_size
	.section .rdata,"dr"
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
	.globl	_xwn_private_kd_unmap_offset
	.align 4
_xwn_private_kd_unmap_offset:
	.long	76
	.globl	_xwn_private_kd_setup_offset
	.align 4
_xwn_private_kd_setup_offset:
	.long	52
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
	.long	2
	.globl	_xwn_hal_dispatch_version
	.align 4
_xwn_hal_dispatch_version:
	.long	3
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
	.long	84017408
	.ident	"GCC: (RosBE-Unix) 8.4.0"
