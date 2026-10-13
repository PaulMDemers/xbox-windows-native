"""Prepare an isolated local E payload from the current console capture. No FTP API."""
import argparse,hashlib,json,shutil,struct,sys,zipfile
from pathlib import Path
W=Path(__file__).resolve().parents[1];K=W/'outputs/stock-physical337'
p=argparse.ArgumentParser(description='Prepare the reviewed private stock-E1080 profile from owned337 capture; no FTP or boot API.')
p.add_argument('--profile',choices=['stock-e-1080i'],required=True)
p.add_argument('--capture-root',type=Path,required=True)
p.add_argument('--hd-archive',type=Path,required=True)
p.add_argument('--boot-root',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--receipt',type=Path,required=True)
a=p.parse_args();P=a.output;dest=a.receipt
assert P.is_absolute() and P.parent.is_dir() and dest.parent.is_dir()
assert not P.is_symlink() and not P.exists() and not dest.exists()
assert not P.exists() and not dest.exists()
assert shutil.disk_usage(P.parent).free-2*1024**3>20*1024**3
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
capture=read(K/'capture001.json');review=read(K/'capture-review001.json');assert capture['complete'] and review['passed']
source=a.capture_root;archive=a.hd_archive
assert sha(archive.read_bytes())=='474957aa6d2eb4cd8c3818a26ad0568e4b9c104b8159891c065b1491c8f6930d'
build=read(K.parent/'stock-boot334/build001.json');assert read(K.parent/'stock-boot334/binary-review003.json')['passed']
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
sys.path.insert(0,str(K.parent/'native-windows-nt5-kernel'));from nt5_hive_indexes import normalize
P.mkdir(parents=True);r=dict(prepared=False,physical_writes=False,console_c_accessed=False,files={},changes={},directories=[],capture_sha256=sha((K/'capture001.json').read_bytes()),archive_sha256=sha(archive.read_bytes()),startup_normal=True,private=str(P))
def save():dest.write_text(json.dumps(r,indent=2)+'\n')
save()
def semantic(h):
    todo=[('',h.root())];d={}
    while todo:
        path,node=todo.pop()
        for v in h.node_values(node):
            typ,data=h.value_value(v);d[path+'|'+h.value_key(v)]=(typ,data.hex())
        todo.extend((path+'\\'+h.node_name(c),c) for c in h.node_children(node))
    return d
try:
    for remote,meta in capture['files'].items():
        data=(source/remote.lstrip('/')).read_bytes();assert sha(data)==meta['sha256'] and len(data)==meta['bytes']
        if remote.startswith('/F/'):
            assert remote.split('/')[2].lower() in ['winnt','documents and settings','program files'];target='/E/'+remote[3:]
        else:
            assert remote.startswith('/E/Applications/XWNFBoot/');target=remote.replace('/XWNFBoot/','/XWNEBoot/')
        local=P/target.lstrip('/');local.parent.mkdir(parents=True,exist_ok=True);local.write_bytes(data);r['files'][target]=dict(bytes=len(data),sha256=sha(data))
    for remote in capture['directories']:
        target='/E/'+remote[3:];(P/target.lstrip('/')).mkdir(parents=True,exist_ok=True);r['directories'].append(target)
    def replace(remote,data,reason):
        local=P/remote.lstrip('/');old=local.read_bytes();local.write_bytes(data)
        r['changes'][remote]=dict(before_sha256=sha(old),after_sha256=sha(data),reason=reason);r['files'][remote]=dict(bytes=len(data),sha256=sha(data))
    system=P/'E/winnt/system32/config/system';h=hivex.Hivex(str(system),write=True);before=semantic(h);node=h.node_get_child(h.root(),'MountedDevices');assert node
    e=struct.pack('<IQ',0xaa55,5633024*512);f=struct.pack('<IQ',0xaa55,15633072*512);changed={}
    for key,typ,data in [(h.value_key(v),*h.value_value(v)) for v in h.node_values(node)]:
        if data in (e,f):
            new=f if data==e else e;h.node_set_value(node,dict(key=key,t=typ,value=new));changed[key]=dict(before=data.hex(),after=new.hex())
    assert len(changed)==4 and changed['\\DosDevices\\C:']['after']==e.hex() and changed['\\DosDevices\\D:']['after']==f.hex()
    patched=P/'system-patched';h.commit(str(patched));del h
    fixed,conversion=normalize(patched.read_bytes());patched.write_bytes(fixed);h=hivex.Hivex(str(patched));after=semantic(h);del h
    delta={n:dict(before=before.get(n),after=after.get(n)) for n in before.keys()|after.keys() if before.get(n)!=after.get(n)}
    assert len(delta)==4 and all(n.startswith('\\MountedDevices|') and n.split('|')[1] in changed for n in delta)
    replace('/E/winnt/system32/config/system',fixed,'Four E/F volume identities only; all other registry values unchanged')
    r['hive_semantic_changes']=delta;r['hive_normalization']=conversion
    with zipfile.ZipFile(archive) as z:
        manifest=json.loads(z.read('MANIFEST.json'))['files']
        for old in ['/F/winnt/system32/xwnown.dll','/F/winnt/system32/drivers/xboxvnt5.sys','/E/Applications/XWNFBoot/loader/xboxbvid.dll']:
            name='1080i'+old;data=z.read(name);assert dict(bytes=len(data),sha256=sha(data))==manifest[name]
            target='/E/'+old[3:] if old.startswith('/F/') else old.replace('/XWNFBoot/','/XWNEBoot/')
            replace(target,data,'Immutable 0.2.0 1080i payload')
    for name in ['default.xbe','freeldr.sys','rosload.exe']:
        data=(a.boot_root/name).read_bytes();assert sha(data)==build['outputs'][name]['sha256']
        replace('/E/Applications/XWNEBoot/'+name,data,'334 isolated stock E boot chain')
    for path,meta in r['files'].items():assert sha((P/path.lstrip('/')).read_bytes())==meta['sha256']
    startup='/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd'
    assert r['files'][startup]['sha256']==review['startup_sha256']
    assert len(r['changes'])==7
    r.update(prepared=True,file_count=len(r['files']),logical_bytes=sum(v['bytes'] for v in r['files'].values()),paging_files=review['paging_files'],profile=a.profile,limits='Private same-console F-to-E migration inputs only. No generic Windows-media installer or deployment. Physical342 scopes pass but combined/strict event gates FAIL. F rollback and Xbox C untouched.')
except BaseException as exc:r['error']=repr(exc);raise
finally:save()
print('Prepared and rehashed isolated E payload',r['file_count'],'files; normal startup retained')
