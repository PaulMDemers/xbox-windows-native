from pathlib import Path
root=Path('/home/paul/xbox-windows-native/sources/reactos')
kit=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-entry')
loader=root/'boot/freeldr/freeldr'
(loader/'ntldr/xwnentryprobe.h').write_bytes((kit/'xwnentryprobe.h').read_bytes())
(root/'hal/halx86/xboxnt5/entryprobe.c').write_bytes((kit/'entryprobe.c').read_bytes())
p=loader/'pcat.cmake';s=p.read_text();s+='''
option(XBOX_NATIVE_FATX_ENTRY_PREFLIGHT "Enter NT5 only to an armed first-HAL halt" OFF)
if(XBOX_NATIVE_FATX_ENTRY_PREFLIGHT AND
   (NOT XBOX_NATIVE_FATX_PAGING_PREFLIGHT OR XBOX_NATIVE_NT5_ENTER OR XBOX_NATIVE_NT5_AUTORUN))
    message(FATAL_ERROR "FATX entry probe requires paging diagnostic and forbids general entry/autorun")
endif()
''';p.write_text(s)
p=loader/'rosload.cmake';s=p.read_text();s+='''
if(XBOX_NATIVE_FATX_ENTRY_PREFLIGHT)
    target_compile_definitions(rosload PRIVATE XBOX_NATIVE_FATX_ENTRY_PREFLIGHT=1)
endif()
''';p.write_text(s)
p=loader/'ntldr/winldr.c';s=p.read_text();needle='static DECLSPEC_NORETURN VOID\nXwnFinishPagingProbe('
assert s.count(needle)==1;s=s.replace(needle,'#ifdef XBOX_NATIVE_FATX_ENTRY_PREFLIGHT\n#include "xwnentryprobe.h"\n#endif\n\n'+needle)
needle='    Record[19] = 0x50414745;';assert s.count(needle)==1
s=s.replace(needle,needle+'\n#ifdef XBOX_NATIVE_FATX_ENTRY_PREFLIGHT\n    if (Valid) XwnEnterKernelProbe(LoaderBlock);\n#endif')
p.write_text(s)
p=root/'hal/halx86/xboxnt5/CMakeLists.txt';s=p.read_text().replace('fmutex.c trapentry.c kdport.c translate.c rootbus.c', 'fmutex.c trapentry.c kdport.c translate.c rootbus.c entryprobe.c')
s+='''
option(XBOX_NT5_ENTRY_PREFLIGHT "Unconditional first-processor HAL diagnostic halt" OFF)
if(XBOX_NT5_ENTRY_PREFLIGHT)
    target_compile_definitions(halxboxnt5 PRIVATE XBOX_NT5_ENTRY_PREFLIGHT=1)
endif()
''';p.write_text(s)
p=root/'hal/halx86/xboxnt5/halnt5.spec';s=p.read_text();s+='\n@ stdcall XwnConfigureEntryProbe(ptr long)\n';p.write_text(s)
p=root/'hal/halx86/generic/halinit.c';s=p.read_text();s=s.replace('/* GLOBALS *******************************************************************/','''#ifdef XBOX_NT5_ENTRY_PREFLIGHT
DECLSPEC_NORETURN VOID HalpXwnFirstProcessor(ULONG, PLOADER_PARAMETER_BLOCK, PVOID);
#endif

/* GLOBALS *******************************************************************/''')
a='''    /* Hal specific initialization for this cpu */''';b='''#ifdef XBOX_NT5_ENTRY_PREFLIGHT
    HalpXwnFirstProcessor(ProcessorNumber, LoaderBlock, _ReturnAddress());
#else
    /* Hal specific initialization for this cpu */''';assert s.count(a)==1;s=s.replace(a,b)
a='''        HalpRegisterKdSupportFunctions();
    }
}''';assert s.count(a)==1;s=s.replace(a,'''        HalpRegisterKdSupportFunctions();
    }
#endif
}''')
a='''    PKPRCB Prcb = KeGetCurrentPrcb();''';assert s.count(a)==1;s=s.replace(a,'''#ifdef XBOX_NT5_ENTRY_PREFLIGHT
    /* Defense in depth: this build cannot continue into HAL system init. */
    _disable(); for (;;) __halt();
#endif
    PKPRCB Prcb = KeGetCurrentPrcb();''');p.write_text(s)
