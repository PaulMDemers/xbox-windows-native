import hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
win=lambda p:Path(p.replace('/mnt/d/','D:/'))
r=read(k/'build003.json');assert r['passed'] and r['borrowed_sources_restored']
for n,h in r['inputs'].items():assert sha(k/n)==h
for p,h in r['private_files'].items():assert sha(win(p))==h
host=read(k/'host002.json');assert host['passed'] and [v['checks'] for v in host['cases']]==[409614,409614]
for p,h in host['files'].items():assert sha(win(p))==h
root=Path('D:/xwn322/build003');a=read(root/'control-source-pins.json');b=read(root/'candidate-source-pins.json')
old=read(ws/'outputs/xemu-cpu-surface-evict/build003/candidate-source-pins.json');assert a==old
changed=[n for n in a if a[n]!=b[n]];assert set(changed)==set(r['changed_sources']) and len(changed)==4
def text(p):
    z=p.read_bytes();pe=struct.unpack_from('<I',z,60)[0];assert z[pe:pe+4]==b'PE\0\0'
    count=struct.unpack_from('<H',z,pe+6)[0];start=pe+24+struct.unpack_from('<H',z,pe+20)[0]
    for off in range(start,start+count*40,40):
        size,raw=struct.unpack_from('<II',z,off+16)
        if z[off:off+8].rstrip(b'\0')==b'.text':return hashlib.sha256(z[raw:raw+size]).hexdigest()
    raise AssertionError('No text')
control_text=text(root/'xemu-control.exe');assert control_text==text(ws/'outputs/xemu-cpu-surface-evict/build003/artifacts/xemu-candidate.exe')
for row in r['builds']:assert sha(win(row['path']))==row['sha256']
assert not set(r['warnings']['candidate'])-set(r['warnings']['control'])
result=dict(passed=True,compiled_only=True,guest_launched=False,source_count=len(a),changed_sources=changed,control_text_identical_to_original=True,control_text_sha256=control_text,host_checks=819228,warning_instances={c:len(v) for c,v in r['warnings'].items()},new_warning_messages=0,borrowed_sources_restored=True,builds=r['builds'],private_build_files_verified=len(r['private_files']),host_files_verified=len(host['files']),migration_schema_reviewed=True,migration_runtime_tested=False,physical_access=False,limits='Three read/write timing latches only. No scanout field simulation, subword qualification, guest change or physical qualification.')
assert not (k/'final-review.json').exists();(k/'final-review.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
