"""Review full-image integration and retained component identities; no launch."""
import datetime,hashlib,json,re
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('C:/xwn678/build001');out=K/'review001.json'
assert not out.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,checks=[])
def check(n,c):assert c,n;r['checks'].append(n)
try:
 b=json.loads((K/'build001.json').read_text());e=json.loads((K/'entry001.json').read_text())
 check('build completed with no deployment',b['passed'] and not b['deployed'] and not b['physical_access'])
 check('25 fresh function fixtures',e['passed'] and len(e['cases'])==25)
 for n,h in b['source_pins'].items():check('source '+n,sha(W/n)==h)
 for n,v in b['artifacts'].items():check('artifact '+n,sha(B/n)==v['sha256'])
 check('entry test source',sha(K/'entry.py')==e['source_sha256'])
 check('entry exact firmware',sha(B/'image-crom.bin')==e['binary_sha256'])
 check('19 unchanged objects, two sections each',len(b['unchanged_objects'])==38)
 for n,h in b['unchanged_objects'].items():
  stem,section=n.split('.',1)
  check('old/new object '+n,sha(B/(stem+'-old.'+section))==sha(B/(stem+'-new.'+section))==h)
 old=(W/'outputs/watched674/export.c').read_bytes()
 expected=old.replace(b'#include "integration.h"',b'#include "integration.h"\nextern void terminal675(void) __attribute__((noreturn));')
 # Compare normalized text only here; build receipt separately pins exact bytes.
 old=(W/'outputs/watched674/export.c').read_text()
 expected=old.replace('#include "integration.h"','#include "integration.h"\nextern void terminal675(void) __attribute__((noreturn));')
 expected=expected.replace('if(entry672())irq_hold669();\n Phase671=4;terminal670(&Config671);','Phase671=4;terminal675();')
 check('only export declaration and final route changed',expected==(K/'export.c').read_text())
 dis=(B/'disassembly.stdout').read_text()
 fn=lambda n:dis.split('<'+n+'>:',1)[1].split('\n\n',1)[0]
 ex=fn('XwnExport657')
 check('freeze bridge encode probe order',ex.index('<irq_enter669>')<ex.index('<xwn652_bridge>')<ex.index('<prepare670>')<ex.index('<terminal675>'))
 check('export no sender or old LED route',not re.search(r'<(?:entry672|terminal670|NativeSend656|send656)>',ex))
 check('terminal cannot return',not re.search(r'\tret\b',fn('terminal675')) and '<irq_hold669>' in fn('terminal675'))
 check('retained CLI HLT','\tcli' in fn('irq_hold669') and '\thlt' in fn('irq_hold669'))
 for n in ['terminal675','probe675','delay656','write658']:
  check(n+' no IF enable/reset/allocator/sender',not re.search(r'\t(?:sti|popf\w*)\b|<(?:malloc|free|BootResetAction|send656|NativeSend656)>',fn(n)))
 check('refused wait has no I/O or call',not re.search(r'\t(?:call\w*|in[bwl]?|out[bwl]?)\b',fn('refuse_wait')))
 check('native exact clock port',bool(re.search(r'\tin\s+\(%dx\),%eax',fn('ticks'))) and (int(re.search(r'\$0x([0-9a-f]+),%edx',fn('ticks'))[1],16)&65535)==0x8008)
 sym={v[2]:int(v[0],16) for line in (B/'symbols.stdout').read_text().splitlines() if len(v:=line.split())==3}
 ranges=[(sym[n],sym[n]+size,n) for n,size in [('Record675',404),('Return675',4),('Record670',1612),('Frozen671',704)]]
 for a,z,n in ranges:check('BSS bounds '+n,sym['BSS_BASE']<=a<z<=sym['BSS_END']<=0x027c0000 and a%4==0)
 ordered=sorted(ranges);check('record ranges disjoint',all(a[1]<=b[0] for a,b in zip(ordered,ordered[1:])))
 check('all terminal, one-shot and source-preserving',all(c['held'] and c['repeat_no_io'] and c['input_unchanged'] for c in e['cases']))
 check('no LEDoff requested',all([8,0] not in c['commands'] for c in e['cases']))
 r['passed']=True
except BaseException as exc:r['failure']=repr(exc);raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['checks']),'integration/provenance checks')
