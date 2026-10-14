##
## PROJECT:     FreeLoader
## LICENSE:     GPL-2.0-or-later (https://spdx.org/licenses/GPL-2.0-or-later)
## PURPOSE:     Build definitions for PC-AT and "compatibles" (NEC PC-98, XBOX)
## COPYRIGHT:   Copyright 2003 Brian Palmer <brianp@sginet.com>
##              Copyright 2011-2014 Amine Khaldi <amine.khaldi@reactos.org>
##              Copyright 2011-2014 Timo Kreuzer <timo.kreuzer@reactos.org>
##              Copyright 2014 Hervé Poussineau <hpoussin@reactos.org>
##              Copyright 2023 Hermès Bélusca-Maïto <hermes.belusca-maito@reactos.org>
##

if(ARCH STREQUAL "i386")
    CreateBootSectorTarget(frldr16
        ${CMAKE_CURRENT_SOURCE_DIR}/arch/realmode/i386.S
        ${CMAKE_CURRENT_BINARY_DIR}/frldr16.bin
        F800)
elseif(ARCH STREQUAL "amd64")
    CreateBootSectorTarget(frldr16
        ${CMAKE_CURRENT_SOURCE_DIR}/arch/realmode/amd64.S
        ${CMAKE_CURRENT_BINARY_DIR}/frldr16.bin
        F800)
endif()


spec2def(freeldr.sys freeldr.spec ADD_IMPORTLIB)

list(APPEND PCATLDR_ARC_SOURCE
    ${FREELDR_ARC_SOURCE}
    arch/drivers/hwide.c)

list(APPEND PCATLDR_BOOTMGR_SOURCE
    ${FREELDR_BOOTMGR_SOURCE}
    linuxboot.c)

list(APPEND PCATLDR_BASE_ASM_SOURCE)

if(ARCH STREQUAL "i386")
    list(APPEND PCATLDR_BASE_ASM_SOURCE
        arch/i386/multiboot.S)

    list(APPEND PCATLDR_COMMON_ASM_SOURCE
        arch/i386/drvmap.S
        arch/i386/entry.S
        arch/i386/int386.S
        arch/i386/irqsup.S
        arch/i386/pnpbios.S
        # arch/i386/i386trap.S
        arch/i386/linux.S)

    list(APPEND PCATLDR_ARC_SOURCE
        # disk/scsiport.c
        lib/fs/pxe.c
        arch/i386/drivemap.c
        arch/i386/hwacpi.c
        arch/i386/hwapm.c
        arch/i386/hwdisk.c
        arch/i386/hwpci.c
        # arch/i386/i386bug.c
        arch/i386/i386idt.c)

    if(SARCH STREQUAL "xbox")
        list(APPEND PCATLDR_ARC_SOURCE
            arch/vidfb.c)
    endif()
    if(SARCH STREQUAL "pc98" OR SARCH STREQUAL "xbox")
        # These machine types require built-in bitmap font
        list(APPEND PCATLDR_ARC_SOURCE
            arch/vgafont.c)
    endif()

    if(SARCH STREQUAL "xbox")
        list(APPEND PCATLDR_ARC_SOURCE
            # FIXME: Abstract things better so we don't need to include /pc/* here
            arch/i386/pc/machpc.c       # machxbox.c depends on it
            arch/i386/pc/pcbeep.c       # machxbox.c depends on it
            arch/i386/pc/pchw.c         # Many files depends on it
            arch/i386/pc/pcmem.c        # hwacpi.c/xboxmem.c depends on it
            arch/i386/xbox/machxbox.c
            arch/i386/xbox/xboxcons.c
            arch/i386/xbox/xboxdisk.c
            arch/i386/xbox/xboxi2c.c
            arch/i386/xbox/xboxmem.c
            arch/i386/xbox/xboxrtc.c
            arch/i386/xbox/xboxvideo.c)
        if(NOT MSVC)
            # Prevent a warning when doing a memcmp with address 0
            set_source_files_properties(arch/i386/xbox/xboxmem.c PROPERTIES COMPILE_OPTIONS "-Wno-nonnull")
        endif()

    elseif(SARCH STREQUAL "pc98")
        list(APPEND PCATLDR_ARC_SOURCE
            arch/i386/pc/pcmem.c        # pc98mem.c depends on it
            arch/i386/pc98/machpc98.c
            arch/i386/pc98/pc98beep.c
            arch/i386/pc98/pc98cons.c
            arch/i386/pc98/pc98disk.c
            arch/i386/pc98/pc98hw.c
            arch/i386/pc98/pc98mem.c
            arch/i386/pc98/pc98rtc.c
            arch/i386/pc98/pc98video.c)
    else()
        list(APPEND PCATLDR_ARC_SOURCE
            arch/i386/pc/machpc.c
            arch/i386/pc/pcbeep.c
            arch/i386/pc/pccons.c
            arch/i386/pc/pcdisk.c
            arch/i386/pc/pchw.c
            arch/i386/pc/pcmem.c
            arch/i386/pc/pcrtc.c
            arch/i386/pc/pcvesa.c
            arch/i386/pc/pcvideo.c)
    endif()

