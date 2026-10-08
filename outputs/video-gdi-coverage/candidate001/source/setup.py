"""Create new ordinary coverage kit around the unchanged qualified RAM0109 DLL."""
from pathlib import Path
import shutil,json
k=Path(__file__).resolve().parent;old=k.parent/'video-ram-ownership'
assert json.loads((old/'evidence-verification.json').read_text())['passed']
for n in ['display','tests']:shutil.copytree(old/n,k/n)
for n in ['0109-ram-ownership.patch','patch-review.json','build-report.json','source-verification.json','host-tests.json','ownership-tests.json','lifecycle-tests.json','tests-body.c','ownership-tests.c','lifecycle-tests.c']:
 shutil.copyfile(old/n,k/n)
(k/'candidate001/artifacts').mkdir(parents=True);(k/'artifacts').mkdir()
shutil.copyfile(old/'candidate001/artifacts/xwnown.dll',k/'candidate001/artifacts/xwnown.dll');shutil.copyfile(old/'candidate001/build.json',k/'candidate001/build.json')
for n in ['atomic_json.py','audit.py','configuration.py','cold-map.py','preflight.py','Run.ps1','supervise.py','record-closure.py','prepare.py','review.py','Build-Probe.ps1']:
 s=(old/n).read_text().replace('video-ram-ownership','video-gdi-coverage').replace('nt5-vown-','nt5-vgdi-').replace('xwnown116','xwngdi118')
 if n=='Build-Probe.ps1':s=s.replace('-ladvapi32','-ladvapi32 -lmsimg32')
 if n=='prepare.py':
  s=s.replace("case in ['control001','candidate001']","case in ['candidate001']")
  s=s.replace("for path in ['winnt/system32/xwnown.dll'","for path in ['xwngdi118/ref%02d.rgb'%i for i in range(26)]+['winnt/system32/xwnown.dll'")
 if n=='audit.py':
  needle="    for row in fixture['payloads']:"
  s=s.replace(needle,"""    for index in range(26):
        path='xwngdi118/ref%02d.rgb'%index;data=optional(path)
        if data is not None:(art/('ref%02d.rgb'%index)).write_bytes(data)
        expected=next((v['reference_hash'] for v in r['protocol_details'].get('cases',[]) if v['index']==index),None)
        matched=data is not None and len(data)==384*256*4 and fnv(data)==expected
        r['files'].append(dict(path=path,sha256=None if data is None else m.sha(data),matched=matched))
"""+needle)
  s=s.replace("r['limits']='Matched RAM0108", "r['limits']='Real-GDI DIB-reference coverage, unchanged RAM0109. Matched RAM0108")
 (k/n).write_text(s,newline='\n')
s=(old/'common.py').read_text();s=s[:s.index('\ndef validate_log')]
(k/'common.py').write_text(s+'\n'+(k/'protocol.py').read_text(),newline='\n')

p=k/'common.py';p.write_text(p.read_text()+"\nPROTECTED += [('F','winnt/system32/msimg32.dll')]\n",newline='\n')
p=k/'prepare.py';s=p.read_text();needle=" rr=readers(io,source)"
assert needle in s
s=s.replace(needle,needle+"\n for dll,digest in next(v for v in review['files'] if v['name']=='probe.exe')['targets'].items():\n  assert m.sha(rr['F'].read('winnt/system32/'+dll))==digest,('Guest API dependency differs',dll)")
p.write_text(s,newline='\n')
