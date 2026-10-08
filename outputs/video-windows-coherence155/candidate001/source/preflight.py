"""Freeze a fresh pair member and all inputs before launch; no debugger."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1]
assert case in ['control001','candidate001'];out=k/case
def read(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert not (out/'preflight.json').exists() and not (ws/('work/runs/nt5-vwin155-'+case)).exists()
f=read(k/('fixture-'+case+'.json'));r=read(k/'pe-review.json');assert r['passed'] and sha(k/'pe-review.json')==f['pe_review_sha256']
assert sha(k/'probe.c')==r['probe_source_sha256'] and sha(k/'artifacts/probe.exe')==r['probe_sha256']
assert r['display_sha256']==r['control_display_sha256']
base=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name']
seed=ws/('work/video-windows-coherence155-'+case+'-seed.qcow2')
assert sha(base)==f['fixture_sha256'] and sha(seed)==f['seed_sha256']
header=seed.read_bytes();offset,length=struct.unpack_from('>QI',header,8)
backing=header[offset:offset+length].decode('utf-8')
assert (ws/('work/runs/nt5-vwin155-'+case)/backing).resolve()==base.resolve()
for row in f['parents']:
    p=Path(row['path'].replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'));assert sha(p)==row['sha256']
assert read(out/'before-configuration.json')['expected_configuration']
for n in ['oracle-tests.json','protocol-tests.json']:
    t=read(k/n);assert t['passed']
    for name,digest in t['pins'].items():assert sha(k/name)==digest
for name,digest in read(k/'frozen-inputs.json').items():assert sha(ws/name)==digest,name
build=read(k.parent/'xemu-cpu-surface-evict/build003/build.json')
digest=next(b['sha256'] for b in build['builds'] if b['case']==case[:-3])
assert sha(k.parent/'xemu-cpu-surface-evict/build003/artifacts'/('xemu-'+case[:-3]+'.exe'))==digest
snapshot=out/'source';snapshot.mkdir(exist_ok=False);pins={}
for p in k.iterdir():
    if p.is_file() and p.suffix in ['.py','.ps1','.c','.md','.json']:
        (snapshot/p.name).write_bytes(p.read_bytes());pins[p.name]=sha(p)
(out/'preflight.json').write_text(json.dumps(dict(passed=True,physical_access=False,debugger=False,
    sources=pins,probe_sha256=r['probe_sha256'],display_sha256=r['display_sha256'],emulator_sha256=digest),indent=2)+'\n')
print('Fresh Windows probe and unchanged guest display frozen')
