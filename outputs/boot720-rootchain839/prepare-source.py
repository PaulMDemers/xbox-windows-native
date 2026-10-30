"""Fresh839 source: FATX root-chain geometry and bounded cached label scan."""
import difflib,hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];A=W/'outputs/boot720-fatpage838'
B=Path('/home/paul/xbox-windows-native/boot720839-source001')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not B.exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=json.loads((A/'source001.json').read_text())
r={'physical_access':False,'space':require_space(B,22),'parents':{},'changes':{},'trees':{},'cache_sites':old['cache_sites']}
assert json.loads((A/'closed001.json').read_text())['state']=='CLOSED'
for label,tree in old['trees'].items():
 p=Path('/home/paul/xbox-windows-native/boot720838-source002')/label
 assert subprocess.check_output(['git','-C',str(p),'write-tree'],text=True).strip()==tree
 assert not subprocess.check_output(['git','-C',str(p),'diff','--name-only'])
 dst=B/label;dst.mkdir(parents=True);subprocess.run(['git','-C',str(p),'checkout-index','--all','--prefix='+str(dst)+'/'],check=True)
 r['parents'][label]={'tree':tree,'path':str(p),'source_only':True}
def change(label,path,new):
 p=B/label/path;before=p.read_text(encoding='latin1');h=sha(p);assert new!=before;p.write_text(new,encoding='latin1')
 r['changes'][label+'/'+path]={'before':h,'after':sha(p)}
 with (K/(label+'.patch')).open('a') as f:f.writelines(difflib.unified_diff(before.splitlines(True),new.splitlines(True),'a/'+path,'b/'+path))
for label,path in [('cromwell','boot/BootResetAction.c'),('reactos','boot/freeldr/freeldr/freeldr.c'),('reactos','boot/freeldr/freeldr/ntldr/winldr.c')]:
 t=(B/label/path).read_text();change(label,path,t.replace('838','839'))
fd='drivers/filesystems/vfatfs/'
for p in sorted((B/'fatx'/fd).iterdir()):
 if p.is_file() and p.suffix in ['.c','.h','.txt']:
  t=p.read_text(encoding='latin1')
  if '838' in t:change('fatx',fd+p.name,t.replace('838','839'))
for ext in ['c','h']:(B/'fatx'/fd/('cache838.'+ext)).rename(B/'fatx'/fd/('cache839.'+ext))
def edit(n,old,new,count=1):
 p=B/'fatx'/fd/n;t=p.read_text(encoding='latin1');assert t.count(old)==count,(n,old,t.count(old));change('fatx',fd+n,t.replace(old,new))
edit('vfat.h','    struct _VFATFCB *RootFcb;','    struct _VFATFCB *RootFcb;\n    ULONG FatXRootSize; /* Mount-time allocated root-chain bytes. */')
p=B/'fatx'/fd/'vfat.h';change('fatx',fd+'vfat.h',p.read_text(encoding='latin1')+'\nNTSTATUS FatXRootSize839(PDEVICE_EXTENSION DeviceExt, PULONG Size);\n')
edit('CMakeLists.txt','    cache839.c','    cache839.c\n    root839.c')
(B/'fatx'/fd/'root839.c').write_bytes((K/'root839.c').read_bytes())
edit('fsctl.c','    InitializeListHead(&DeviceExt->FcbListHead);','''    /* FATX root is cluster 1 of a potentially fragmented chain. Keep physical
     * layout fields unchanged; size the root cache before it is opened. */
    if (vfatVolumeIsFatX(DeviceExt))
    {
        Status = FatXRootSize839(DeviceExt, &DeviceExt->FatXRootSize);
        if (!NT_SUCCESS(Status))
            goto ByeBye;
    }

    InitializeListHead(&DeviceExt->FcbListHead);''')
