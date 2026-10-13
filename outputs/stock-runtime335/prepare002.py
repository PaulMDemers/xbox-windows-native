"""Fresh private 10GB stock-layout disk; no physical access or extended F partition."""
import hashlib,json,os,shutil,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/e/xwn335/seed002');out=K/'seed002'
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not P.exists() and not out.exists()
assert shutil.disk_usage('/mnt/c').free-256*1024**2>20*1024**3 and shutil.disk_usage('/mnt/e').free-12*1024**3>20*1024**3
sys.path.insert(0,str(K.parent/'video-text-oracle206'));from common import ColdIO,m,sha,HIVES,hive,STARTUP
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
sys.path.insert(0,str(K.parent/'native-windows-nt5-kernel'));from nt5_hive_indexes import normalize
parent=Path('/mnt/e/xwn329/seed001/source.qcow2');blank=Path('/mnt/c/Emulators/xemu/system/xbox_hdd.qcow2')
f=json.loads((K.parent/'artifact-recovery329/seed001/fixture.json').read_text());assert sha(parent)==f['fixture_sha256']
build=json.loads((K.parent/'stock-boot334/build001.json').read_text());assert build['status']=='compiled'
assert json.loads((K.parent/'stock-boot334/binary-review003.json').read_text())['passed']
P.mkdir(parents=True);out.mkdir();raw=P/'stock10gb.raw';target=P/'source.qcow2'
r=dict(prepared=False,physical_access=False,parent_sha256=sha(parent),blank_sha256=sha(blank),bytes=10000000000,extended_partition_table=False,files=[],changes={})
def save():(out/'fixture.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    subprocess.run(['qemu-img','convert','-O','raw',str(blank),str(raw)],check=True)
    with raw.open('r+b') as dst,ColdIO(parent) as src:
        dst.truncate(r['bytes']);dst.seek(0);assert dst.read(512)==bytes(512)
        # Dashboard is seeded entirely from an owned never-executed emulator fixture.
        # This writes a private host image, not the physical Xbox C partition.
        start=4609024*512;size=1024000*512;digest=hashlib.sha256()
        for off in range(0,size,8*1024*1024):
            n=min(8*1024*1024,size-off);src.seek(start+off);b=src.read(n);digest.update(b);dst.seek(start+off);dst.write(b)
        dst.flush();dst.seek(start);after=hashlib.sha256()
        for off in range(0,size,8*1024*1024):after.update(dst.read(min(8*1024*1024,size-off)))
        assert after.digest()==digest.digest();r['private_dashboard_partition_sha256']=digest.hexdigest()
        m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
        m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
        re=m.Writer(src,m.fatx.open_partition(src,parent,'E'));rf=m.Writer(src,m.fatx.open_partition(src,parent,'F'))
        writer=m.Writer(dst,m.fatx.open_partition(dst,raw,'E'))
        # Change only equivalent volume identities; retain all C:\ absolute paths.
        original=rf.read('winnt/system32/config/system');before=P/'system-before';before.write_bytes(original)
        patched=P/'system-after';patched.write_bytes(original)
        def semantic(h):
            todo=[('',h.root())];d={}
            while todo:
                path,node=todo.pop()
                for v in h.node_values(node):d[path+'|'+h.value_key(v)]=(h.value_type(v) if hasattr(h,'value_type') else h.value_value(v)[0],h.value_value(v)[1].hex())
                for ch in h.node_children(node):todo.append((path+'\\'+h.node_name(ch),ch))
            return d
        h=hivex.Hivex(str(patched),write=True);before_values=semantic(h);node=h.node_get_child(h.root(),'MountedDevices');assert node
        e=struct.pack('<IQ',0xaa55,5633024*512);fmap=struct.pack('<IQ',0xaa55,15633072*512);changed={}
        for v in h.node_values(node):
            key=h.value_key(v);typ,data=h.value_value(v)
            if data in (e,fmap):
                new=fmap if data==e else e;h.node_set_value(node,dict(key=key,t=typ,value=new));changed[key]=dict(before=data.hex(),after=new.hex())
        assert changed['\\DosDevices\\C:']['after']==e.hex() and changed['\\DosDevices\\D:']['after']==fmap.hex()
        h.commit(str(patched));del h
        fixed,conversion=normalize(patched.read_bytes());patched.write_bytes(fixed)
        h=hivex.Hivex(str(patched));after_values=semantic(h);del h
        delta={key:dict(before=before_values.get(key),after=after_values.get(key)) for key in before_values.keys()|after_values.keys() if before_values.get(key)!=after_values.get(key)}
        assert len(delta)==len(changed) and all(key.startswith('\\MountedDevices|') and key.split('|')[1] in changed for key in delta)
        r['mounted_devices_changes']=changed;r['hive_semantic_changes']=delta;r['hive_normalization']=conversion
        def copydir(reader,first,sourcepath,targetpath,overrides):
            if targetpath:writer.mkdir(targetpath)
            if not first:return
            for name,(_,_,entry) in reader.directory(first)['entries'].items():
                sp='/'.join(x for x in [sourcepath,name] if x);tp='/'.join(x for x in [targetpath,name] if x);cluster=int.from_bytes(entry[44:48],'little')
                if entry[1]&16:copydir(reader,cluster,sp,tp,overrides)
                else:
                    data=overrides.get(sp.lower())
                    if data is None:data=reader.read(sp)
                    row=writer.write(tp,data);r['files'].append(row)
                    if len(r['files'])%1000==0:print('Copied',len(r['files']),flush=True)
        # Entire original Windows F file tree, including pagefile and prepared runner.
        copydir(rf,1,'','',{'winnt/system32/config/system':fixed})
        at=1
        for name in ['applications','xwnfboot']:at=int.from_bytes(re.directory(at)['entries'][name][2][44:48],'little')
        boot={}
        for name in ['default.xbe','freeldr.sys','rosload.exe']:
            b=(Path('/mnt/e/xwn334/build001')/name).read_bytes();assert m.sha(b)==build['outputs'][name]['sha256'];boot['applications/xwnfboot/'+name]=b
        copydir(re,at,'applications/xwnfboot','Applications/XWNEBoot',boot)
        writer.flush();dst.flush();cold=m.Writer(dst,m.fatx.open_partition(dst,raw,'E'))
        for item in r['files']:assert m.sha(cold.read(item['path']))==item['sha256'],item['path']
        assert cold.read(STARTUP)==rf.read(STARTUP)
        r['cold_readback_files']=len(r['files']);r['logical_file_bytes']=sum(x['bytes'] for x in r['files'])
        r['free_e_bytes']=sum(x==0 for x in cold.fat[1:cold.limit])*cold.p.cluster_size
        r['hives']=[hive(patched if n=='system' else P/('hive-'+n)) if n=='system' else {} for n in ['system']]
        for name in HIVES[1:]:
            path=P/('hive-'+name);path.write_bytes(cold.read('winnt/system32/config/'+name));r['hives'].append(hive(path))
        dst.seek(0);assert dst.read(512)==bytes(512)
        # No FATX header at the extended partition's former starting offset.
        dst.seek(15633072*512);assert dst.read(4)!=b'FATX'
    subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(raw),str(target)],check=True)
    subprocess.run(['qemu-img','compare','-f','raw','-F','qcow2',str(raw),str(target)],check=True)
    check=subprocess.run(['qemu-img','check','--output=json',str(target)],capture_output=True,text=True,check=True)
    assert sha(parent)==r['parent_sha256'] and sha(blank)==r['blank_sha256']
    r.update(prepared=True,fixture_path_linux=str(target),fixture_path_windows='E:'+str(target)[6:],fixture_sha256=sha(target),qcow_check=json.loads(check.stdout),sources_unchanged=True)
except BaseException as e:r['error']=repr(e);raise
finally:save()
print('Stock 10GB source prepared and all files readback verified',flush=True)
