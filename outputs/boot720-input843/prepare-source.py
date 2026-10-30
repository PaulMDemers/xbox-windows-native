"""Fresh namespace-only reproduction of desktop842 with mouse attached at boot."""
from pathlib import Path
import difflib,hashlib,json,os,subprocess,sys
K=Path(__file__).resolve().parent;W=K.parents[1];A=W/'outputs/boot720-bridge842'
B=Path('/home/paul/xbox-windows-native/boot720843-source001')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not B.exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(A/'source001.json');assert read(A/'closed001.json')['state']=='CLOSED'
r={'physical_access':False,'space':require_space(B,22),'parents':{},'changes':{},'trees':{},'cache_sites':old['cache_sites'],'scope':'Namespace-only source reproduction of842. No functional display, storage, USB or input change. Mouse connected before boot; immutable hives restored, no runtime parent.'}
for label,tree in old['trees'].items():
 p=Path('/home/paul/xbox-windows-native/boot720842-source001')/label
 assert subprocess.check_output(['git','-C',str(p),'write-tree'],text=True).strip()==tree
 assert not subprocess.check_output(['git','-C',str(p),'diff','--name-only'])
 dst=B/label;dst.mkdir(parents=True)
 subprocess.run(['git','-C',str(p),'checkout-index','--all','--prefix='+str(dst)+'/'],check=True)
 r['parents'][label]={'tree':tree,'path':str(p),'source_only':True}

def change(label,path):
 p=B/label/path;data=p.read_bytes();new=data.replace(b'842',b'843')
 if data==new:return
 r['changes'][label+'/'+path]={'before':sha(p)};p.write_bytes(new);r['changes'][label+'/'+path]['after']=sha(p)
 with (K/(label+'.patch')).open('a') as f:f.writelines(difflib.unified_diff(data.decode('latin1').splitlines(True),new.decode('latin1').splitlines(True),'a/'+path,'b/'+path))
for label,path in [('cromwell','boot/BootResetAction.c'),('reactos','boot/freeldr/freeldr/freeldr.c'),('reactos','boot/freeldr/freeldr/ntldr/winldr.c')]:change(label,path)
fd='drivers/filesystems/vfatfs/'
for p in (B/'fatx'/fd).iterdir():
 if p.is_file() and p.suffix in ['.c','.h','.txt']:change('fatx',fd+p.name)
for prefix in ['cache','load']:
 for ext in ['c','h']:
  p=B/'fatx'/fd/(prefix+'842.'+ext)
  if p.exists():p.rename(B/'fatx'/fd/(prefix+'843.'+ext))
for label in old['trees']:
 dst=B/label;subprocess.run(['git','init','-q',str(dst)],check=True)
 subprocess.run(['git','-C',str(dst),'config','core.autocrlf','false'],check=True)
 subprocess.run(['git','-C',str(dst),'add','-f','.'],check=True)
 r['trees'][label]=subprocess.check_output(['git','-C',str(dst),'write-tree'],text=True).strip()
r['retention_unchanged_sha256']=sha(B/'cromwell/boot/retain835.c');r['loader_fat_unchanged_sha256']=sha(B/'reactos/boot/freeldr/freeldr/lib/fs/fat.c')
for key in ['retention_unchanged_sha256','loader_fat_unchanged_sha256']:assert r[key]==old[key]
assert sha(B/'cromwell/drivers/pci/pci.c')==sha(Path('/home/paul/xbox-windows-native/boot720842-source001/cromwell/drivers/pci/pci.c'))
(K/'source001.json').write_text(json.dumps(r,indent=2)+'\n')
for n in ['main.c','Makefile','layout.c','layout.h','plan.c','plan.h','page.c','page.h','bridge.S','fixture.S','link.ld','plan_test.py','retain835.c']:
 data=(A/n).read_bytes()
 if n in ['main.c','Makefile']:data=data.replace(b'842',b'843')
 (K/n).write_bytes(data)
for n in ['cache843.c','cache843.h','load843.c']:(K/n).write_bytes((B/'fatx'/fd/n).read_bytes())
for n in ['build-chain002.py','build-driver003.py','qualify-chain002.py','qualify-driver002.py','qualify-load003.py','review-driver002.py','host007.py','cpu006.py','build003.py','physical003.py','qualify-bridge.py']:
 t=(A/n).read_text().replace('boot720-bridge842','boot720-input843').replace('842','843')
 if n=='physical003.py':t=t.replace("'restore-system001'","'restore-hives001'")
 (K/n).write_text(t)
base=read(A/'baseline001.json');base['scope']='Immutable installed package; five baseline hives restored before843, mouse preconnected. No runtime parent.'
base['projected_console_reserve']['additional_owned_budget']+=116*1024**2;base['projected_console_reserve']['projected_remaining']-=116*1024**2
assert base['projected_console_reserve']['projected_remaining']>512*1024**2
(K/'baseline001.json').write_text(json.dumps(base,indent=2)+'\n');(K/'.gitattributes').write_bytes(b'* -text\n')
print('843 source prepared: namespace only;842 functional source unchanged')