elseif(ARCH STREQUAL "amd64")
    list(APPEND PCATLDR_BASE_ASM_SOURCE
        arch/i386/multiboot.S)

    list(APPEND PCATLDR_COMMON_ASM_SOURCE
        arch/amd64/entry.S
        arch/amd64/int386.S
        arch/amd64/pnpbios.S
        arch/amd64/linux.S)

    list(APPEND PCATLDR_ARC_SOURCE
        lib/fs/pxe.c
        arch/i386/drivemap.c
        arch/i386/hwacpi.c
        arch/i386/hwapm.c
        arch/i386/hwdisk.c
        arch/i386/hwpci.c
        # arch/i386/i386bug.c
        arch/i386/pc/machpc.c
        arch/i386/pc/pcbeep.c
        arch/i386/pc/pccons.c
        arch/i386/pc/pcdisk.c
        arch/i386/pc/pchw.c
        arch/i386/pc/pcmem.c
        arch/i386/pc/pcrtc.c
        arch/i386/pc/pcvesa.c
        arch/i386/pc/pcvideo.c)

elseif(ARCH STREQUAL "arm")
    list(APPEND PCATLDR_COMMON_ASM_SOURCE
        arch/arm/boot.S)

    list(APPEND PCATLDR_ARC_SOURCE
        arch/arm/entry.c
        arch/arm/macharm.c)
else()
    #TBD
endif()

add_asm_files(freeldr_common_asm ${FREELDR_COMMON_ASM_SOURCE} ${PCATLDR_COMMON_ASM_SOURCE})

add_library(freeldr_common
    ${freeldr_common_asm}
    ${PCATLDR_ARC_SOURCE}
    ${FREELDR_BOOTLIB_SOURCE}
    ${PCATLDR_BOOTMGR_SOURCE}
)
target_compile_definitions(freeldr_common PRIVATE _FRLDRLIB_)

if(MSVC AND CMAKE_C_COMPILER_ID STREQUAL "Clang")
    # We need to reduce the binary size
    target_compile_options(freeldr_common PRIVATE "/Os")
endif()
if(CMAKE_C_COMPILER_ID STREQUAL "GNU" OR CMAKE_C_COMPILER_ID STREQUAL "Clang")
    # Prevent using SSE (no support in freeldr)
    target_compile_options(freeldr_common PUBLIC -mno-sse)
endif()

set(PCH_SOURCE
    ${PCATLDR_ARC_SOURCE}
    ${FREELDR_BOOTLIB_SOURCE}
    ${PCATLDR_BOOTMGR_SOURCE}
)

add_pch(freeldr_common include/freeldr.h PCH_SOURCE)
add_dependencies(freeldr_common bugcodes asm xdk)

## GCC builds need this extra thing for some reason...
if(ARCH STREQUAL "i386" AND NOT MSVC)
    target_link_libraries(freeldr_common mini_hal)
endif()

