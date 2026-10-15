"""Read-only full clean-install extraction; never mount or boot the source."""
import hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
K = Path(__file__).resolve().parent
W = K.parents[1]
P = Path('/mnt/c/xwn405/extract004')
SOURCE = Path('/home/paul/xbox-windows-native/clean-media404-oem001/disk.qcow2')
SEVEN = '/home/paul/xbox-windows-native/toolchains/7zip/root/usr/lib/7zip/7z'
sys.path.insert(0, str(W/'tools'))
from build_space import require_space
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
assert P.exists() and (P/'disk.raw').is_file() and not (P/'files').exists() and not (K/'extraction004.json').exists()
assert sha(SOURCE) == 'ece991e4dc6b662ece2a39dddba384a3c480173cafd89086135f6bb861b7f796'
assert not any(SOURCE.parent.glob('phase*/qmp.sock'))
info = json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(SOURCE)]))
assert not info.get('backing-filename')
mapping = json.loads(subprocess.check_output(['qemu-img','map','--output=json',str(SOURCE)]))
budget = sum(r['length'] for r in mapping if r['data']) + 16*1024**2
r = dict(source_sha256=sha(SOURCE), source_is_closed=True, status='converting', physical_access=False,
         space=require_space(P, 20+budget/1024**3))
# Windows pre-created an explicitly sparse 2 GiB regular file.
def save(): (K/'extraction004.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    raw=P/'disk.raw'
    subprocess.run(['qemu-img','convert','-n','--target-is-zero','-S','4k','-O','raw',str(SOURCE),str(raw)],check=True)
    listing=subprocess.check_output([SEVEN,'l','-slt',str(raw)],text=True)
    (P/'listing.txt').write_text(listing)
    rows=[]
    for block in listing.split('\n\n'):
        row=dict(line.split(' = ',1) for line in block.splitlines() if ' = ' in line)
        if 'Path' in row and 'Size' in row and 'Folder' in row: rows.append(row)
    assert rows
    # Filesystem metadata and paging are not Windows installation payloads.
    excluded=[]; selected=[]
    for row in rows:
        name=row['Path']; first=name.replace('\\','/').split('/')[0].lower()
        if first.startswith('$') or first in ['pagefile.sys','hiberfil.sys','system volume information','recycler','[system]']:
            excluded.append(dict(path=name,reason='NTFS metadata, paging, recycle or restore state',bytes=int(row['Size'] or 0)))
        else: selected.append(row)
    total=sum(int(row['Size'] or 0) for row in selected if row['Folder']=='-')
    r.update(status='listed', listed_rows=len(rows), extraction_bytes=total, excluded=excluded)
    save()
    r['extract_space']=require_space(P,20+(total+32*1024**2)/1024**3); save()
    # List explicit paths, rather than extracting NTFS metadata or pagefile.
    names=[row['Path'] for row in selected if row['Folder']=='-']
    assert names and len(names)==len(set(n.lower() for n in names))
    (P/'paths.txt').write_text('\n'.join(names)+'\n')
    with (P/'extract.log').open('xb') as log:
        subprocess.run([SEVEN,'x','-y','-ssc-','-scsUTF-8','-o'+str(P/'files'),str(raw),'@'+str(P/'paths.txt')],check=True,stdout=log,stderr=subprocess.STDOUT)
    actual={p.relative_to(P/'files').as_posix():p for p in (P/'files').rglob('*') if p.is_file()}
    expected={row['Path'].replace('\\','/'):int(row['Size'] or 0) for row in selected if row['Folder']=='-'}
    assert set(actual)==set(expected),(len(actual),len(expected))
    files=[]; issues=[]
    for name,p in sorted(actual.items()):
        assert p.stat().st_size==expected[name]
        files.append(dict(path=name,bytes=p.stat().st_size,sha256=sha(p)))
        reasons=[]
        for component in name.split('/'):
            if not component.isascii(): reasons.append('non-ASCII component')
            if len(component.encode('utf-8'))>42: reasons.append('component exceeds 42 bytes')
            if any(c in component for c in ':*?"<>|'): reasons.append('unsupported component character')
        if reasons: issues.append(dict(path=name,reasons=sorted(set(reasons))))
    (P/'files.json').write_text(json.dumps(files,indent=2)+'\n')
    r.update(status='extracted', files=len(files), logical_bytes=sum(v['bytes'] for v in files),
             manifest_sha256=sha(P/'files.json'), fatx_name_issues=issues, source_unchanged=sha(SOURCE)==r['source_sha256'])
    assert r['source_unchanged']
    assert raw.resolve().parent==P.resolve() and raw.name=='disk.raw'
    raw.unlink(); r['temporary_raw_removed']=True; r['final_space']=require_space(P)
except BaseException as exc:
    r.update(status='failed',error=repr(exc)); raise
finally: save()
print(json.dumps({k:r[k] for k in ['status','files','logical_bytes','fatx_name_issues']}))
