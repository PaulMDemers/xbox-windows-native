##
## PROJECT:     FreeLoader
## LICENSE:     GPL-2.0-or-later (https://spdx.org/licenses/GPL-2.0-or-later)
## PURPOSE:     Build definitions for rosload 2nd stage loader
## COPYRIGHT:   Copyright 2024 Timo Kreuzer <timo.kreuzer@reactos.org>
##

spec2def(rosload.exe rosload.spec)

list(APPEND ROSLOAD_SOURCE
    include/freeldr.h
    bootmgr.c
    custom.c
    linuxboot.c
    miscboot.c
    options.c
    oslist.c
    lib/rtl/libsupp.c
    ${REACTOS_SOURCE_DIR}/ntoskrnl/config/cmboot.c
    ${REACTOS_SOURCE_DIR}/ntoskrnl/ke/config.c
    ntldr/advopts.c
    ntldr/conversion.c
    ntldr/headless.c
    ntldr/inffile.c
    ntldr/ntldropts.c
    ntldr/registry.c
    ntldr/setupldr.c
    ntldr/winldr.c
    ntldr/wlmemory.c
    ntldr/wlregistry.c)

if(ARCH STREQUAL "i386")

    list(APPEND ROSLOAD_SOURCE
        arch/i386/halstub.c
        arch/i386/ntoskrnl.c
        disk/scsiport.c
        ntldr/arch/i386/winldr.c)

    list(APPEND ROSLOAD_ASM_SOURCE
        arch/i386/drvmap.S
        arch/i386/linux.S)

elseif(ARCH STREQUAL "amd64")

    list(APPEND ROSLOAD_SOURCE
        ntldr/arch/amd64/winldr.c)

    list(APPEND ROSLOAD_ASM_SOURCE
        arch/amd64/misc.S
        arch/amd64/linux.S)

elseif(ARCH STREQUAL "arm")

    list(APPEND ROSLOAD_SOURCE
        ntldr/arch/arm/winldr.c)

    list(APPEND ROSLOAD_ASM_SOURCE
        arch/arm/boot.S)

else()
    #TBD
endif()

add_asm_files(rosload_asm ${ROSLOAD_ASM_SOURCE})

add_executable(rosload
    ${ROSLOAD_SOURCE}
    ${rosload_asm}
    ${CMAKE_CURRENT_BINARY_DIR}/rosload.def
)

set_target_properties(rosload
    PROPERTIES
    ENABLE_EXPORTS TRUE
    DEFINE_SYMBOL "")

if(XBOX_NATIVE_IO_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_IO_PREFLIGHT=1)
endif()

set_image_base(rosload 0x10000) # 0x200000
set_subsystem(rosload native)
set_entrypoint(rosload RunLoader)

target_link_libraries(rosload blcmlib blrtl libcntpr)
if(ARCH STREQUAL "i386")
    target_link_libraries(rosload mini_hal)
endif()

add_importlibs(rosload freeldr)

# dynamic analysis switches
if(STACK_PROTECTOR)
    target_link_libraries(rosload gcc_ssp_nt)
endif()

if(RUNTIME_CHECKS)
    target_link_libraries(rosload runtmchk)
endif()

add_dependencies(rosload bugcodes asm xdk)

add_cd_file(TARGET rosload DESTINATION loader NO_CAB FOR bootcd regtest)

if(XBOX_NATIVE_VOLUME_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_VOLUME_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_NT5_HANDOFF)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_NT5_HANDOFF=1)
endif()

if(XBOX_NATIVE_NT5_ENTER)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_NT5_ENTER=1)
endif()

if(XBOX_NATIVE_NT5_AUTORUN)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_NT5_AUTORUN=1)
endif()

if(XBOX_NATIVE_FATX_NT5_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_NT5_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_PAGING_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_PAGING_PREFLIGHT=1)
    target_sources(rosload PRIVATE arch/vgafont.c)
endif()

if(XBOX_NATIVE_FATX_ENTRY_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_ENTRY_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_PHASE0_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_PHASE0_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_HALBASE_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_HALBASE_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_TIMER_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_TIMER_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_CLOCK_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_CLOCK_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_HOOKS_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_HOOKS_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_BIOS_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_BIOS_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_MM_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_MM_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_MI_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_MI_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_MAP_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_MAP_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_SCAN_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_SCAN_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_SIZE_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_SIZE_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_PT_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_PT_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_POOL_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_POOL_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_POOLINIT_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_POOLINIT_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_PFN_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_PFN_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_PFNMAP_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_PFNMAP_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_PFNCOMMIT_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_PFNCOMMIT_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_FREELIST_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_FREELIST_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_SYSPTES_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_SYSPTES_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_PROCESSPAGES_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_PROCESSPAGES_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_PROCESSINIT_PREFLIGHT)
 target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_PROCESSINIT_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_MMCOMPLETE_PREFLIGHT)
 target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_MMCOMPLETE_PREFLIGHT=1)
endif()

if(XBOX_NATIVE_FATX_BOOTVIDEO_PREFLIGHT)
 target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_BOOTVIDEO_PREFLIGHT=1)
endif()
option(XBOX_NATIVE_EXTENDED_READ_PREFLIGHT "Read owned 250GB FATX fixture then halt" OFF)
if(XBOX_NATIVE_EXTENDED_READ_PREFLIGHT)
    if(NOT SARCH STREQUAL "xbox" OR NOT XBOX_NATIVE_IO_PREFLIGHT)
        message(FATAL_ERROR "Extended read preflight requires Xbox IO preflight")
    endif()
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_EXTENDED_READ_PREFLIGHT=1)
endif()

option(XBOX_NATIVE_EXTENDED_NT5_BOOT "Boot native Windows from Xbox partition 6" OFF)
if(XBOX_NATIVE_EXTENDED_NT5_BOOT)
    if(NOT SARCH STREQUAL "xbox" OR NOT XBOX_NATIVE_NT5_HANDOFF OR
       XBOX_NATIVE_EXTENDED_READ_PREFLIGHT)
        message(FATAL_ERROR "Extended NT5 boot requires Xbox handoff without read-only stop")
    endif()
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_EXTENDED_NT5_BOOT=1)
endif()
