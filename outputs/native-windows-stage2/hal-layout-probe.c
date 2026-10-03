#include <hal.h>
#undef KdSetupPciDeviceForDebugging
#undef KdUnmapVirtualAddress
#undef HalGetDmaAdapter
const ULONG xwn_ntddi = NTDDI_VERSION;
const ULONG xwn_dbg = DBG;
const ULONG xwn_hal_build_type = HAL_BUILD_TYPE;
const ULONG xwn_hal_dispatch_version = HAL_DISPATCH_VERSION;
const ULONG xwn_hal_private_dispatch_version = HAL_PRIVATE_DISPATCH_VERSION;
const ULONG xwn_prcb_major_version = PRCB_MAJOR_VERSION;
const ULONG xwn_pcr_prcb_offset = FIELD_OFFSET(KPCR, Prcb);
const ULONG xwn_prcb_build_type_offset = FIELD_OFFSET(KPRCB, BuildType);
const ULONG xwn_prcb_major_version_offset = FIELD_OFFSET(KPRCB, MajorVersion);
const ULONG xwn_prcb_current_thread_offset = FIELD_OFFSET(KPRCB, CurrentThread);
const ULONG xwn_private_kd_setup_offset = FIELD_OFFSET(HAL_PRIVATE_DISPATCH, KdSetupPciDeviceForDebugging);
const ULONG xwn_private_kd_unmap_offset = FIELD_OFFSET(HAL_PRIVATE_DISPATCH, KdUnmapVirtualAddress);
const ULONG xwn_dispatch_dma_adapter_offset = FIELD_OFFSET(HAL_DISPATCH, HalGetDmaAdapter);
const ULONG xwn_fast_mutex_size = sizeof(FAST_MUTEX);
const ULONG xwn_ktrap_frame_size = sizeof(KTRAP_FRAME);