add_asm_files(freeldr_base_asm ${PCATLDR_BASE_ASM_SOURCE})

list(APPEND PCATLDR_BASE_SOURCE
    ${freeldr_base_asm}
    ${FREELDR_BASE_SOURCE})

add_executable(freeldr_pe ${PCATLDR_BASE_SOURCE})

set_target_properties(freeldr_pe
    PROPERTIES
    ENABLE_EXPORTS TRUE
    DEFINE_SYMBOL "")

if(MSVC)
    if(ARCH STREQUAL "arm")
        target_link_options(freeldr_pe PRIVATE /ignore:4078 /ignore:4254 /DRIVER)
    else()
        target_link_options(freeldr_pe PRIVATE /ignore:4078 /ignore:4254 /DYNAMICBASE:NO /FIXED /FILEALIGN:512 /ALIGN:512)
        add_linker_script(freeldr_pe freeldr_i386.msvc.lds)
    endif()
    # We don't need hotpatching
    remove_target_compile_option(freeldr_pe "/hotpatch")
    remove_target_compile_option(freeldr_common "/hotpatch")
else()
    target_link_options(freeldr_pe PRIVATE -Wl,--exclude-all-symbols,--file-alignment,0x200,--section-alignment,0x200)
    add_linker_script(freeldr_pe freeldr_gcc.lds)
    # Strip everything, including rossym data
    add_custom_command(TARGET freeldr_pe
                    POST_BUILD
                    COMMAND ${CMAKE_STRIP} --remove-section=.rossym $<TARGET_FILE:freeldr_pe>
                    COMMAND ${CMAKE_STRIP} --strip-all $<TARGET_FILE:freeldr_pe>)
endif()

option(XBOX_NATIVE_PREFLIGHT "Stop Xbox loader after platform and disk diagnostics" OFF)
if(XBOX_NATIVE_PREFLIGHT)
    if(NOT ARCH STREQUAL "i386" OR NOT SARCH STREQUAL "xbox")
        message(FATAL_ERROR "XBOX_NATIVE_PREFLIGHT requires ARCH=i386 and SARCH=xbox")
    endif()
    target_compile_definitions(freeldr_pe PRIVATE XBOX_NATIVE_PREFLIGHT=1)
endif()

option(XBOX_NATIVE_IO_PREFLIGHT "Verify Xbox CD reads and rosload handoff, then halt" OFF)
if(XBOX_NATIVE_IO_PREFLIGHT)
    if(NOT ARCH STREQUAL "i386" OR NOT SARCH STREQUAL "xbox" OR XBOX_NATIVE_PREFLIGHT)
        message(FATAL_ERROR "IO preflight requires i386/xbox and the first preflight OFF")
    endif()
    target_compile_definitions(freeldr_pe PRIVATE XBOX_NATIVE_IO_PREFLIGHT=1)
endif()

set_image_base(freeldr_pe 0x10000)
set_subsystem(freeldr_pe native)
set_entrypoint(freeldr_pe RealEntryPoint)

target_link_libraries(freeldr_pe freeldr_common cportlib libcntpr blrtl)
if(ARCH STREQUAL "i386")
    target_link_libraries(freeldr_pe mini_hal)
endif()

# dynamic analysis switches
if(STACK_PROTECTOR)
    target_link_libraries(freeldr_pe gcc_ssp_nt)
endif()

if(RUNTIME_CHECKS)
    target_link_libraries(freeldr_pe runtmchk)
    target_link_options(freeldr_pe PRIVATE "/MERGE:.rtc=.text")
endif()

add_dependencies(freeldr_pe asm)

if(SARCH STREQUAL "pc98")
    file(MAKE_DIRECTORY ${REACTOS_BINARY_DIR}/PC98)
    add_custom_target(pc98bootfdd
        COMMAND native-fatten ${REACTOS_BINARY_DIR}/PC98/ReactOS-98.IMG -format 2880 ROS98BOOT -boot ${CMAKE_BINARY_DIR}/boot/freeldr/bootsect/pc98/fat12fdd.bin -add ${CMAKE_CURRENT_BINARY_DIR}/freeldr.sys FREELDR.SYS -add ${CMAKE_SOURCE_DIR}/boot/bootdata/floppy_pc98.ini FREELDR.INI
        DEPENDS native-fatten fat12pc98 freeldr
        VERBATIM)
