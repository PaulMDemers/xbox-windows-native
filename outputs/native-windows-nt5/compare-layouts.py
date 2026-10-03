import json,pathlib
out=pathlib.Path(__file__).resolve().parent
actual=json.loads((out/'microsoft-kernel-layouts.json').read_text())['structures']
compiled=json.loads((out/'hal-layout-probe.json').read_text())['values']
mapping={
    'fast_mutex_size':('_FAST_MUTEX',None), 'ktrap_frame_size':('_KTRAP_FRAME',None),
    'prcb_size':('_KPRCB',None), 'thread_size':('_KTHREAD',None),
    'pcr_prcb_offset':('_KPCR','Prcb'), 'prcb_current_thread_offset':('_KPRCB','CurrentThread'),
    'prcb_major_version_offset':('_KPRCB','MajorVersion'), 'prcb_build_type_offset':('_KPRCB','BuildType'),
    'trap_eip_offset':('_KTRAP_FRAME','Eip'), 'trap_eflags_offset':('_KTRAP_FRAME','EFlags'),
    'trap_exception_list_offset':('_KTRAP_FRAME','ExceptionList'),
    'thread_header_debug_active_offset':('_KTHREAD','DebugActive'),
}
checks=[]
for name,(struct,field) in mapping.items():
    expected=actual[struct]['fields'][field]['offset'] if field else actual[struct]['size']
    checks.append({'item':name,'compiled':compiled[name],'windows_2000':expected,'matches':compiled[name]==expected})
report={'scope':'Exact 2195.7376 Microsoft PDB versus actual NT5 HAL compile flags. Selected offsets only; this is not complete ABI validation.',
        'checks':checks,'known_execution_contracts':[
          'Kei386EoiHelper expects a trap frame in both ESP and EBP, unlike the current KiEoiHelper C interface.',
          'Windows KeUpdateSystemTime consumes the increment in EAX; the ReactOS fastcall declaration passes it in EDX.',
          'KiEnterInterruptTrap reads KTHREAD.Header.DebugActive at offset 3; the Windows thread field is at offset 44.',
          'Full KPRCB and KTHREAD layouts differ despite matching common prefix fields. Audit every inherited access before kernel entry.'
        ]}
(out/'abi-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(checks,indent=2))
