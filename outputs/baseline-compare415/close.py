"""Verify immutable comparison captures and record the read-only closeout."""
import collections
import datetime
import hashlib
import json
from pathlib import Path

K=Path(__file__).resolve().parent
W=K.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
p=read(K/'physical001.json');f=read(K/'fresh001.json')
assert p['completed'] and p['baseline_code_and_startup_exact']
assert not p['physical_writes'] and not p['launch_requested'] and not p['console_C_accessed']
assert f['completed'] and f['source_unchanged'] and not f['guest_launched']
private={}
for remote,row in p['files'].items():
    path=Path('E:/xwn415/demo')/remote[3:]
    assert sha(path)==row['sha256']
    private[str(path)]=sha(path)
for row in f['files'].values():
    path=Path(row['local_path'].replace('/mnt/e/','E:/'))
    assert sha(path)==row['sha256']
    private[str(path)]=sha(path)
c=read(K/'comparison001.json')
counts=dict(collections.Counter(v['classification'] for v in c['comparison']))
assert counts=={'Byte-identical':16,'PE timestamps/checksum only':6,
               'Nonmetadata binary differences':3,'Configuration/state difference':3,
               'Absent from fresh installation':2,'Display date and section digest only':1}
assert read(K/'classifier-tests001.json')['checks']==74
for side in ['demo','fresh']:
    r=read(K/'registry001.json')['snapshots'][side]
    assert sha(Path('E:/xwn415')/side/'winnt/system32/config/system')==r['hive_sha256']
inputs={str(v.relative_to(W)):sha(v) for v in K.iterdir() if v.is_file()}
for name in ['outputs/demo-ready411/verification001.json',
             'outputs/install-validation406/emu001/audit.json',
             'outputs/fresh-assembly405/installed-final001.json',
             'outputs/release-readiness403/hal-correspondence003.json']:
    inputs[name]=sha(W/name)
result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            readonly_comparison_complete=True,classification_counts=counts,
            physical_files=len(p['files']),fresh_files=len(f['files']),
            private_captures=private,analysis_inputs=inputs,
            classifier_checks=74,physical_writes=False,console_C_accessed=False,
            new_builds=0,new_guest_launches=0,launch_cause_identified=False,
            intermittency_established=False,full_binary_equivalence_proved=False,
            physical_demo_unchanged=True,public_release_ready=False,
            no_processes_started_remain=True)
with (K/'final-review.json').open('x',encoding='utf-8') as out:
    json.dump(result,out,indent=2);out.write('\n')
print(json.dumps(dict(captures=len(private),analysis_inputs=len(inputs),checks=74)))
