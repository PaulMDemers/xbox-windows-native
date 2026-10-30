"""Fresh837 boot and diagnostic FATX sources; no installed driver mutation."""
import difflib,hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];A=W/'outputs/boot720-root836'
B=Path('/home/paul/xbox-windows-native/boot720837-source001')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not B.exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'physical_access':False,'space':require_space(B,22),'parents':{},'changes':{},'trees':{},'cache_sites':{}}
parents={n:(Path('/home/paul/xbox-windows-native/boot720836-source001')/n,t) for n,t in json.loads((A/'source001.json').read_text())['trees'].items()}
parents['fatx']=(Path('/home/paul/xbox-windows-native/build/fatx-directory-order-001/source'),'8e12297ca0ed53383fe9aaebef152c26aee5a43b')
for label,(p,tree) in parents.items():
 assert subprocess.check_output(['git','-C',str(p),'write-tree'],text=True).strip()==tree
 assert not subprocess.check_output(['git','-C',str(p),'diff','--name-only'])
 dst=B/label;dst.mkdir(parents=True)
 subprocess.run(['git','-C',str(p),'checkout-index','--all','--prefix='+str(dst)+'/'],check=True)
 r['parents'][label]={'tree':tree,'path':str(p),'source_only':True}
def change(label,path,new):
 p=B/label/path;before=p.read_text();old=sha(p);assert new!=before;p.write_text(new)
 r['changes'][label+'/'+path]={'before':old,'after':sha(p)}
 with (K/(label+'.patch')).open('a') as f:f.writelines(difflib.unified_diff(before.splitlines(True),new.splitlines(True),'a/'+path,'b/'+path))
for label,path in [('cromwell','boot/BootResetAction.c'),('reactos','boot/freeldr/freeldr/freeldr.c')]:
 t=(B/label/path).read_text();assert 'XWN16Boot836' in t;change(label,path,t.replace('XWN16Boot836','XWN16Boot837'))
path='boot/freeldr/freeldr/ntldr/winldr.c';t=(B/'reactos'/path).read_text()
anchor='    NtLdrOutputLoadMsg(FullPath, NULL);\n    Success = PeLdrLoadImage(FullPath, LoaderBootDriver, &DriverBase);'
assert t.count(anchor)==1
override='''    /* Isolated837 diagnostic: only this boot uses its private FATX image.
     * Keep the installed registry, service name and Windows image untouched. */
    if (_stricmp(DllName, "xwnfatx.sys") == 0)
    {
        if (_stricmp(DriverPath, "system32\\\\drivers\\\\") != 0)
            return FALSE;
        RtlStringCbPrintfA(FullPath, sizeof(FullPath), "%s\\\\loader\\\\xwnfatx.sys", FrLdrGetBootPath());
    }

'''
change('reactos',path,t.replace(anchor,override+anchor))
fd='drivers/filesystems/vfatfs/'
site=0
for p in sorted((B/'fatx'/fd).glob('*.c')):
 lines=p.read_text().splitlines(True);new=[]
 for line_no,line in enumerate(lines,1):
  if '"' not in line:
   for old,fn in [('CcMapData(', 'Cache837Map('),('CcPinRead(', 'Cache837Pin(')]:
    if old in line:
     assert line.count(old)==1;site+=1;r['cache_sites'][str(site)]={'file':p.name,'line':line_no,'api':old[:-1],'source':line.strip()}
     line=line.replace(old,fn+str(site)+', ')
  new.append(line)
 if ''.join(new)!=p.read_text():change('fatx',fd+p.name,''.join(new))
assert site>=30
p=B/'fatx'/fd/'vfat.h';t=p.read_text()
decl='''
VOID Cache837Initialize(VOID);
BOOLEAN Cache837Map(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length,ULONG Flags,PVOID *Bcb,PVOID *Buffer);
BOOLEAN Cache837Pin(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length,ULONG Flags,PVOID *Bcb,PVOID *Buffer);
'''
change('fatx',fd+'vfat.h',t+'\n'+decl)
p=B/'fatx'/fd/'iface.c';t=p.read_text();assert t.count('    return STATUS_SUCCESS;')==1
change('fatx',fd+'iface.c',t.replace('    return STATUS_SUCCESS;','    Cache837Initialize();\n    return STATUS_SUCCESS;'))
p=B/'fatx'/fd/'CMakeLists.txt';t=p.read_text();change('fatx',fd+'CMakeLists.txt',t.replace('    blockdev.c','    cache837.c\n    blockdev.c'))
for n in ['cache837.c','cache837.h']:(B/'fatx'/fd/n).write_bytes((K/n).read_bytes())
r['new_diagnostic_sources']={n:sha(K/n) for n in ['cache837.c','cache837.h']}
for label in parents:
 dst=B/label;subprocess.run(['git','init','-q',str(dst)],check=True);subprocess.run(['git','-C',str(dst),'config','core.autocrlf','false'],check=True)
 subprocess.run(['git','-C',str(dst),'add','-f','.'],check=True);r['trees'][label]=subprocess.check_output(['git','-C',str(dst),'write-tree'],text=True).strip()
r['retention_unchanged_sha256']=sha(B/'cromwell/boot/retain835.c')
r['loader_fat_unchanged_sha256']=sha(B/'reactos/boot/freeldr/freeldr/lib/fs/fat.c')
(K/'source001.json').write_text(json.dumps(r,indent=2)+'\n')
for n in ['main.c','Makefile','layout.c','layout.h','plan.c','plan.h','page.c','page.h','bridge.S','fixture.S','link.ld','plan_test.py','retain835.c']:
 data=(A/n).read_bytes()
 if n in ['main.c','Makefile']:data=data.replace(b'836',b'837')
 (K/n).write_bytes(data)
for n in ['build-chain002.py','qualify-chain.py','host006.py','cpu005.py','build001.py']:
 t=(A/n).read_text().replace('boot720-root836','boot720-cache837').replace('boot720836-source001','boot720837-source001').replace('xwn836','xwn837')
 (K/n).write_text(t)
(K/'.gitattributes').write_bytes(b'* -text\n')
print('Fresh837 sources exported;',site,'cache call sites; installed driver untouched')