endif()

if(NOT ARCH STREQUAL "arm")
    concatenate_files(
        ${CMAKE_CURRENT_BINARY_DIR}/freeldr.sys
        ${CMAKE_CURRENT_BINARY_DIR}/frldr16.bin
        ${CMAKE_CURRENT_BINARY_DIR}/$<TARGET_FILE_NAME:freeldr_pe>)
    add_custom_target(freeldr ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/freeldr.sys)
else()
    add_custom_target(freeldr ALL DEPENDS freeldr_pe)
endif()

add_cd_file(TARGET freeldr FILE ${CMAKE_CURRENT_BINARY_DIR}/freeldr.sys DESTINATION loader NO_CAB FOR bootcd regtest)

option(XBOX_NATIVE_NT5_ENTER "Permit debugger-gated experimental Windows kernel entry" OFF)
if(XBOX_NATIVE_NT5_ENTER AND NOT XBOX_NATIVE_NT5_HANDOFF)
    message(FATAL_ERROR "NT5 entry requires the handoff diagnostic")
endif()

option(XBOX_NATIVE_NT5_AUTORUN "Enter experimental NT5 kernel without a host debugger gate" OFF)
if(XBOX_NATIVE_NT5_AUTORUN AND NOT XBOX_NATIVE_NT5_ENTER)
    message(FATAL_ERROR "NT5 autorun requires the explicit kernel-entry option")
endif()

option(XBOX_NATIVE_NT5_HANDOFF "Load installed NT5 files and halt before kernel entry" OFF)
if(XBOX_NATIVE_NT5_HANDOFF AND (NOT XBOX_NATIVE_IO_PREFLIGHT OR XBOX_NATIVE_VOLUME_PREFLIGHT))
    message(FATAL_ERROR "NT5 handoff requires I/O preflight, excludes volume-only preflight")
endif()

option(XBOX_NATIVE_VOLUME_PREFLIGHT "Read and verify the private installed Windows NTFS fixture, then halt" OFF)
if(XBOX_NATIVE_VOLUME_PREFLIGHT AND NOT XBOX_NATIVE_IO_PREFLIGHT)
    message(FATAL_ERROR "Volume preflight requires the IO preflight")
endif()

if(XBOX_NATIVE_NT5_HANDOFF)
    target_compile_definitions(freeldr_common PRIVATE XBOX_NATIVE_NT5_HANDOFF=1)
endif()

# Isolated physical FATX diagnostic; never combine with native kernel entry.
option(XBOX_NATIVE_FATX_IO_PREFLIGHT "Run halt-only I/O probe from E Applications XWNLoader" OFF)
if(XBOX_NATIVE_FATX_IO_PREFLIGHT)
    if(NOT SARCH STREQUAL "xbox" OR NOT XBOX_NATIVE_IO_PREFLIGHT OR
       XBOX_NATIVE_PREFLIGHT OR XBOX_NATIVE_VOLUME_PREFLIGHT OR
       XBOX_NATIVE_NT5_HANDOFF OR XBOX_NATIVE_NT5_ENTER OR XBOX_NATIVE_NT5_AUTORUN)
        message(FATAL_ERROR "FATX I/O preflight requires Xbox I/O-only mode with every kernel-entry option OFF")
    endif()
    target_compile_definitions(freeldr_pe PRIVATE XBOX_NATIVE_FATX_IO_PREFLIGHT=1)
endif()

