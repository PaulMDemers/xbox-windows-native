"""Versioned harness for build002 stereo topology, preserving every earlier case."""
import hashlib,json,pathlib
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
def write(name,s):
    p=k/name;assert not p.exists();p.write_text(s)
s=(k/'prepare-fixture.py').read_text().replace("['control001','candidate001']","['candidate002']").replace("'xwnaud207a' if case=='control001' else 'xwnaud207b'","'xwnaud207c'").replace("case=='candidate001'","case=='candidate002'").replace('artifacts/build001','artifacts/build002')
write('prepare-fixture002.py',s)
for a,b in [('supervise002.py','supervise003.py'),('audit002.py','audit003.py'),('typed-state002.py','typed-state003.py')]:
    s=(k/a).read_text().replace("['control002','candidate001']","['candidate002']").replace("k/'typed-state002.py'","k/'typed-state003.py'").replace("k/'frozen002.json'","k/'frozen003.json'")
    write(b,s)
s=(k/'Run002.ps1').read_text().replace("'control002','candidate001'","'candidate002'").replace('frozen002.json','frozen003.json')
write('Run003.ps1',s)
for a,b in [('Wait-Run002.ps1','Wait-Run003.ps1'),('Audit002.ps1','Audit003.ps1')]:
    s=(k/a).read_text().replace("'control002','candidate001'","'candidate002'").replace('Run002.ps1','Run003.ps1').replace('audit002.py','audit003.py')
    write(b,s)
s=(k/'review-build.py').read_text().replace('artifacts/build001','artifacts/build002').replace("k/'build-review.json'","k/'build-review002.json'")
write('review-build002.py',s)
source=repo.parent/'work/reactos001/drivers/wdm/audio/drivers/ac97';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((k/'source-build001.json').read_text());r.update(patch_sha256=sha(k/'0208-fixed-codec-cumulative.patch'),patch='0208-fixed-codec-cumulative.patch',sources={p.name:sha(p) for p in source.iterdir() if p.is_file()},driver_sha256=sha(k/'artifacts/build002/ac97xnt5.sys'),normal_ac97_sha256=sha(k/'artifacts/build002/ac97.sys'),note='Cumulative patch relative to0016, replaces0207; both targets compiled, normal target compile-only')
write('source-build002.json',json.dumps(r,indent=2)+'\n')
print('Created candidate002 harness sources and exact source/build pins')
