from pathlib import Path
import json, subprocess, hashlib, sys, os, difflib
K=Path(__file__).resolve().parent; W=K.parents[1]; old=W/'outputs/boot720-input843'; B=Path('/home/paul/xbox-windows-native/bundle-boot844-source001'); prior=Path('/home/paul/xbox-windows-native/boot720843-source001')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not B.exists()
sys.path.insert(0,str(W/'tools')); from build_space import require_space
r={'space':require_space(B,23),'source_only':True,'physical_access':False,'parents':{},'changes':{},'trees':{}}
record=json.loads((old/'source001.json').read_text())
for name in ['cromwell','reactos']:
 p=prior/name; tree=subprocess.check_output(['git','-C',str(p),'write-tree'],text=True).strip(); assert tree==record['trees'][name]; assert not subprocess.check_output(['git','-C',str(p),'diff','--name-only'])
 dst=B/name; dst.mkdir(parents=True); subprocess.run(['git','-C',str(p),'checkout-index','--all','--prefix='+str(dst)+'/'],check=True); r['parents'][name]=tree
for name,path in [('cromwell','boot/BootResetAction.c'),('reactos','boot/freeldr/freeldr/freeldr.c')]:
 p=B/name/path; data=p.read_bytes(); assert data.count(b'XWN16Boot843') in (1,2); new=data.replace(b'XWN16Boot843',b'XWNEBoot'); p.write_bytes(new)
 r['changes'][name+'/'+path]={'before':hashlib.sha256(data).hexdigest(),'after':hashlib.sha256(new).hexdigest()}
 (K/(name+'.patch')).write_text(''.join(difflib.unified_diff(data.decode().splitlines(True),new.decode().splitlines(True),'a/'+path,'b/'+path)))
for name in ['cromwell','reactos']:
 p=B/name; subprocess.run(['git','init','-q',str(p)],check=True); subprocess.run(['git','-C',str(p),'config','core.autocrlf','false'],check=True); subprocess.run(['git','-C',str(p),'add','-f','.'],check=True); r['trees'][name]=subprocess.check_output(['git','-C',str(p),'write-tree'],text=True).strip()
(K/'source001.json').write_text(json.dumps(r,indent=2)+'\n')