# Load Windows files from the isolated FATX app, stopping before paging or entry.
option(XBOX_NATIVE_FATX_NT5_PREFLIGHT "Load NT5 files from FATX and halt visibly before paging" OFF)
if(XBOX_NATIVE_FATX_NT5_PREFLIGHT)
    if(NOT ARCH STREQUAL "i386" OR NOT SARCH STREQUAL "xbox" OR
       NOT XBOX_NATIVE_IO_PREFLIGHT OR NOT XBOX_NATIVE_NT5_HANDOFF OR
       XBOX_NATIVE_PREFLIGHT OR XBOX_NATIVE_VOLUME_PREFLIGHT OR
       XBOX_NATIVE_FATX_IO_PREFLIGHT OR XBOX_NATIVE_NT5_ENTER OR XBOX_NATIVE_NT5_AUTORUN)
        message(FATAL_ERROR "FATX NT5 preflight requires i386/xbox I/O and handoff, with other probes and kernel entry OFF")
    endif()
    target_compile_definitions(freeldr_pe PRIVATE XBOX_NATIVE_FATX_NT5_PREFLIGHT=1)
endif()

option(XBOX_NATIVE_FATX_PAGING_PREFLIGHT "Switch NT5 page tables and halt with a framebuffer result" OFF)
if(XBOX_NATIVE_FATX_PAGING_PREFLIGHT AND
   (NOT XBOX_NATIVE_FATX_NT5_PREFLIGHT OR XBOX_NATIVE_NT5_ENTER OR XBOX_NATIVE_NT5_AUTORUN))
    message(FATAL_ERROR "FATX paging probe requires FATX NT5 preflight with kernel entry OFF")
endif()

option(XBOX_NATIVE_FATX_ENTRY_PREFLIGHT "Enter NT5 only to an armed first-HAL halt" OFF)
if(XBOX_NATIVE_FATX_ENTRY_PREFLIGHT AND
   (NOT XBOX_NATIVE_FATX_PAGING_PREFLIGHT OR XBOX_NATIVE_NT5_ENTER OR XBOX_NATIVE_NT5_AUTORUN))
    message(FATAL_ERROR "FATX entry probe requires paging diagnostic and forbids general entry/autorun")
endif()

option(XBOX_NATIVE_FATX_PHASE0_PREFLIGHT "Continue only to HAL phase-0 entrance" OFF)
if(XBOX_NATIVE_FATX_PHASE0_PREFLIGHT AND NOT XBOX_NATIVE_FATX_ENTRY_PREFLIGHT)
    message(FATAL_ERROR "Phase-0 probe requires entry preflight")
endif()

option(XBOX_NATIVE_FATX_HALBASE_PREFLIGHT "Stop after base HAL setup before timers" OFF)
if(XBOX_NATIVE_FATX_HALBASE_PREFLIGHT AND NOT XBOX_NATIVE_FATX_PHASE0_PREFLIGHT)
    message(FATAL_ERROR "HAL-base probe requires phase-0 preflight")
endif()

option(XBOX_NATIVE_FATX_TIMER_PREFLIGHT "Stop after RTC stall calibration" OFF)
if(XBOX_NATIVE_FATX_TIMER_PREFLIGHT AND NOT XBOX_NATIVE_FATX_HALBASE_PREFLIGHT)
    message(FATAL_ERROR "Timer probe requires HAL-base preflight")
endif()

option(XBOX_NATIVE_FATX_CLOCK_PREFLIGHT "Stop after clock setup before storage" OFF)
if(XBOX_NATIVE_FATX_CLOCK_PREFLIGHT AND NOT XBOX_NATIVE_FATX_TIMER_PREFLIGHT)
    message(FATAL_ERROR "Clock probe requires timer preflight")
endif()

option(XBOX_NATIVE_FATX_HOOKS_PREFLIGHT "Stop after partition hook registration before BIOS allocation" OFF)
if(XBOX_NATIVE_FATX_HOOKS_PREFLIGHT AND NOT XBOX_NATIVE_FATX_CLOCK_PREFLIGHT)
    message(FATAL_ERROR "Hooks probe requires clock preflight")
endif()

