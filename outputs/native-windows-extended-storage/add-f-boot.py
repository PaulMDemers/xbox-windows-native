"""Add an opt-in native Windows partition(6) boot path to the isolated branch."""
from pathlib import Path
src=Path('/home/paul/xbox-windows-native/sources/reactos-extended/boot/freeldr/freeldr')
p=src/'bootmgr.c';s=p.read_text();needle='                       "SystemPartition=multi(0)disk(0)rdisk(0)partition(1)",'
assert s.count(needle)==1
s=s.replace(needle,'''#ifdef XBOX_NATIVE_EXTENDED_NT5_BOOT
                       "SystemPartition=multi(0)disk(0)rdisk(0)partition(6)",
#else
'''+needle+'\n#endif');p.write_text(s)
p=src/'rosload.cmake';s=p.read_text();s+='''
option(XBOX_NATIVE_EXTENDED_NT5_BOOT "Boot native Windows from Xbox partition 6" OFF)
if(XBOX_NATIVE_EXTENDED_NT5_BOOT)
    if(NOT SARCH STREQUAL "xbox" OR NOT XBOX_NATIVE_NT5_HANDOFF OR
       XBOX_NATIVE_EXTENDED_READ_PREFLIGHT)
        message(FATAL_ERROR "Extended NT5 boot requires Xbox handoff without read-only stop")
    endif()
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_EXTENDED_NT5_BOOT=1)
endif()
''';p.write_text(s)
