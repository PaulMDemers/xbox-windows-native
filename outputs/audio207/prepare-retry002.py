"""Fresh control case after host-only PIL import failure; keep frozen001 intact."""
import hashlib,json,pathlib,shutil
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=json.loads((k/'frozen.json').read_text())
assert all(sha(repo/n)==h for n,h in pins.items())
old=k/'control001';out=k/'control002';out.mkdir(exist_ok=False)
assert json.loads((old/'closure.json').read_text())['closed']
assert not json.loads((old/'host-abort.json').read_text())['windows_launch_requested']
f=json.loads((old/'fixture.json').read_text());assert sha(pathlib.Path(f['fixture_path_windows']))==f['fixture_sha256']
f.update(case='control002',reuses_immutable_source_of='control001',reason='New private runtime disk from unchanged cold source; prior instance failed before Windows launch')
(out/'fixture.json').write_text(json.dumps(f,indent=2)+'\n')
(out/'artifacts').mkdir()
for p in (old/'artifacts').glob('before-*'):
    if p.name in ['before-system','before-software','before-default','before-sam','before-security']:
        shutil.copyfile(p,out/'artifacts'/p.name)
shutil.copytree(old/'before',out/'before')
for a,b in [('supervise.py','supervise002.py'),('audit.py','audit002.py'),('typed-state.py','typed-state002.py')]:
    s=(k/a).read_text();assert s.count("['control001','candidate001']")==1
    s=s.replace("['control001','candidate001']","['control002','candidate001']")
    if a=='audit.py':s=s.replace("k/'typed-state.py'","k/'typed-state002.py'").replace("k/'frozen.json'","k/'frozen002.json'")
    assert not (k/b).exists();(k/b).write_text(s)
s=(k/'Run.ps1').read_text().replace("'control001','candidate001'","'control002','candidate001'").replace('frozen.json','frozen002.json')
anchor="$out=Join-Path $PSScriptRoot $Case\n"
preflight="""$env:PYTHONPATH='C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages'
$deps=Get-Content (Join-Path $PSScriptRoot host-dependencies002.json) -Raw | ConvertFrom-Json
foreach($p in $deps.PSObject.Properties){if((Get-FileHash $p.Name).Hash.ToLowerInvariant() -ne $p.Value){throw 'Host Pillow dependency changed'}}
& python -c "from PIL import Image; import PIL._imaging"
if($LASTEXITCODE){throw 'Host image dependency preflight failed before guest creation'}
"""
assert s.count(anchor)==1;s=s.replace(anchor,anchor+preflight)
(k/'Run002.ps1').write_text(s)
pil=pathlib.Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages/PIL')
deps={str(p):sha(p) for p in pil.iterdir() if p.suffix in ['.py','.pyd','.dll']}
assert deps;(k/'host-dependencies002.json').write_text(json.dumps(deps,indent=2)+'\n')
for name in ['Run002.ps1','supervise002.py','audit002.py','typed-state002.py','host-dependencies002.json','control002/fixture.json','candidate001/fixture.json']:
    pins[str((k/name).relative_to(repo)).replace('\\','/')]=sha(k/name)
(k/'frozen002.json').write_text(json.dumps(pins,indent=2)+'\n')
print('Prepared new control002 identity and preflighted host dependency pins; no guest launched')
