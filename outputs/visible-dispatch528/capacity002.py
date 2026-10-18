"""Losslessly compress one newly selected closed524 executable; no backing files."""
import importlib.util,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('allocation_inspection',K.parent/'portable-compression523/common002.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
P=Path('C:/xwn524/instances/windows-native-extent524-emu001/EA3473314E6C0EA0/xemu-windows-native-extent524-emu001.exe')
R=Path('C:/xwn524/runs/nt5-extent524-emu001')
records=[K.parent/'extent-runtime524/final-review.json',R/'instance.json',R/'host-exit.json',R/'cleanup.json']
f,i,e,c=[m.js(p) for p in records]
assert f['passed'] and f['all_owned_processes_closed'] and e['closed'] and e['exit_code']==0 and not e['fallback_kill'] and not e['timeout'] and c['completedUtc'] and not c['retained']
assert Path(i['executable'])==P and P.resolve()==P.absolute()
for p in [P,*P.parents]:assert not p.lstat().st_file_attributes&0x400
if sys.argv[1]=='plan':
 out=K/'capacity-plan002.json';assert not out.exists()
 before=m.metadata(P);assert before['links']==1 and before['allocated_bytes']==191320064
 assert before['sha256']==i['sourceSha256'].lower()==f['private_files'][str(P)]
 out.write_text(json.dumps(dict(path=str(P),before=before,records={str(p.resolve()):m.sha(p) for p in records},processes=m.processes(),volume=m.volume(),scope='one closed524 nonbacking private executable; not any523 selected file',helper_sha256=m.sha(K.parent/'portable-compression523/common002.py')),indent=2)+'\n',encoding='utf-8')
 print('PLAN exact closed524 single-link executable',before['allocated_bytes'])
elif sys.argv[1]=='apply':
 out=K/'capacity-apply002.json';assert not out.exists();plan=m.js(K/'capacity-plan002.json')
 assert plan['path']==str(P) and m.metadata(P)==plan['before'];m.processes()
 for n,h in plan['records'].items():assert m.sha(Path(n))==h
 result=subprocess.run([str(m.COMPACT),'/C','/EXE:LZX',str(P)],capture_output=True,text=True,timeout=60)
 after=m.metadata(P)
 for key in ['bytes','links','file_id','device','sha256']:assert after[key]==plan['before'][key],key
 assert result.returncode==0 and after['allocated_bytes']<plan['before']['allocated_bytes']
 out.write_text(json.dumps(dict(passed=True,before=plan['before'],after=after,output=result.stdout,error=result.stderr,exit_code=result.returncode,saved_allocated_bytes=plan['before']['allocated_bytes']-after['allocated_bytes'],all_bytes_paths_identity_preserved=True,no_backing_changes=True),indent=2)+'\n',encoding='utf-8')
 print('PASS lossless new524 compression saved',plan['before']['allocated_bytes']-after['allocated_bytes'])
else:raise ValueError('plan/apply')