option(XBOX_NATIVE_FATX_BIOS_PREFLIGHT "Stop after BIOS phase-0 allocation before HAL return" OFF)
if(XBOX_NATIVE_FATX_BIOS_PREFLIGHT AND NOT XBOX_NATIVE_FATX_HOOKS_PREFLIGHT)
    message(FATAL_ERROR "BIOS probe requires hooks preflight")
endif()

option(XBOX_NATIVE_FATX_MM_PREFLIGHT "Return HAL phase 0 and halt at NT5 memory-manager entry" OFF)
if(XBOX_NATIVE_FATX_MM_PREFLIGHT AND NOT XBOX_NATIVE_FATX_BIOS_PREFLIGHT)
    message(FATAL_ERROR "MM probe requires BIOS preflight")
endif()

option(XBOX_NATIVE_FATX_MI_PREFLIGHT "Run MM prefix and halt before machine-dependent initialization" OFF)
if(XBOX_NATIVE_FATX_MI_PREFLIGHT AND NOT XBOX_NATIVE_FATX_MM_PREFLIGHT)
    message(FATAL_ERROR "MI probe requires MM preflight")
endif()

option(XBOX_NATIVE_FATX_MAP_PREFLIGHT "Halt in high HAL after native low-PDE clearing" OFF)
if(XBOX_NATIVE_FATX_MAP_PREFLIGHT AND NOT XBOX_NATIVE_FATX_MI_PREFLIGHT)
    message(FATAL_ERROR "MAP probe requires MI preflight")
endif()

option(XBOX_NATIVE_FATX_SCAN_PREFLIGHT "Halt after native RAM scan before allocation" OFF)
if(XBOX_NATIVE_FATX_SCAN_PREFLIGHT AND NOT XBOX_NATIVE_FATX_MAP_PREFLIGHT)
    message(FATAL_ERROR "SCAN probe requires MAP preflight")
endif()

option(XBOX_NATIVE_FATX_SIZE_PREFLIGHT "Halt after sizing before MM allocation" OFF)
if(XBOX_NATIVE_FATX_SIZE_PREFLIGHT AND NOT XBOX_NATIVE_FATX_SCAN_PREFLIGHT)
    message(FATAL_ERROR "SIZE probe requires SCAN preflight")
endif()

option(XBOX_NATIVE_FATX_PT_PREFLIGHT "Halt after first page-table allocation" OFF)
if(XBOX_NATIVE_FATX_PT_PREFLIGHT AND NOT XBOX_NATIVE_FATX_SIZE_PREFLIGHT)
    message(FATAL_ERROR "PT probe requires SIZE preflight")
endif()

option(XBOX_NATIVE_FATX_POOL_PREFLIGHT "Halt after initial nonpaged-pool mappings" OFF)
if(XBOX_NATIVE_FATX_POOL_PREFLIGHT AND NOT XBOX_NATIVE_FATX_PT_PREFLIGHT)
    message(FATAL_ERROR "POOL probe requires PT preflight")
endif()

option(XBOX_NATIVE_FATX_POOLINIT_PREFLIGHT "Halt after native nonpaged-pool initialization" OFF)
if(XBOX_NATIVE_FATX_POOLINIT_PREFLIGHT AND NOT XBOX_NATIVE_FATX_POOL_PREFLIGHT)
    message(FATAL_ERROR "POOLINIT probe requires POOL preflight")
endif()

option(XBOX_NATIVE_FATX_PFN_PREFLIGHT "Halt after native PFN backing allocation" OFF)
if(XBOX_NATIVE_FATX_PFN_PREFLIGHT AND NOT XBOX_NATIVE_FATX_POOLINIT_PREFLIGHT)
    message(FATAL_ERROR "PFN probe requires POOLINIT preflight")
endif()

option(XBOX_NATIVE_FATX_PFNMAP_PREFLIGHT "Halt after mapped PFN initialization" OFF)
if(XBOX_NATIVE_FATX_PFNMAP_PREFLIGHT AND NOT XBOX_NATIVE_FATX_PFN_PREFLIGHT)
    message(FATAL_ERROR "PFNMAP probe requires PFN preflight")
endif()

