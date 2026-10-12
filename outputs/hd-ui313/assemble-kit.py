from pathlib import Path
import json
k=Path(__file__).resolve().parent;p=k.parent/'hd-boot312'
for name in ['Prepare.ps1','Run.ps1','Invoke.ps1','supervise.py','audit.py','typed-state.py','installed-binding.py','analyze-capture.py','review-combined.py','freeze.py','close-host.py']:
    text=(p/name).read_text().replace('hd-boot312','hd-ui313').replace('xwn312','xwn313').replace('hd312','hd313').replace('XWN312','XWN313')
    if name=='freeze.py':text=text.replace("k/'control001/fixture.json',",'')
    (k/name).write_text(text,newline='\n')
s=(p/'prepare.py').read_text().replace('xwn312','xwn313')
s=s.replace("assert case in ('control001','candidate001')","assert case=='candidate001'")
s=s.replace("hd-regression304/candidate001/fixture.json","hd-boot312/candidate001/fixture.json")
start=s.index("review=json.loads(");end=s.index("files=dict(parent",start)
s=s[:start]+'''review=json.loads((K/'build-review001.json').read_text());assert review['passed']
build=pathlib.Path('/mnt/d/xwn313/build001')
mapping={'F/'+parent['namespace']+'/wizard.exe':'wizard.exe'}
assert sha(build/'wizard.exe')==review['binary_sha256']
'''+s[end:]
s=s.replace('Matched311 loader on unused304 candidate preparation; same303 software bounds/300 nine-MiB chain/audio004/FATX0101. Control720x480 versus candidate1280x720. No physical/1080i qualification','Only313 emulator opt-in wizard helper differs from unused312 candidate preparation. Same311720p/303/300/audio004/FATX0101; no physical/1080i qualification')
s=s.replace('with one matched launcher override','with one emulator-only helper override')
(k/'prepare.py').write_text(s,newline='\n')
(k/'profile.json').write_text(json.dumps(dict(expected={'candidate001':[1280,720,5120]},scope='Unchanged311720p loader; only emulator wizard helper changed',parent='never-executed312 candidate preparation'),indent=2)+'\n')
# Retain provider lookup/import-forwarder validation from201, only expected source/API delta.
s=(k.parent/'setup-wizard-automation201/review-build006.py').read_text()
s=s.replace("k/'build-review006.json'","k/'build-review001.json'").replace("k/'artifacts/build006/wizard.exe'","Path('D:/xwn313/build001/wizard.exe')")
s=s.replace("'SetForegroundWindow',",'').replace("k/'wizard006.c'","k/'wizard313.c'")
s=s.replace(" and 'SetForegroundWindow' not in source",'')
s=s.replace("r=dict(passed=True", "assert 'SetForegroundWindow' in names\nassert 'AttachThreadInput' not in names\nassert sha(k/'policy.h')==sha(k.parent/'setup-wizard-automation201/policy.h')\nassert source.replace('#include \\\"activation.inc\\\"\\n','').replace('    activate313(h,w.tid);\\n','')==(k.parent/'setup-wizard-automation201/wizard006.c').read_text()\nr=dict(passed=True")
s=s.replace('No focus or foreground mutation and one action per held owner. Runtime GUI-state observation unverified.','One emulator-only SetForegroundWindow attempt per held PID/creation,8owner bound; unchanged actual Cancel guard. New adapter Win32 calls host modeled; runtime still unverified.')
s=s.replace('Observe or explicit verified Cancel BN_CLICKED notification only.','Observe or explicit verified Cancel BM_CLICK; new compiled emulator-only activation opt-in.')
(k/'review-build.py').write_text(s,newline='\n')
