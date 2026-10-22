"""Admission review of exact artifacts; no console access."""
import hashlib,json,subprocess,re
from pathlib import Path
K=Path(__file__).resolve().parent;S=Path('C:/xwn667/source001');P=Path('C:/xwn666/source001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
out=K/'review001.json';assert not out.exists();r=dict(passed=False,physical_access=False,checks=[])
def check(n,v):assert v,n;r['checks'].append(n)
try:
 b=read('build001.json');h=read('host001.json');c=read('compiled001.json')
 check('host and linked control cases',h['status']=='pass' and h['tests']['cases']==53760 and c['passed'] and len(c['cases'])==55)
 check('288 context cases and actual snapshot header layout',h['tests']['context_cases']==288 and h['layout']['flags_before_offset']==16 and h['layout']['flags_after_offset']==20 and h['layout']['pre_offset']==328 and h['layout']['post_offset']==516)
 check('linked image pin',c['image_sha256']==b['artifacts']['image-crom.bin']['sha256'])
 check('compiled harness pin',c['source_sha256']==sha(K/'compiled.py'))
 for n,p in b['source_pins'].items():check('build pin '+n,sha(K/n)==p)
 for n in ['export.c','classify.c','classify.h']:check('compiled source '+n,(S/'drivers/diag657'/n).read_bytes()==(K/n).read_bytes())
 for n in ['classify.c','classify.h']:check('host source '+n,(K/n).read_bytes()==Path('C:/xwn667/host001/source',n).read_bytes())
 for n in ['drivers/video/xwn_hd_native.c','drivers/diag657/control.c','drivers/diag657/control.h','drivers/diag657/indication.c','drivers/diag657/indication.h','drivers/diag657/packet.c','drivers/diag657/bridge.c','drivers/diag656/nic.c','drivers/diag656/native.c','drivers/diag656/admission.c']:
  check('unchanged '+n,(S/n).read_bytes()==(P/n).read_bytes())
 check('34 unchanged object sections',len(b['unchanged_objects'])==34)
 check('exact receipt header',(S/'drivers/diag657/receipt.h').read_bytes()==Path('C:/xwn667/host001/source/receipt.h').read_bytes())
 check('exact native admission header',(S/'drivers/diag657/admission.h').read_bytes()==(S/'drivers/diag656/admission.h').read_bytes()==(K.parent/'net656/admission.h').read_bytes())
 source=(K/'export.c').read_text()
 check('freeze encode entry show final hold',source.index('xwn652_bridge(&Frozen657')<source.index('Encode659=xwn655_encode')<source.index('EntryError659=latch659')<source.index('ShowError659=show658')<source.index('SendError667=NativeSend656')<source.index('FinalError659=latch659')<source.index('for(;;)'))
 allowed={'export657':{'delay656','xwn652_bridge','xwn655_encode','show658','latch659','mask667','context667','boundary667','boundary_mask667','BootDetectMemorySize','cpu_bits667','cpu_stage667','NativeAdmission656','eeprom','NativeSend656','NativeAdmissionError656','NativeResult656'},'classify667':set()}
 for stem,expected in allowed.items():
  obj='/mnt/c/xwn667/source001/obj/'+stem+'.o'
  undef=subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-u',obj],text=True,timeout=25)
  check(stem+' dependencies',{v.split()[-1] for v in undef.splitlines()}==expected)
  dis=subprocess.check_output(['wsl','-d','Ubuntu','--','objdump','-dr',obj],text=True,timeout=25)
  check(stem+' no reset/network/legacy wait/state change',not any(v in dis for v in ['Reset657','wait_us','wbinvd','wrmsr','invlpg','\tsti','\tcli','popf','%cr']))
  if stem=='classify667':check('classifier contains no hardware reads/writes',not re.search(r'\t(?:in|out|inb|outb|inw|outw|inl|outl|rdmsr|cpuid)\s',dis))
 check('network only after preconditions','if(!Encode659 && !EntryError659 && !ShowError659)' in source)
 check('exact polling latch inherited',(S/'drivers/diag657/control.c').read_bytes()==(P/'drivers/diag657/control.c').read_bytes())
 previous=(K.parent/'context666/classify.c').read_text().replace('666','667')
 current=(K/'classify.c').read_text()
 check('CPU and sender classification unchanged',current.startswith(previous))
 check('stored CPU predicates unchanged',current[:current.index('unsigned mask667')]==previous[:previous.index('unsigned mask667')])
 check('caller comparison occurs after original classification',source.index('OriginalMask667=mask667')<source.index('Context667=context667')<source.index('Mask659=boundary_mask667')<source.index('FinalError659=latch659'))
 check('comparison gated by original preconditions and IF admission','NativeAdmissionError656==A656_CPU && !NativeResult656.used' in source)

 masks=[0x50,0xff,0x03,0x0f,0xa5,0x55]
 cycles=[]
 for mask in masks:
  seq=tuple((2 if mask&(1<<(i+4)) else 0)+(1 if mask&(1<<i) else 0) for i in range(3,-1,-1))
  cycles.append(min(seq[i:]+seq[:i] for i in range(4)))
 check('6 LED codes distinct under cyclic rotation',len(set(cycles))==len(masks))
 entry=tuple((2 if 0xe1&(1<<(i+4)) else 0)+(1 if 0xe1&(1<<i) else 0) for i in range(3,-1,-1))
 entry=min(entry[i:]+entry[:i] for i in range(4))
 check('entry distinct from every result and timed dark/green-off',entry not in cycles and entry!=(0,0,0,0) and entry!=(0,1,0,1))
 check('old classifier retained as prefix',current.startswith(previous))
 check('360 memory boundary cases',h['tests']['memory_cases']==360)
 linked=read('boundary001.json')
 check('linked boundary placement and four modeled transitions',linked['passed'] and len(linked['cases'])==4 and linked['source_sha256']==sha(K/'boundary.py') and linked['image_sha256']==b['artifacts']['image-crom.bin']['sha256'])
 parent=(P/'boot/BootResetAction.c').read_text()
 check('only reset change is wrapper call and declaration',(S/'boot/BootResetAction.c').read_text()=='extern void XwnMemoryBoundary667(void);\n'+parent.replace('BootDetectMemorySize();','XwnMemoryBoundary667();'))
 for n in ['drivers/pci/pci.c','lib/misc/BootLibrary.c']:check('unchanged initializer '+n,(S/n).read_bytes()==(P/n).read_bytes())
 r['entry_cycle']=list(entry)
 r['led_cycles']={hex(mask):list(cycle) for mask,cycle in zip(masks,cycles)}
 r.update(passed=True,binary_sha256=b['artifacts']['default.xbe']['sha256'],tree=b['tree'],physical_qualified=False,deliberate_hold=True)
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['checks']),'artifact reviews')
