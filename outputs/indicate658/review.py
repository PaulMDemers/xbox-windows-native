"""Review fresh658 sources, linked dependencies and indication ordering."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;S=Path('C:/xwn658/source001');P=Path('C:/xwn657/source001')
out=K/'review001.json';assert not out.exists()
r=dict(passed=False,physical_access=False,checks=[]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,ok):assert ok,name;r['checks'].append(name)
try:
 b=json.loads((K/'build001.json').read_text());c=json.loads((K/'compiled-wrapper001.json').read_text());h=json.loads((K/'host001.json').read_text())
 check('qualified host and compiled wrapper models',h['status']=='pass' and c['passed'] and len(c['cases'])==83 and c['image_sha256']==b['artifacts']['image-crom.bin']['sha256'])
 for n,pin in b['source_pins'].items():check('build source '+n,sha(K/n)==pin)
 for n in ['indication.c','indication.h']:check('host/native source '+n,(K/n).read_bytes()==(S/'drivers/diag657'/n).read_bytes()==Path('C:/xwn658/host001/source',n).read_bytes())
 for rel in ['drivers/video/xwn_hd_native.c','drivers/diag657/packet.c','drivers/diag657/packet.h','drivers/diag657/bridge.c','drivers/diag657/receipt.h','drivers/diag656/nic.c','drivers/diag656/admission.c','drivers/diag656/native.c']:
  check('unchanged '+rel,(S/rel).read_bytes()==(P/rel).read_bytes())
 source=(K/'export.c').read_text();old=(K.parent/'export657/export.c').read_text()
 check('unchanged bounded reset',source[source.index('unsigned Reset657'):source.index('static unsigned in658')]==old[old.index('unsigned Reset657'):old.index('__attribute__((noreturn))')])
 check('freeze encode then entry then sender then classification',source.index('xwn652_bridge(&Frozen657')<source.index('EncodeError657=xwn655_encode')<source.index('indicate658(1,4000)')<source.index('SendError657=NativeSend656')<source.index('classify658(EncodeError657'))
 check('safe cleanup gate retained','if(!EncodeError657 && (!NativeResult656.used || NativeResult656.safe_to_continue))' in source)
 check('16 unchanged module sections',len(b['unchanged_objects'])==16)
 allowed={'export657':{'NativeResult656','NativeSend656','NativeAdmissionError656','delay656','eeprom','xwn652_bridge','xwn655_encode','show658','classify658'},'indicate658':set()}
 for stem in allowed:
  obj='/mnt/c/xwn658/source001/obj/'+stem+'.o'
  text=subprocess.check_output(['wsl','-d','Ubuntu','--','objdump','-dr',obj],text=True,timeout=25)
  check(stem+' no legacy delay/cache/mapping/IRQ mutation',not any(v in text for v in ['wait_us','wbinvd','wrmsr','invlpg','\tsti','\tcli','popf','%cr']))
  undef=subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-u',obj],text=True,timeout=25)
  check(stem+' exact dependencies',{line.split()[-1] for line in undef.splitlines()}==allowed[stem])
 r.update(passed=True,binary_sha256=b['artifacts']['default.xbe']['sha256'],tree=b['tree'],compiled_cases=83,physical_indications_qualified=False)
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['checks']),'source/object checks')
