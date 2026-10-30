"""Fresh836 source trees;835 source-only reuse, fixed720 retained unchanged."""
import difflib,hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];A=W/'outputs/boot720-native835'
B=Path('/home/paul/xbox-windows-native/boot720836-source001')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not B.exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'physical_access':False,'space':require_space(B,21.5),'parents':{},'changes':{},'trees':{}}
parent=json.loads((A/'source002.json').read_text())
for label,tree in parent['trees'].items():
 p=Path('/home/paul/xbox-windows-native/boot720835-source001')/label
 assert subprocess.check_output(['git','-C',str(p),'write-tree'],text=True).strip()==tree
 assert not subprocess.check_output(['git','-C',str(p),'diff','--name-only'])
 dst=B/label;dst.mkdir(parents=True)
 subprocess.run(['git','-C',str(p),'checkout-index','--all','--prefix='+str(dst)+'/'],check=True)
 r['parents'][label]={'tree':tree,'path':str(p),'source_only':True}
def change(label,path,new):
 p=B/label/path;before=p.read_text();old=sha(p);p.write_text(new)
 r['changes'][label+'/'+path]={'before':old,'after':sha(p)}
 with (K/(label+'.patch')).open('a') as f:f.writelines(difflib.unified_diff(before.splitlines(True),new.splitlines(True),'a/'+path,'b/'+path))
for label,path in [('cromwell','boot/BootResetAction.c'),('reactos','boot/freeldr/freeldr/freeldr.c')]:
 t=(B/label/path).read_text();assert 'XWN16Boot835' in t
 change(label,path,t.replace('XWN16Boot835','XWN16Boot836'))
fat='boot/freeldr/freeldr/lib/fs/fat.c'
q=json.loads((K/'root001.json').read_text());assert q['passed']
assert sha(B/'reactos'/fat)==q['source_sha256']
patched=Path('/mnt/c/xwn836/root001/fat-after.c');assert sha(patched)==q['patched_source_sha256']
change('reactos',fat,patched.read_text())
for label in parent['trees']:
 dst=B/label
 subprocess.run(['git','init','-q',str(dst)],check=True)
 subprocess.run(['git','-C',str(dst),'config','core.autocrlf','false'],check=True)
 subprocess.run(['git','-C',str(dst),'add','-f','.'],check=True)
 r['trees'][label]=subprocess.check_output(['git','-C',str(dst),'write-tree'],text=True).strip()
r['retention_unchanged_sha256']=sha(B/'cromwell/boot/retain835.c')
assert r['retention_unchanged_sha256']==sha(A/'retain835.c')
(K/'source001.json').write_text(json.dumps(r,indent=2)+'\n')
# Fresh frontend namespace; bridge/layout algorithms remain byte-identical.
for n in ['main.c','Makefile','layout.c','layout.h','plan.c','plan.h','page.c','page.h','bridge.S','fixture.S','link.ld','plan_test.py','retain835.c']:
 data=(A/n).read_bytes()
 if n in ['main.c','Makefile']:data=data.replace(b'835',b'836').replace(b'xwn-native-mode831',b'xwn-fixed720-836')
 (K/n).write_bytes(data)
for n in ['build-chain002.py','qualify-chain.py','host006.py','cpu005.py','build001.py']:
 t=(A/n).read_text().replace('boot720-native835','boot720-root836').replace('boot720835-source001','boot720836-source001').replace('xwn835','xwn836')
 t=t.replace('source002.json','source001.json')
 if n=='build001.py':t=t.replace('830','836')
 (K/n).write_text(t)
(K/'.gitattributes').write_bytes(b'* -text\n')
print('Fresh836 source export and pinned root fix ready; no hardware access')
