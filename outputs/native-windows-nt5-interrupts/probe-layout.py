"""Compile ABI constants with the exact release Xbox HAL compiler flags."""
import json,os,pathlib,re,shlex,subprocess
if os.environ.get('XWN_BUILD_LEASE')!='held':raise SystemExit('Use the build resource lease.')
root=pathlib.Path('/home/paul/xbox-windows-native')
build=root/'build/hal-nt5'
out=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-nt5-interrupts')
ninja=root/'toolchains/RosBE-2.2.1/bin/ninja'
commands=subprocess.check_output([str(ninja),'-t','commands','halxboxnt5'],cwd=build,text=True)
line=next(line for line in commands.splitlines() if ' -c ' in line and line.endswith('/hal/halx86/generic/halinit.c'))
args=shlex.split(line)
source=build/'xwn-abi-layout.c';assembly=build/'xwn-abi-layout.s'
fields={
    'ntddi': 'NTDDI_VERSION', 'dbg':'DBG', 'hal_build_type':'HAL_BUILD_TYPE',
    'hal_dispatch_version':'HAL_DISPATCH_VERSION', 'hal_private_dispatch_version':'HAL_PRIVATE_DISPATCH_VERSION',
    'prcb_major_version':'PRCB_MAJOR_VERSION',
    'pcr_prcb_offset':'FIELD_OFFSET(KPCR, Prcb)',
    'prcb_build_type_offset':'FIELD_OFFSET(KPRCB, BuildType)',
    'prcb_major_version_offset':'FIELD_OFFSET(KPRCB, MajorVersion)',
    'prcb_current_thread_offset':'FIELD_OFFSET(KPRCB, CurrentThread)',
    'private_size':'sizeof(HAL_PRIVATE_DISPATCH)',
    'dispatch_size':'sizeof(HAL_DISPATCH)',
    'dispatch_dma_adapter_offset':'FIELD_OFFSET(HAL_DISPATCH, HalGetDmaAdapter)',
    'fast_mutex_size':'sizeof(FAST_MUTEX)', 'ktrap_frame_size':'sizeof(KTRAP_FRAME)',
    'prcb_size':'sizeof(KPRCB)', 'thread_size':'sizeof(KTHREAD)',
    'thread_header_debug_active_offset':'FIELD_OFFSET(KTHREAD, Header.DebugActive)',
    'trap_eip_offset':'FIELD_OFFSET(KTRAP_FRAME, Eip)',
    'trap_eflags_offset':'FIELD_OFFSET(KTRAP_FRAME, EFlags)',
    'trap_exception_list_offset':'FIELD_OFFSET(KTRAP_FRAME, ExceptionList)',
}

# Compare every trap field and the PCR/PRCB prefix used by the HAL's current
# interrupt/init code. Whole-structure sizes are intentionally still different.
for name in ('Irql','IRR','IrrActive','IDR','IDT','GDT','TSS','StallScaleFactor'):
    fields['KPCR.'+name] = 'FIELD_OFFSET(KPCR, '+name+')'
for name in ('MajorVersion','BuildType','CurrentThread','Number','CpuID','ProcessorState'):
    fields['KPRCB.'+name] = 'FIELD_OFFSET(KPRCB, '+name+')'
for name in ('DbgEbp','DbgEip','DbgArgMark','DbgArgPointer','TempSegCs','TempEsp','Dr0','Dr1','Dr2','Dr3','Dr6','Dr7','SegGs','SegEs','SegDs','Edx','Ecx','Eax','ExceptionList','SegFs','Edi','Esi','Ebx','Ebp','ErrCode','Eip','SegCs','EFlags','HardwareEsp','HardwareSegSs','V86Es','V86Ds','V86Fs','V86Gs'):
    fields['KTRAP_FRAME.'+name] = 'FIELD_OFFSET(KTRAP_FRAME, '+name+')'
for name in ('KernelDr0','KernelDr1','KernelDr2','KernelDr3','KernelDr6','KernelDr7'):
    fields['KPRCB.ProcessorState.SpecialRegisters.'+name] = 'FIELD_OFFSET(KPRCB, ProcessorState.SpecialRegisters.'+name+')'
fields['KIPCR.PrcbData.CurrentThread']='FIELD_OFFSET(KIPCR, PrcbData.CurrentThread)'

source.write_text('#include <hal.h>\n#undef KdSetupPciDeviceForDebugging\n#undef KdUnmapVirtualAddress\n#undef HalGetDmaAdapter\n'+''.join(f'const ULONG xwn_{name.replace('.', '_')} = {value};\n' for name,value in fields.items()))
new=[];index=0
while index<len(args):
    token=args[index]
    if token in ('-o','-c','-MF','-MT'):
        index+=2;continue
    if token in ('-MD','-MMD'):index+=1;continue
    new.append(token);index+=1
new+=['-S','-o',str(assembly),str(source)]
subprocess.run(new,cwd=build,check=True)
text=assembly.read_text()
values={}
for name in fields:
    match=re.search(r'^_xwn_'+name.replace('.', '_')+r':\s*\n\s*\.(long|space)\s+(\d+)',text,re.M)
    if not match:raise RuntimeError(f'Assembly constant missing: {name}')
    values[name]=int(match[2]) if match[1]=='long' else 0
(out/'hal-layout-probe.json').write_text(json.dumps({'method':'Compiled constants under actual release halinit.c flags; no kernel executed.', 'values':values,'command':new},indent=2)+'\n')
(out/'hal-layout-probe.c').write_text(source.read_text())
(out/'hal-layout-probe.s').write_text(text)
print(json.dumps(values,indent=2))
