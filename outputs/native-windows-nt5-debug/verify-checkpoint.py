"""Verify saved package integrity and consistency; does not rerun guest tests."""
import hashlib, json, pathlib
out=pathlib.Path(__file__).resolve().parent
def read(name):return json.loads((out/name).read_text())
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
manifest=read('manifest.json')
for name,record in manifest['files'].items():
    p=out/name
    assert p.stat().st_size==record['bytes'],name
    assert sha(p)==record['sha256'],name
hal=sha(out/'artifacts/halxboxnt5.dll')
count=0
for name in ['binary-unit-tests.json','boundary-tests.json','kdport-tests.json']:
    report=read(name)
    assert report['hal_sha256']==hal,name
    assert all(t['passed'] for t in report['tests']),name
    count+=len(report['tests'])
assert count==30,count
audit=read('installed-kernel-binding-audit.json')
assert audit['runtime_approved'] is False
assert audit['records']['hal.dll']['sha256']==hal
assert audit['records']['bootvid.dll']['sha256']==sha(out/'artifacts/xboxbvid.dll')
assert all(not c.get('missing') and c.get('resolved',True) for c in audit['checks'])
layout=read('boot-layout-comparison.json')
for target,count in [('hal',49),('loader',45)]:
    checks=layout['targets'][target]['checks']
    assert len(checks)==count and all(c['matches'] for c in checks)
iso=read('artifacts/volume-read-boundaries.json')
assert iso['iso_sha256']==sha(out/'artifacts/volume-read-boundaries.iso')
for file,name in [('freeldr.sys','/LOADER/FREELDR.SYS;1'),('rosload.exe','/LOADER/ROSLOAD.EXE;1')]:
    assert sha(out/'artifacts'/file)==iso['files'][name]
checkpoint=read('checkpoint.json')
assert checkpoint['windows_kernel_entered'] is False
for run in checkpoint['runs']:
    evidence=out/'evidence'/run['id']
    assert not json.loads((evidence/'cleanup.json').read_text())['retained']
    assert not json.loads((evidence/'disk-retention.json').read_text())['retained']
    if run['final_probe']:
        inputs=json.loads((evidence/'input-hashes.json').read_text())
        assert any(p['Hash'].lower()==iso['iso_sha256'] for p in inputs)
assert read('patch-check.json')['complete_chain_matches_working_tree']
print('PASS: package hashes, 30 HAL test groups, import bindings, 94 selected offsets, final ISO inputs and cleanup records. Guest outcomes use recorded visual observations; Windows kernel entry remains untested.')