edit('fcb.c','        FCB->entry.FatX.FileSize = pVCB->FatInfo.rootDirectorySectors * pVCB->FatInfo.BytesPerSector;','        FCB->entry.FatX.FileSize = pVCB->FatXRootSize;')
edit('fcb.c','        Size = pVCB->FatInfo.rootDirectorySectors * pVCB->FatInfo.BytesPerSector;\n    }\n    else','        Size = pVCB->FatXRootSize;\n    }\n    else')
edit('fcb.c','            Size = Vcb->FatInfo.rootDirectorySectors * Vcb->FatInfo.BytesPerSector;','            Size = vfatVolumeIsFatX(Vcb) ? Vcb->FatXRootSize :\n                   Vcb->FatInfo.rootDirectorySectors * Vcb->FatInfo.BytesPerSector;')
edit('rw.c','    if (FirstCluster == 1)','    if (FirstCluster == 1 && !vfatVolumeIsFatX(DeviceExt))',4)
edit('fat.c','    return DeviceExt->FatInfo.dataStart +','    if (vfatVolumeIsFatX(DeviceExt) && Cluster == 1)\n        return DeviceExt->FatInfo.rootStart;\n\n    return DeviceExt->FatInfo.dataStart +')
edit('fsctl.c','''                    CcUnpinData(Context);

                    _SEH2_TRY''','''                    CcUnpinData(Context);
                    Context = NULL;
                    /* A full directory may have no end-marker entry. */
                    if (FileOffset.QuadPart >= pFcb->RFCB.FileSize.QuadPart)
                        break;

                    _SEH2_TRY''')
r['repair_scope']='Bounded mount-time FATX root-chain size, correct cluster1 chain/sector dispatch, cached volume-label EOF bound. Existing root growth refusal retained; no format/allocation-policy/timing change.'
for label in old['trees']:
 dst=B/label;subprocess.run(['git','init','-q',str(dst)],check=True);subprocess.run(['git','-C',str(dst),'config','core.autocrlf','false'],check=True);subprocess.run(['git','-C',str(dst),'add','-f','.'],check=True);r['trees'][label]=subprocess.check_output(['git','-C',str(dst),'write-tree'],text=True).strip()
r['retention_unchanged_sha256']=sha(B/'cromwell/boot/retain835.c');r['loader_fat_unchanged_sha256']=sha(B/'reactos/boot/freeldr/freeldr/lib/fs/fat.c')
(K/'source001.json').write_text(json.dumps(r,indent=2)+'\n')
for n in ['main.c','Makefile','layout.c','layout.h','plan.c','plan.h','page.c','page.h','bridge.S','fixture.S','link.ld','plan_test.py','retain835.c']:
 data=(A/n).read_bytes()
 if n in ['main.c','Makefile']:data=data.replace(b'838',b'839')
 (K/n).write_bytes(data)
for n in ['cache839.c','cache839.h']:(K/n).write_bytes((B/'fatx'/fd/n).read_bytes())
for n in ['build-chain002.py','build-driver002.py','qualify-chain.py','host006.py','cpu005.py','build001.py','qualify-driver002.py','review-driver.py','physical.py','qualify-fatpage002.py']:
 t=(A/n).read_text().replace('boot720-fatpage838','boot720-rootchain839').replace('838','839').replace('boot720839-source002','boot720839-source001')
 if n=='physical.py':t=t.replace("['fatpage002'","['root001','fatpage002'").replace('isolated FATX metadata page fix839 with cache diagnostic','isolated FATX root-chain fix839 with cache diagnostic')
 (K/n).write_text(t)
base=json.loads((A/'baseline001.json').read_text());audit=json.loads((A/'audit001.json').read_text());assert audit['completed'] and all(v['matches_baseline'] for v in audit['critical'].values())
base['scope']='Installed baseline unchanged after838; immutable archive support and isolated839 driver. No runtime parent.'
base['projected_console_reserve']['additional_owned_budget']+=16*1024**2;base['projected_console_reserve']['projected_remaining']-=16*1024**2
(K/'baseline001.json').write_text(json.dumps(base,indent=2)+'\n');(K/'.gitattributes').write_bytes(b'* -text\n')
print('839 fresh source prepared; FATX root chain and EOF bounds; unchanged720p')
