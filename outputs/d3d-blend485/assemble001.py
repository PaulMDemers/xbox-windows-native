"""Fresh alpha hardware kit using the reviewed 483 diagnostic implementation."""
from pathlib import Path
import re
K=Path(__file__).resolve().parent;old=K.parent/'handoff-witness483'
sample_sha='edf7b7c796cd1ca1ba44a6c2cbbbab14007be003e7239cd2c92df65389927c12'
names=['build001.py','binary-review001.py','runner-build001.py','host001.py','test-wrapper.c','witness.S','decode.py','witness_decode.py','legacy_refusal_decode.py','failure_marker.py','transport001.py','controller-host001.py','physical.py','imports001.py','package001.py','review001.py','module-read001.py','actual-witness001.py','archive-inputs001.py','closeout001.py','process-closeout001.py']
for name in names:
    p=K/name;assert not p.exists()
    s=(old/name).read_text().replace('483','485')
    s=re.sub(r'(?<![0-9])480(?![0-9])','484',s)
    for a,b in [('d3d-depth484','d3d-blend484'),('graphics_depth','graphics_blend'),('ladder/depth','ladder/blend'),('scoped_depth_passed','scoped_blend_passed'),('depth_cases','blend_cases'),('actual_depth_controls','actual_blend_controls'),('r08bd','r08cd'),('r08bs','r08cs'),('00f6487c474420a2b84d60381d2915621c047e33eb2c3b27adc2c2ecd99c9d2f',sample_sha)]:
        s=s.replace(a,b)
    if name=='physical.py':s=s.replace('len(listing)<=16','len(listing)<=18')
    if name=='controller-host001.py':
        s=s.replace("'changed-candidate']:","'changed-candidate','capacity18','capacity19']:")
        s=s.replace("['success','timeout']","['success','timeout','capacity18','capacity19']")
        s=s.replace("case in ['success','timeout']","case in ['success','timeout','capacity18','capacity19']")
        a=s.index("  m.collect();r=")
        b=s.index("  assert all(state[n]",a)
        s=s[:a]+'''  if case.startswith('capacity'):
   for j in range(int(case[8:])):state[m.RESULT+f'/result{j}.txt']=b'modeled'
  if case=='capacity19':
   try:m.collect()
   except AssertionError:pass
   else:raise AssertionError('oversize result directory accepted')
   assert m.HOOK not in state
   assert not json.loads((m.K/'physical001-collection.json').read_text())['completed']
   cases.append(dict(case=case,admitted=ok,collection_refused=True,hook_removed=True,calls=calls));continue
  m.collect();r=json.loads((m.K/'physical001-collection.json').read_text());assert r['hook_removed'] and m.HOOK not in state and state[m.KITROOT+'/startup-used.cmd']==m.hook()
  if case=='capacity18':assert len(r['result_directory'])==18 and all(m.RESULT+f'/result{j}.txt' in r['files'] for j in range(18))
'''+s[b:]
        s=s.replace('PASS 10 actual dispatcher cases','PASS 12 actual dispatcher cases')
    p.write_text(s,encoding='utf-8',newline='\n')
p=K/'runner.c';assert not p.exists()
s=(K.parent/'d3d-blend484/runner.c').read_text().replace('484','485').replace('Owned NT5 PC fixture only','Owned physical Xbox Windows fixture only')
s=s.replace('A:'+chr(92)*2+'D3D.EXE','C:'+chr(92)*2+'xwn485-kit'+chr(92)*2+'d3d.exe')
p.write_text(s,encoding='utf-8',newline='\n')
p=K/'actual-controls001.py';assert not p.exists()
s=(K.parent/'d3d-blend484/actual-controls001.py').read_text().replace("c=json.loads((K/'ntfs-cold1-002.json').read_text());p=Path(c['private_path'])/'files/xwn484';rows=[]","c=json.loads((K/'physical001-collection.json').read_text());p=Path(c['files']['/E/xwn485/runner.txt']['path']).parent;rows=[]")
assert 'ntfs-cold' not in s;p.write_text(s,encoding='utf-8',newline='\n')
print('New 485 sources only; no build, deployment or launch.')
