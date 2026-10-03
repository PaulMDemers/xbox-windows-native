"""Compare selected compiled offsets with the matching public PDB types."""
import json,pathlib
out=pathlib.Path(__file__).resolve().parent
v=json.loads((out/'hal-layout-probe.json').read_text())['values']
s=json.loads((out/'microsoft-kernel-layouts.json').read_text())['structures']
def off(t,f):return s['_'+t]['fields'][f]['offset']
checks=[]
for key,actual in v.items():
 if '.' not in key:continue
 parts=key.split('.')
 if len(parts)==2:expected=off(*parts)
 elif parts==['KIPCR','PrcbData','CurrentThread']:expected=off('KPCR','PrcbData')+off('KPRCB','CurrentThread')
 else:
  assert parts[:3]==['KPRCB','ProcessorState','SpecialRegisters']
  expected=off('KPRCB','ProcessorState')+off('KPROCESSOR_STATE','SpecialRegisters')+off('KSPECIAL_REGISTERS',parts[3])
 checks.append({'field':key,'compiled':actual,'windows':expected,'matches':actual==expected})
assert off('KPCR','DebugActive')==0x50
assert all(c['matches'] for c in checks)
report={'scope':'Selected fields used by interrupt entry, timer, PIC, processor prefix and trap return; not a complete ABI or source access audit.',
 'checked_offsets':checks,'nt5_pcr_debug_active':80,
 'known_whole_structure_differences':{'KPRCB':{'compiled':v['prcb_size'],'windows':s['_KPRCB']['size']},'KTHREAD':{'compiled':v['thread_size'],'windows':s['_KTHREAD']['size']}},
 'thread_debug_access':'New trap entry reads the native PCR.DebugActive byte at 0x50; it does not dereference KTHREAD.Header.DebugActive.'}
(out/'layout-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'matching_offsets':len(checks),'native_pcr_debug_flag':80}))
