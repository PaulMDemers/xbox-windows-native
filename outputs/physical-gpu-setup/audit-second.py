"""Read-only full binary/nine-hive audit after the second physical GPU setup boot."""
import argparse,json,pathlib,struct,subprocess,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent/"fatx0101-physical"))
from physical import k,ws,connect,owner,get,save,sha,utc,startup,baseline,expected,driver,candidate_sha
k=pathlib.Path(__file__).resolve().parent/'002'
p=argparse.ArgumentParser();p.add_argument('--resume',action='store_true');a=p.parse_args()
trial=json.loads((k/'physical.json').read_text());assert trial.get('collected_utc') and not trial['automatic_restart']
manifest=json.loads((ws/'outputs/native-windows-physical-f/package-manifest.json').read_text())['files']
extensions={'.exe','.dll','.sys','.nls','.fon','.ttf','.cpl','.ocx'}
items=[v for v in manifest if v['path'].startswith('F/') and pathlib.PurePosixPath(v['path']).suffix.lower() in extensions]
overrides={p.lower():h for p,h in expected.items()};overrides[driver.lower()]=candidate_sha
record=k/'binary-audit.json'
r=dict(scope=__doc__,started_utc=utc(),checked=0,expected_count=len(items),bytes=0,mismatches=[],hives=[],complete=False)
if a.resume:r=json.loads(record.read_text());assert not r['complete'] and r['expected_count']==len(items);r.pop('error',None)
else:assert not record.exists()
try:
    with connect() as f:
        owner(f);assert sha(get(f,startup))==baseline['startup_sha256']
        for v in items[r['checked']:]:
            path='/'+v['path'];data=get(f,path);h=overrides.get(path.lower(),v['sha256'])
            if sha(data)!=h:r['mismatches'].append(dict(path=path,expected=h,actual=sha(data)))
            r['checked']+=1;r['bytes']+=len(data)
            if r['checked']%100==0:save(r,record);print(r['checked'],'checked;',len(r['mismatches']),'mismatches',flush=True)
        hives={'F/winnt/system32/config/'+n for n in ['system','software','sam','security','default']}
        hives.update(v['path'] for v in manifest if v['path'].startswith('F/') and pathlib.PurePosixPath(v['path']).name.lower() in ['ntuser.dat','usrclass.dat'])
        folder=k/'artifacts/hives';folder.mkdir(parents=True,exist_ok=True)
        for name in sorted(hives):
            if any(v['path']==name for v in r['hives']):continue
            data=get(f,'/'+name);assert len(data)>=4096 and data[:4]==b'regf';assert struct.unpack_from('<I',data,4)==struct.unpack_from('<I',data,8)
            checksum=0
            for value in struct.unpack_from('<127I',data):checksum^=value
            checksum=0xfffffffe if checksum==0xffffffff else checksum or 1;assert checksum==struct.unpack_from('<I',data,508)[0]
            path=folder/name.replace('/','__')
            if path.exists():assert path.read_bytes()==data
            else:path.write_bytes(data)
            linux='/mnt/c/'+path.resolve().as_posix()[3:]
            command=['wsl','-d','Ubuntu','--','env','LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu','python3','/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-fatx-paging/audit-hive.py',linux]
            tree=json.loads(subprocess.check_output(command));r['hives'].append(dict(path=name,bytes=len(data),sha256=sha(data),matching_sequences=True,checksum_valid=True,tree=tree));save(r,record)
        r.update(complete=True,passed=not r['mismatches'],completed_utc=utc());save(r,record)
except Exception as exc:r['error']=repr(exc);save(r,record);raise
print('Binary/hive audit complete:',r['checked'],len(r['hives']),r['passed'])
