"""Independent source/linked-object boundary review of diagnostic657."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;S=Path('C:/xwn657/source001');P=Path('C:/xwn656/source005')
out=K/'review001.json';assert not out.exists()
r=dict(passed=False,physical_access=False,checks=[])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,ok):assert ok,name;r['checks'].append(name)
try:
 b=json.loads((K/'build001.json').read_text());c=json.loads((K/'compiled-wrapper001.json').read_text())
 check('compiled exact native image',b['status']=='compiled-unqualified' and c['passed'] and c['image_sha256']==b['artifacts']['image-crom.bin']['sha256'])
 for n,h in b['source_pins'].items():check('source '+n,sha(K/n)==h)
 check('compiled modeled cases',len(c['cases'])==78)
 old=(P/'drivers/video/xwn_hd_native.c').read_text();new=(S/'drivers/video/xwn_hd_native.c').read_text()
 declaration='extern void XwnExport657(int,const struct xwn_hd_request *,const volatile struct xwn_hd_state *,const volatile struct xwn_trace649 *,const volatile struct readback651 *,const volatile struct readback651 *) __attribute__((noreturn));\n'
 check('unchanged pre-capture/apply/post-capture prefix',new.replace(declaration,'').split(' (void)mode;')[0]==old.split(' XwnDiag651Status=led651_show')[0])
 check('no legacy fallback or Windows return',new.endswith(' XwnExport657(result,&r,&XwnHdState311,&XwnTrace649,&XwnReadback651Pre,&XwnReadback651Post);\n}\n#endif\n'))
 for local,parent in [('packet.c','udp655/packet.c'),('bridge.c','receipt652/bridge.c'),('receipt.h','receipt652/receipt.h')]:check('unchanged '+local,(S/'drivers/diag657'/local).read_bytes()==(K.parent/parent).read_bytes())
 for n in ['nic.c','native.c','admission.c','nic.h','admission.h']:check('unchanged native656 '+n,(S/'drivers/diag656'/n).read_bytes()==(K.parent/'net656'/n).read_bytes())
 check('header-only freestanding adaptation',(S/'drivers/diag657/packet.h').read_text()==(K.parent/'udp655/packet.h').read_text().replace('#include <stddef.h>\n','').replace('../receipt652/receipt.h','receipt.h'))
 for stem in ['export657','encode657','bridge657']:
  obj='/mnt/c/xwn657/source001/obj/'+stem+'.o'
  text=subprocess.check_output(['wsl','-d','Ubuntu','--','objdump','-dr',obj],text=True,timeout=25)
  check(stem+' no legacy delay/cache/mapping/IRQ writes',not any(v in text for v in ['wait_us','wbinvd','wrmsr','invlpg','\tsti','\tcli','popf','%cr']))
  undef=subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-u',obj],text=True,timeout=25)
  allowed={'export657':{'NativeResult656','NativeSend656','delay656','eeprom','xwn652_bridge','xwn655_encode'},'encode657':set(),'bridge657':set()}[stem]
  check(stem+' declared dependencies',{line.split()[-1] for line in undef.splitlines()}==allowed)
 check('10 unchanged original module sections',len(b['unchanged_objects'])==10)
 r.update(passed=True,binary_sha256=b['artifacts']['default.xbe']['sha256'],source_tree=b['tree'],compiled_cases=78,scope='Source and compiled-wrapper models; actual native NIC and external firewall delivery unqualified.')
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['checks']),'source/linked-object review checks')
