"""Admission review of exact artifacts; no console access."""
import hashlib,json,subprocess,re
from pathlib import Path
K=Path(__file__).resolve().parent;S=Path('C:/xwn664/source001');P=Path('C:/xwn663/source001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
out=K/'review001.json';assert not out.exists();r=dict(passed=False,physical_access=False,checks=[])
def check(n,v):assert v,n;r['checks'].append(n)
try:
 b=read('build001.json');h=read('host001.json');c=read('compiled001.json')
 check('host and linked control cases',h['status']=='pass' and h['tests']['cases']==53760 and c['passed'] and len(c['cases'])==35)
 check('linked image pin',c['image_sha256']==b['artifacts']['image-crom.bin']['sha256'])
 check('compiled harness pin',c['source_sha256']==sha(K/'compiled.py'))
 for n,p in b['source_pins'].items():check('build pin '+n,sha(K/n)==p)
 for n in ['export.c','classify.c','classify.h']:check('compiled source '+n,(S/'drivers/diag657'/n).read_bytes()==(K/n).read_bytes())
 for n in ['classify.c','classify.h']:check('host source '+n,(K/n).read_bytes()==Path('C:/xwn664/host001/source',n).read_bytes())
 for n in ['drivers/video/xwn_hd_native.c','drivers/diag657/control.c','drivers/diag657/control.h','drivers/diag657/indication.c','drivers/diag657/indication.h','drivers/diag657/packet.c','drivers/diag657/bridge.c','drivers/diag656/nic.c','drivers/diag656/native.c','drivers/diag656/admission.c']:
  check('unchanged '+n,(S/n).read_bytes()==(P/n).read_bytes())
 check('20 unchanged object sections',len(b['unchanged_objects'])==20)
 check('exact native admission header',(S/'drivers/diag657/admission.h').read_bytes()==(S/'drivers/diag656/admission.h').read_bytes()==(K.parent/'net656/admission.h').read_bytes())
 source=(K/'export.c').read_text()
 check('freeze encode entry show final hold',source.index('xwn652_bridge(&Frozen657')<source.index('Encode659=xwn655_encode')<source.index('EntryError659=latch659')<source.index('ShowError659=show658')<source.index('SendError664=NativeSend656')<source.index('FinalError659=latch659')<source.index('for(;;)'))
 allowed={'export657':{'delay656','xwn652_bridge','xwn655_encode','show658','latch659','mask664','cpu_bits664','cpu_stage664','NativeAdmission656','eeprom','NativeSend656','NativeAdmissionError656','NativeResult656'},'classify664':set()}
 for stem,expected in allowed.items():
  obj='/mnt/c/xwn664/source001/obj/'+stem+'.o'
  undef=subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-u',obj],text=True,timeout=25)
  check(stem+' dependencies',{v.split()[-1] for v in undef.splitlines()}==expected)
  dis=subprocess.check_output(['wsl','-d','Ubuntu','--','objdump','-dr',obj],text=True,timeout=25)
  check(stem+' no reset/network/legacy wait/state change',not any(v in dis for v in ['Reset657','wait_us','wbinvd','wrmsr','invlpg','\tsti','\tcli','popf','%cr']))
  if stem=='classify664':check('classifier contains no hardware reads/writes',not re.search(r'\t(?:in|out|inb|outb|inw|outw|inl|outl|rdmsr|cpuid)\s',dis))
 check('network only after preconditions','if(!Encode659 && !EntryError659 && !ShowError659)' in source)
 check('exact polling latch inherited',(S/'drivers/diag657/control.c').read_bytes()==(P/'drivers/diag657/control.c').read_bytes())
 previous=(K.parent/'indication663/classify.c').read_text().replace('663','664')
 current=(K/'classify.c').read_text()
 check('CPU and sender classification unchanged',current[current.index(' if(r->used'):]==previous[previous.index(' if(r->used'):])
 check('stored CPU predicates unchanged',current[:current.index('unsigned mask664')]==previous[:previous.index('unsigned mask664')])
 check('caller changes only entry mask and diagnostic names',(K/'export.c').read_text()==(K.parent/'indication663/export.c').read_text().replace('663','664').replace('latch659(&Smc659,0x55,&Entry659)','latch659(&Smc659,0xe1,&Entry659)'))
 masks=[0x10,0xff,0xc6,0xc4,0x4c,0x84,0xc7,0xf0,0x50,0x55,0xa5,0x5f,0xf5,0x05,0x01,0x11,0x33,0x0f,0x03]
 cycles=[]
 for mask in masks:
  seq=tuple((2 if mask&(1<<(i+4)) else 0)+(1 if mask&(1<<i) else 0) for i in range(3,-1,-1))
  cycles.append(min(seq[i:]+seq[:i] for i in range(4)))
 check('19 LED codes distinct under cyclic rotation',len(set(cycles))==len(masks))
 entry=tuple((2 if 0xe1&(1<<(i+4)) else 0)+(1 if 0xe1&(1<<i) else 0) for i in range(3,-1,-1))
 entry=min(entry[i:]+entry[:i] for i in range(4))
 check('entry distinct from every result and timed dark/green-off',entry not in cycles and entry!=(0,0,0,0) and entry!=(0,1,0,1))
 check('final classifier unchanged apart names',current==previous)
 r['entry_cycle']=list(entry)
 r['led_cycles']={hex(mask):list(cycle) for mask,cycle in zip(masks,cycles)}
 r.update(passed=True,binary_sha256=b['artifacts']['default.xbe']['sha256'],tree=b['tree'],physical_qualified=False,deliberate_hold=True)
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['checks']),'artifact reviews')
