"""Fresh source-only841: observe display image loading; no functional change."""
import difflib,hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];A=W/'outputs/boot720-rootchain839'
B=Path('/home/paul/xbox-windows-native/boot720841-source001')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not B.exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
old=read(A/'source001.json');assert read(A/'closed001.json')['state']=='CLOSED'
r={'physical_access':False,'space':require_space(B,22),'parents':{},'changes':{},'trees':{},'cache_sites':old['cache_sites']}
for label,tree in old['trees'].items():
 p=Path('/home/paul/xbox-windows-native/boot720839-source001')/label
 assert subprocess.check_output(['git','-C',str(p),'write-tree'],text=True).strip()==tree
 assert not subprocess.check_output(['git','-C',str(p),'diff','--name-only'])
 dst=B/label;dst.mkdir(parents=True);subprocess.run(['git','-C',str(p),'checkout-index','--all','--prefix='+str(dst)+'/'],check=True)
 r['parents'][label]={'tree':tree,'path':str(p),'source_only':True}
def change(label,path,new):
 p=B/label/path;before=p.read_text(encoding='latin1');assert new!=before
 h=sha(p);p.write_text(new,encoding='latin1');r['changes'][label+'/'+path]={'before':h,'after':sha(p)}
 with (K/(label+'.patch')).open('a') as f:f.writelines(difflib.unified_diff(before.splitlines(True),new.splitlines(True),'a/'+path,'b/'+path))
for label,path in [('cromwell','boot/BootResetAction.c'),('reactos','boot/freeldr/freeldr/freeldr.c'),('reactos','boot/freeldr/freeldr/ntldr/winldr.c')]:
 p=B/label/path;t=p.read_text();change(label,path,t.replace('Boot839','Boot841'))
fd='drivers/filesystems/vfatfs/'
for p in (B/'fatx'/fd).iterdir():
 if p.is_file() and p.suffix in ['.c','.h','.txt']:
  t=p.read_text(encoding='latin1');u=t
  for a,b in [('Cache839','Cache841'),('cache839','cache841'),('XWN839','XWN841'),('0xE839','0xE841'),('Rows839','Rows841'),('Sequence839','Sequence841'),('Callback839','Callback841'),('callback839','callback841'),('check839','check841'),('hex839','hex841'),('CACHE839','CACHE841')]:u=u.replace(a,b)
  if u!=t:change('fatx',fd+p.name,u)
for ext in ['c','h']:(B/'fatx'/fd/('cache839.'+ext)).rename(B/'fatx'/fd/('cache841.'+ext))
def edit(n,a,b):
 p=B/'fatx'/fd/n;t=p.read_text(encoding='latin1');assert t.count(a)==1,(n,a,t.count(a));change('fatx',fd+n,t.replace(a,b))
edit('CMakeLists.txt','    cache841.c','    cache841.c\n    load841.c')
edit('iface.c','    Cache841Initialize();','    Cache841Initialize();\n    Load841Initialize();')
p=B/'fatx'/fd/'vfat.h';change('fatx',fd+'vfat.h',p.read_text(encoding='latin1')+'\nVOID Load841Initialize(VOID);\nVOID Load841Open(PFILE_OBJECT File, NTSTATUS Status);\nVOID Load841Read(PVFAT_IRP_CONTEXT Context,NTSTATUS Status,ULONG Requested,LARGE_INTEGER Offset);\n')
edit('create.c','''    if (NT_SUCCESS(Status))
        IrpContext->PriorityBoost = IO_DISK_INCREMENT;

    return Status;''','''    if (NT_SUCCESS(Status))
        IrpContext->PriorityBoost = IO_DISK_INCREMENT;

    Load841Open(IrpContext->FileObject, Status);
    return Status;''')
edit('rw.c','''ByeBye:
    return Status;
}

VOID
NTAPI
VfatStackOverflowRead''','''ByeBye:
    Load841Read(IrpContext, Status, Length, ByteOffset);
    return Status;
}

VOID
NTAPI
VfatStackOverflowRead''')
(B/'fatx'/fd/'load841.c').write_bytes((K/'load841.c').read_bytes())
for label in old['trees']:
 dst=B/label;subprocess.run(['git','init','-q',str(dst)],check=True);subprocess.run(['git','-C',str(dst),'config','core.autocrlf','false'],check=True);subprocess.run(['git','-C',str(dst),'add','-f','.'],check=True);r['trees'][label]=subprocess.check_output(['git','-C',str(dst),'write-tree'],text=True).strip()
r['retention_unchanged_sha256']=sha(B/'cromwell/boot/retain835.c');r['loader_fat_unchanged_sha256']=sha(B/'reactos/boot/freeldr/freeldr/lib/fs/fat.c')
r['scope']='RAM-only opens/reads and image-load observations; no functional PCI/display/filesystem change. Existing839 root fix and838 metadata fix retained.'
(K/'source001.json').write_text(json.dumps(r,indent=2)+'\n')
for n in ['main.c','Makefile','layout.c','layout.h','plan.c','plan.h','page.c','page.h','bridge.S','fixture.S','link.ld','plan_test.py','retain835.c']:
 data=(A/n).read_bytes()
 if n in ['main.c','Makefile']:data=data.replace(b'Windows839',b'Windows841').replace(b'Boot839',b'Boot841').replace(b'boot839',b'boot841').replace(b'xwn839',b'xwn841')
 (K/n).write_bytes(data)
for n in ['cache841.c','cache841.h']:(K/n).write_bytes((B/'fatx'/fd/n).read_bytes())
for n in ['build-chain002.py','build-driver002.py','qualify-chain002.py','host006.py','cpu005.py','build002.py','qualify-driver002.py','review-driver.py','physical002.py']:
 t=(A/n).read_text().replace('boot720-rootchain839','boot720-load841').replace('839','841')
 if n=='physical002.py':t=t.replace("['root001','fatpage002',","['load-host001',").replace('isolated FATX root-chain fix841 with cache diagnostic','display-load observation841; existing FATX fixes')
 (K/n).write_text(t)
base=read(A/'baseline001.json');base['scope']='Immutable installed package; restore SYSTEM from clean archive before841. No failed runtime parent.'
base['projected_console_reserve']['additional_owned_budget']+=16*1024**2;base['projected_console_reserve']['projected_remaining']-=16*1024**2
(K/'baseline001.json').write_text(json.dumps(base,indent=2)+'\n');(K/'.gitattributes').write_bytes(b'* -text\n')
print('841 fresh source prepared')
