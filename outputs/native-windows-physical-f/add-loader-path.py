from pathlib import Path
s=Path('/home/paul/xbox-windows-native/sources/reactos-extended/boot/freeldr/freeldr')
p=s/'freeldr.c';t=p.read_text();needle='#if defined(XBOX_NATIVE_FATX_IO_PREFLIGHT) || defined(XBOX_NATIVE_FATX_NT5_PREFLIGHT)';assert t.count(needle)==1
t=t.replace(needle,'''#if defined(XBOX_NATIVE_FATX_F_BOOT)
    /* Separate E launcher; native Windows root remains partition 6. */
    if (strcmp(FrLdrBootPath, "multi(0)disk(0)rdisk(0)partition(1)") != 0 ||
        !NT_SUCCESS(RtlStringCbCatA(FrLdrBootPath, sizeof(FrLdrBootPath),
                                   "\\\\Applications\\\\XWNFBoot")))
        XwnStop("XWNFAIL: unexpected FATX F-boot launcher device");
#elif defined(XBOX_NATIVE_FATX_IO_PREFLIGHT) || defined(XBOX_NATIVE_FATX_NT5_PREFLIGHT)''');p.write_text(t)
p=s/'pcat.cmake';t=p.read_text();t+='''
option(XBOX_NATIVE_FATX_F_BOOT "Load the isolated E XWNFBoot launcher for native F Windows" OFF)
if(XBOX_NATIVE_FATX_F_BOOT)
    if(NOT SARCH STREQUAL "xbox" OR NOT XBOX_NATIVE_IO_PREFLIGHT OR
       NOT XBOX_NATIVE_EXTENDED_NT5_BOOT OR NOT XBOX_NATIVE_NT5_HANDOFF OR
       NOT XBOX_NATIVE_NT5_ENTER OR NOT XBOX_NATIVE_NT5_AUTORUN OR
       XBOX_NATIVE_FATX_IO_PREFLIGHT OR XBOX_NATIVE_FATX_NT5_PREFLIGHT)
        message(FATAL_ERROR "FATX F boot requires ordinary Xbox partition-6 native autorun")
    endif()
    target_compile_definitions(freeldr_pe PRIVATE XBOX_NATIVE_FATX_F_BOOT=1)
endif()
''';p.write_text(t)
