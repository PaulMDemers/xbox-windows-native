"""Read-only classification of actual 405 exclusions and installed configuration."""
import hashlib, json, sys
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'))
from Registry import Registry
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
system=Path('C:/xwn405/cold006/after/system')
r=Registry.Registry(str(system)); control=r.open('Select').value('Current').value()
root='ControlSet%03d\\Control\\'%control
nls=r.open(root+'Nls\\CodePage'); cp=nls.value('OEMCP').value()
assert cp=='437'
rows=[]
source=W/'outputs/fresh-assembly405/assembly001.json'
for row in json.loads(source.read_text())['explicit_exclusions']:
    if 'FATX component limitation' not in row['reason']:continue
    parts=[]
    for s in row['path'].split('/'):
        try:
            b=s.encode('cp437'); assert b.decode('cp437')==s
            parts.append(dict(component=s,encoded_bytes=len(b),representable=len(b)<=42,hex=b.hex()))
        except UnicodeError:parts.append(dict(component=s,representable=False,encoding_failure=True))
    rows.append(dict(path=row['path'],bytes=row['bytes'],sha256=row['sha256'],
                     cp437_representable=all(p['representable'] for p in parts),components=parts))
assert len(rows)==8 and sum(v['cp437_representable'] for v in rows)==2
out=dict(source_sha256=sha(source),system_sha256=sha(system),current_control_set=control,oemcp=cp,
         exclusions=rows,crash_control={v.name():v.value() for v in r.open(root+'CrashControl').values()},
         paging_files=r.open(root+'Session Manager\\Memory Management').value('PagingFiles').value(),
         physical_access=False,long_name_support_implemented=False,
         scope='Actual hive/path inspection; CP437 eligibility is not a native runtime roundtrip')
with (K/'inspection001.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({k:out[k] for k in ['oemcp','long_name_support_implemented','paging_files']}))
