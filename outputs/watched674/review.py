"""Review exact full-image entry, linkage, provenance and host-only limits."""
import datetime,hashlib,json,re,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];S=Path('C:/xwn674/source001');P=Path('C:/xwn671/source001');B=Path('C:/xwn674/build001');out=K/'review001.json'
assert not out.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,checks=[],physical_qualified=False)
def check(n,v):assert v,n;r['checks'].append(n)
try:
 b=json.loads((K/'build001.json').read_text());e=json.loads((K/'execute001.json').read_text());entry=json.loads((K/'entry001.json').read_text())
 check('compiled full image',b['status']=='compiled-host-only-unqualified')
 for n,h in b['source_pins'].items():check('source '+n,sha(W/n)==h)
 for n in ['default.xbe','image-crom.elf','image-crom.bin','symbols.stdout','disassembly.stdout']:check('artifact '+n,sha(B/n)==b['artifacts'][n]['sha256'])
 check('40 full-linked transport cases',e['passed'] and len(e['cases'])==40 and e['source_sha256']==sha(K/'execute.py'))
 check('17 actual entry cases',entry['passed'] and len(entry['cases'])==17 and entry['source_sha256']==sha(K/'entry.py'))
 check('same linked image',e['binary_sha256']==entry['binary_sha256']==sha(B/'image-crom.bin'))
 check('34 unchanged original object sections',len(b['unchanged_objects'])==34)
 for n in ['drivers/video/xwn_hd_native.c','drivers/video/BootVgaInitialization.c','drivers/diag656/native.c','drivers/diag656/nic.c','drivers/diag656/admission.c','drivers/diag657/packet.c','drivers/diag657/bridge.c','drivers/pci/pci.c','drivers/pci/BootInterrupts.c','boot/BootResetAction.c','boot/BootStartup.S','scripts/ldscript-crom.ld']:
  check('unchanged '+n,(S/n).read_bytes()==(P/n).read_bytes())
 for n,base in [('phase.c','terminal669'),('phase.h','terminal669'),('irq.S','terminal669')]:check('reused '+n,(S/'drivers/diag657'/n).read_bytes()==(W/'outputs'/base/n).read_bytes())
 check('export exact',(S/'drivers/diag657/export.c').read_bytes()==(K/'export.c').read_bytes())
 check('source trees unchanged',all(not subprocess.check_output(['git','-C',str(root),'diff','--name-only'],timeout=25) for root in [P,S]))
 check('new source tree exact',subprocess.check_output(['git','-C',str(S),'write-tree'],text=True,timeout=25).strip()==b['tree'])
 check('private identity header pin',sha(S/'drivers/diag657/identity657.h')==b['identity_header_sha256'])
 syms={a[2]:int(a[0],16) for line in (B/'symbols.stdout').read_text().splitlines() if len(a:=line.split())==3}
 check('owned aligned DMA inside actual BSS',0x02600000<=syms['_bss']<=syms['Dma656'] and syms['Dma656']%32==0 and syms['Dma656']+9280<=syms['BSS_END']<=0x027c0000)
 r['layout']={n:hex(syms[n]) for n in ['_bss','BSS_END','Dma656','Record670','Frozen671','Config671']}
 dis=(B/'disassembly.stdout').read_text()
 def fn(n):return dis.split('<'+n+'>:',1)[1].split('\n\n',1)[0]
 x=fn('XwnExport657');order=['irq_enter669','xwn652_bridge','prepare670','entry672','terminal670']
 check('linked freeze copy encode terminal order',[x.index('<'+n+'>') for n in order]==sorted(x.index('<'+n+'>') for n in order))
 check('no return from export',not re.search(r'\tret\b',x))
 check('no return from terminal',not re.search(r'\tret\b',fn('terminal670')))
 check('terminal hold explicit CLI/HLT','\tcli' in fn('irq_hold669') and '\thlt' in fn('irq_hold669'))
 for n in ['XwnExport657','xwn652_bridge','prepare670','terminal670','run669','seal669','NativeSend656','send656','write658','entry672','marker672','report672','classify672']:
  check(n+' no IF enable/reset/allocator',not re.search(r'\t(?:sti|popf\w*)\b|<(?:malloc|free|BootResetAction|Reset657)>',fn(n)))
 for n in ['PciReadDword','PciReadWord','PciWriteWord']:
  check(n+' actual port instructions', '\tout' in fn(n) and '\tud2' not in fn(n))
 check('real PCI symbols not test source',not (S/'drivers/diag657/host_boundary.S').exists())
 check('hardware capture precedes export',fn('XwnHdTry720').index('<xwn_hd_apply>')<fn('XwnHdTry720').index('<XwnExport657>'))
 check('display native object unchanged','xwn_hd_native.text' in b['unchanged_objects'])
 check('all entry repeat paths terminal',all(v['held'] and v['repeat_export_no_io'] and v['input_capture_unchanged'] for v in entry['cases']))
 check('capture flags distinct from new boundaries',entry['cases'][0]['freeze_before']&512 and not entry['cases'][0]['freeze_after']&512 and not entry['cases'][0]['transport_original_flags']&512)
 host=json.loads((K.parent/'signal672/host001.json').read_text())
 check('sanitizer protocol tests',host['passed'] and host['tests']['assertion_groups']==2763)
 for name in ['signal672.c','signal672.h','integration.c','integration.h']:
  check('new source exact '+name,(K/name).read_bytes()==(S/'drivers/diag657'/name).read_bytes())
 guards=json.loads((K/'guards001.json').read_text())
 check('linked marker and terminal guards',guards['passed'] and len(guards['cases'])==6 and guards['source_sha256']==sha(K/'guards.py'))
 check('guards same image',guards['binary_sha256']==sha(B/'image-crom.bin'))
 check('no hardware qualification inferred',not e['physical_access'] and not entry['physical_access'] and not guards['physical_access'])
 r['passed']=True;r['binary_sha256']=sha(B/'default.xbe');r['tree']=b['tree']
except BaseException as ex:r['failure']=repr(ex);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['checks']),'full-image checks')
