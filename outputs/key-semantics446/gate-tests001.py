"""Exercise the actual dispatch gate with owned temporary files and fake Popen."""
import copy
import json
from pathlib import Path
import tempfile
import time
import launch_gate as g

K = Path(__file__).resolve().parent
out = K/'gate-tests001.json'
assert not out.exists()
rows = []
with tempfile.TemporaryDirectory(prefix='xwn446-gate-') as tmp:
    root = Path(tmp).resolve()
    kit, fixture = root/'kit', root/'fixture'
    kit.mkdir(); fixture.mkdir()
    for p in (kit/'run001.py', kit/'launch_gate.py', fixture/'disk.qcow2',
              fixture/'probe.img', root/'parent.qcow2', root/'runtime'):
        p.write_bytes(b'owned test bytes: '+p.name.encode())
    prep = dict(path=str(fixture), guest_launched=False, source=str(root/'parent.qcow2'),
                source_sha256=g.sha(root/'parent.qcow2'), child_sha256=g.sha(fixture/'disk.qcow2'),
                floppy_sha256=g.sha(fixture/'probe.img'), inputs={'run001.py':g.sha(kit/'run001.py')},
                runtime_pins={str(root/'runtime'):g.sha(root/'runtime')})
    cold = dict(complete=True, audit_unchanged=True, source_unchanged=True, disk_sha256=prep['child_sha256'])
    for name, data in [('ntfs-preparation001.json', prep), ('ntfs-cold0-002.json', cold)]:
        (kit/name).write_text(json.dumps(data), encoding='utf-8')
    originals = {p:p.read_bytes() for p in root.rglob('*') if p.is_file()}
    receipt, claim = kit/'preflight001.json', kit/'launch-admission001.json'
    valid = dict(schema=1, attempt='446-test', fixture=str(fixture), completed=True, passed=True,
                 finished_ns=time.time_ns(), files={str(p):g.sha(p) for p in originals if p.parent==kit or p.name=='runtime'},
                 fixture_files={str(fixture/'disk.qcow2'):prep['child_sha256'],
                                str(fixture/'probe.img'):prep['floppy_sha256'],
                                prep['source']:prep['source_sha256']})
    calls = []
    def fake(command, **kwargs):
        calls.append(command)
        return 'process-model'
    def reset(record):
        for p, raw in originals.items(): p.write_bytes(raw)
        if claim.exists(): claim.unlink()
        receipt.write_text(json.dumps(record), encoding='utf-8')
    def reject(name, record, change=None):
        reset(record)
        if change: change()
        before = len(calls)
        try: g.launch(receipt, kit, fixture, '446-test', ['owned-model'], popen=fake)
        except (ValueError, OSError, KeyError, TypeError): pass
        else: raise AssertionError('Accepted '+name)
        assert len(calls)==before, name
        rows.append(name)
    reject('missing', valid, receipt.unlink)
    for raw in (b'', b'{', b'{"schema":1,"schema":1}', b'x'*(1024*1024+1)):
        reject('invalid-transport-'+str(len(raw)), valid, lambda raw=raw:receipt.write_bytes(raw))
    for key in valid:
        r=copy.deepcopy(valid); del r[key]; reject('missing-'+key, r)
    for key, values in {'schema':[True,0,2,'1'], 'completed':[False,1,'true',None],
                        'passed':[False,1,'true',None], 'attempt':['old',''],
                        'fixture':[str(root),''], 'finished_ns':[True,0,time.time_ns()+10**12],
                        'files':[{},[]], 'fixture_files':[{},[]]}.items():
        for value in values:
            r=copy.deepcopy(valid); r[key]=value; reject(key+'='+str(value),r)
    r=copy.deepcopy(valid);r['extra']=1;reject('unknown-field',r)
    for p in originals:
        reject('changed-'+p.name, valid, lambda p=p:p.write_bytes(b'changed'))
    for p in list(valid['files']):
        r=copy.deepcopy(valid); del r['files'][p]; reject('missing-pin-'+Path(p).name,r)
    # A newly pinned false/incomplete preparation or baseline must still refuse.
    for filename, key, value in [('ntfs-preparation001.json','guest_launched',True),
                                  ('ntfs-preparation001.json','path',str(root)),
                                  ('ntfs-cold0-002.json','complete',1),
                                  ('ntfs-cold0-002.json','audit_unchanged',False),
                                  ('ntfs-cold0-002.json','source_unchanged',False),
                                  ('ntfs-cold0-002.json','disk_sha256','0'*64)]:
        r=copy.deepcopy(valid); p=kit/filename
        data=json.loads(originals[p]);data[key]=value
        raw=json.dumps(data).encode();r['files'][str(p)]=g.hashlib.sha256(raw).hexdigest()
        reject(filename+'-'+key,r,lambda p=p,raw=raw:p.write_bytes(raw))
    reset(valid)
    assert g.launch(receipt,kit,fixture,'446-test',['owned-model'],popen=fake)=='process-model'
    assert len(calls)==1 and claim.exists()
    try:g.launch(receipt,kit,fixture,'446-test',['owned-model'],popen=fake)
    except FileExistsError:pass
    else:raise AssertionError('Repeated launch')
    assert len(calls)==1
    rows.append('second-dispatch')
    reset(valid)
    def failed(command, **kwargs):raise OSError('modeled spawn failure')
    try:g.launch(receipt,kit,fixture,'446-test',['owned-model'],popen=failed)
    except OSError:pass
    assert claim.exists()
    try:g.launch(receipt,kit,fixture,'446-test',['owned-model'],popen=fake)
    except FileExistsError:pass
    else:raise AssertionError('Retry spawn failure')
    assert len(calls)==1
    rows.append('failed-spawn-consumed')
    receipt.unlink()
    g.publish(receipt,valid)
    assert g.read(receipt)==valid
    before=receipt.read_bytes()
    try:g.publish(receipt,dict(valid,passed=False))
    except FileExistsError:pass
    else:raise AssertionError('Overwrite receipt')
    assert receipt.read_bytes()==before
    rows.append('exclusive-publication')
record=dict(passed=True, rejected=rows, fake_popen_successes=len(calls), actual_guest_launches=0,
            gate_sha256=g.sha(K/'launch_gate.py'), test_sha256=g.sha(Path(__file__)))
out.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(len(rows),'refusals; one modeled successful dispatch; zero real processes')
