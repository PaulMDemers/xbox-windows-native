"""Apply the opt-in emulator-only high-LBA read probe after patch 0063."""
from pathlib import Path
src=Path('/home/paul/xbox-windows-native/sources/reactos-extended/boot/freeldr/freeldr')
s=(src/'include/xwnprobe.h').read_text()
s=s[s.index('static BOOLEAN XwnVerifyFile'):]
s=s.replace('XwnVerifyFile','XwnVerifyExtendedFile').replace('131075','4097')
s=s.replace('RtlStringCbPrintfA(Path, sizeof(Path), "%s\\\\probe.bin", FrLdrGetBootPath());',
'''RtlStringCbCopyA(Path, sizeof(Path), "multi(0)disk(0)rdisk(0)partition(6)\\\\xwn-high.bin");''')
assert 'FrLdrGetBootPath' not in s
s='''/* SPDX-License-Identifier: GPL-2.0-or-later */
#pragma once
/* Opt-in owned-emulator fixture test. No writes and no kernel entry. */
'''+s+'''
static VOID XwnExtendedReadPreflight(VOID)
{
    if (!XwnVerifyExtendedFile()) XwnStop("XWNFAIL: high-LBA F file");
    XwnStop("XWNF90: F high-LBA file/size/seek/EOF verified. Windows NOT entered.");
}
'''
(src/'include/xwnextended.h').write_text(s)
p=src/'bootmgr.c';s=p.read_text();s=s.replace('#include <xwnprobe.h>','#include <xwnprobe.h>\n#ifdef XBOX_NATIVE_EXTENDED_READ_PREFLIGHT\n#include <xwnextended.h>\n#endif',1)
needle='    printf("XWN70: second-stage file and configuration verified\\n");'
assert s.count(needle)==1
s=s.replace(needle,needle+'\n#ifdef XBOX_NATIVE_EXTENDED_READ_PREFLIGHT\n    XwnExtendedReadPreflight();\n#endif')
p.write_text(s)
p=src/'rosload.cmake';s=p.read_text();s+='''
option(XBOX_NATIVE_EXTENDED_READ_PREFLIGHT "Read owned 250GB FATX fixture then halt" OFF)
if(XBOX_NATIVE_EXTENDED_READ_PREFLIGHT)
    if(NOT SARCH STREQUAL "xbox" OR NOT XBOX_NATIVE_IO_PREFLIGHT)
        message(FATAL_ERROR "Extended read preflight requires Xbox IO preflight")
    endif()
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_EXTENDED_READ_PREFLIGHT=1)
endif()
''';p.write_text(s)
