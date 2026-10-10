"""Fresh ordinary case for cumulative0209, preserving the failed candidate002."""
import hashlib,json,pathlib
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
def write(n,s):
    p=k/n;assert not p.exists();p.write_text(s)
write('prepare-fixture003.py',(k/'prepare-fixture002.py').read_text().replace('candidate002','candidate003').replace('xwnaud207c','xwnaud207d').replace('artifacts/build002','artifacts/build003'))
for a,b in [('supervise003.py','supervise004.py'),('audit003.py','audit004.py'),('typed-state003.py','typed-state004.py'),('Run003.ps1','Run004.ps1'),('Wait-Run003.ps1','Wait-Run004.ps1'),('Audit003.ps1','Audit004.ps1')]:
    s=(k/a).read_text().replace('candidate002','candidate003').replace('typed-state003.py','typed-state004.py').replace('frozen003.json','frozen004.json').replace('Run003.ps1','Run004.ps1').replace('audit003.py','audit004.py')
    write(b,s)
write('Prepare-Candidate003.ps1',(k/'Prepare-Candidate002.ps1').read_text().replace('candidate002','candidate003').replace('Candidate002','Candidate003').replace('prepare-fixture002.py','prepare-fixture003.py'))
write('review-build003.py',(k/'review-build002.py').read_text().replace('artifacts/build002','artifacts/build003').replace('build-review002.json','build-review003.json'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=repo.parent/'work/reactos001/drivers/wdm/audio/drivers/ac97'
r=json.loads((k/'source-build002.json').read_text());current={p.name:sha(p) for p in source.iterdir() if p.is_file()}
changed=sorted(n for n in current if current[n]!=r['sources'][n]);assert changed==['adapter.cpp','mintopo.cpp']
r.update(patch='0209-render-connections-cumulative.patch',patch_sha256=sha(k/'0209-render-connections-cumulative.patch'),sources=current,driver_sha256=sha(k/'artifacts/build003/ac97xnt5.sys'),normal_ac97_sha256=sha(k/'artifacts/build003/ac97.sys'),changed_since002=changed,note='Cumulative0209 replaces0208/0207; both targets compiled. Prior stream/common source hashes unchanged. Six targeted host connection cases passed in tests004; tests003 extractor failed before test compilation.')
write('source-build003.json',json.dumps(r,indent=2)+'\n')