option(XBOX_NATIVE_FATX_PFNCOMMIT_PREFLIGHT "Reconcile descriptor accounting then halt before free lists" OFF)
if(XBOX_NATIVE_FATX_PFNCOMMIT_PREFLIGHT AND NOT XBOX_NATIVE_FATX_PFNMAP_PREFLIGHT)
    message(FATAL_ERROR "PFNCOMMIT probe requires PFNMAP preflight")
endif()

option(XBOX_NATIVE_FATX_FREELIST_PREFLIGHT "Halt after native free-page list construction" OFF)
if(XBOX_NATIVE_FATX_FREELIST_PREFLIGHT AND NOT XBOX_NATIVE_FATX_PFNCOMMIT_PREFLIGHT)
    message(FATAL_ERROR "FREELIST probe requires PFNCOMMIT preflight")
endif()

option(XBOX_NATIVE_FATX_SYSPTES_PREFLIGHT "Halt after system PTE initialization" OFF)
if(XBOX_NATIVE_FATX_SYSPTES_PREFLIGHT AND NOT XBOX_NATIVE_FATX_FREELIST_PREFLIGHT)
    message(FATAL_ERROR "SYSPTES probe requires FREELIST preflight")
endif()

option(XBOX_NATIVE_FATX_PROCESSPAGES_PREFLIGHT "Halt after first process pages are zeroed" OFF)
if(XBOX_NATIVE_FATX_PROCESSPAGES_PREFLIGHT AND NOT XBOX_NATIVE_FATX_SYSPTES_PREFLIGHT)
    message(FATAL_ERROR "PROCESSPAGES probe requires SYSPTES preflight")
endif()

option(XBOX_NATIVE_FATX_PROCESSINIT_PREFLIGHT "Halt after initial process address-space initialization" OFF)
if(XBOX_NATIVE_FATX_PROCESSINIT_PREFLIGHT AND NOT XBOX_NATIVE_FATX_PROCESSPAGES_PREFLIGHT)
 message(FATAL_ERROR "PROCESSINIT probe requires PROCESSPAGES preflight")
endif()

option(XBOX_NATIVE_FATX_MMCOMPLETE_PREFLIGHT "Halt after complete MM phase zero" OFF)
if(XBOX_NATIVE_FATX_MMCOMPLETE_PREFLIGHT AND NOT XBOX_NATIVE_FATX_PROCESSINIT_PREFLIGHT)
 message(FATAL_ERROR "MMCOMPLETE probe requires PROCESSINIT preflight")
endif()

option(XBOX_NATIVE_FATX_BOOTVIDEO_PREFLIGHT "Halt after native boot video initialization" OFF)
if(XBOX_NATIVE_FATX_BOOTVIDEO_PREFLIGHT AND NOT XBOX_NATIVE_FATX_MMCOMPLETE_PREFLIGHT)
 message(FATAL_ERROR "BOOTVIDEO probe requires MMCOMPLETE preflight")
endif()

option(XBOX_NATIVE_FATX_F_BOOT "Load the isolated E XWNFBoot launcher for native F Windows" OFF)
if(XBOX_NATIVE_FATX_F_BOOT)
    if(NOT SARCH STREQUAL "xbox" OR NOT XBOX_NATIVE_IO_PREFLIGHT OR
       NOT XBOX_NATIVE_EXTENDED_NT5_BOOT OR NOT XBOX_NATIVE_NT5_HANDOFF OR
       NOT XBOX_NATIVE_NT5_ENTER OR NOT XBOX_NATIVE_NT5_AUTORUN OR
       XBOX_NATIVE_FATX_IO_PREFLIGHT OR XBOX_NATIVE_FATX_NT5_PREFLIGHT)
        message(FATAL_ERROR "FATX F boot requires ordinary Xbox partition-6 native autorun")
    endif()
    target_compile_definitions(freeldr_pe PRIVATE XBOX_NATIVE_FATX_F_BOOT=1)
    target_compile_definitions(freeldr_common PRIVATE XBOX_NATIVE_FATX_F_BOOT=1)
endif()
