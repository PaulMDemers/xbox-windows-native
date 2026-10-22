"""Admission review of exact artifacts; no console access."""
import hashlib,json,subprocess,re
from pathlib import Path
K=Path(__file__).resolve().parent;S=Path('C:/xwn662/source001');P=Path('C:/xwn661/source001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
out=K/'review001.json';assert not out.exists();r=dict(passed=False,physical_access=False,checks=[])
def check(n,v):assert v,n;r['checks'].append(n)
try:
 b=read('build001.json');h=read('host001.json');c=read('compiled001.json')
 check('host and linked control cases',h['status']=='pass' and h['tests']['cases']==53760 and c['passed'] and len(c['cases'])==29)
 check('linked image pin',c['image_sha256']==b['artifacts']['image-crom.bin']['sha256'])
 check('compiled harness pin',c['source_sha256']==sha(K/'compiled.py'))
 for n,p in b['source_pins'].items():check('build pin '+n,sha(K/n)==p)
 for n in ['export.c','classify.c','classify.h']:check('compiled source '+n,(S/'drivers/diag657'/n).read_bytes()==(K/n).read_bytes())
 for n in ['classify.c','classify.h']:check('host source '+n,(K/n).read_bytes()==Path('C:/xwn662/host001/source',n).read_bytes())
 for n in ['drivers/video/xwn_hd_native.c','drivers/diag657/control.c','drivers/diag657/control.h','drivers/diag657/indication.c','drivers/diag657/indication.h','drivers/diag657/packet.c','drivers/diag657/bridge.c','drivers/diag656/nic.c','drivers/diag656/native.c','drivers/diag656/admission.c']:
  check('unchanged '+n,(S/n).read_bytes()==(P/n).read_bytes())
 check('20 unchanged object sections',len(b['unchanged_objects'])==20)
 check('exact native admission header',(S/'drivers/diag657/admission.h').read_bytes()==(S/'drivers/diag656/admission.h').read_bytes()==(K.parent/'net656/admission.h').read_bytes())
 source=(K/'export.c').read_text()
 check('freeze encode entry show final hold',source.index('xwn652_bridge(&Frozen657')<source.index('Encode659=xwn655_encode')<source.index('EntryError659=latch659')<source.index('ShowError659=show658')<source.index('SendError662=NativeSend656')<source.index('FinalError659=latch659')<source.index('for(;;)'))
 allowed={'export657':{'delay656','xwn652_bridge','xwn655_encode','show658','latch659','mask662','cpu_bits662','cpu_stage662','NativeAdmission656','eeprom','NativeSend656','NativeAdmissionError656','NativeResult656'},'classify662':set()}
 for stem,expected in allowed.items():
  obj='/mnt/c/xwn662/source001/obj/'+stem+'.o'
  undef=subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-u',obj],text=True,timeout=25)
  check(stem+' dependencies',{v.split()[-1] for v in undef.splitlines()}==expected)
  dis=subprocess.check_output(['wsl','-d','Ubuntu','--','objdump','-dr',obj],text=True,timeout=25)
  check(stem+' no reset/network/legacy wait/state change',not any(v in dis for v in ['Reset657','wait_us','wbinvd','wrmsr','invlpg','\tsti','\tcli','popf','%cr']))
  if stem=='classify662':check('classifier contains no hardware reads/writes',not re.search(r'\t(?:in|out|inb|outb|inw|outw|inl|outl|rdmsr|cpuid)\s',dis))
 check('network only after preconditions','if(!Encode659 && !EntryError659 && !ShowError659)' in source)
 check('exact polling latch inherited',(S/'drivers/diag657/control.c').read_bytes()==(P/'drivers/diag657/control.c').read_bytes())
 r.update(passed=True,binary_sha256=b['artifacts']['default.xbe']['sha256'],tree=b['tree'],physical_qualified=False,deliberate_hold=True)
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['checks']),'artifact reviews')
