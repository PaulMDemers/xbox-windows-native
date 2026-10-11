"""Inspect existing complete cold directory captures, no disk open or recollection."""
import hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'directory-delta001.json';assert not dest.exists()
def inventory(path):
 raw=path.read_bytes();assert len(raw)%80==0;parents={1:''};files=set();terminal=None
 for offset in range(0,len(raw),80):
  kind,first,cluster,slot=struct.unpack_from('<4I',raw,offset);entry=raw[offset+16:offset+80]
  if kind==1:assert first in parents
  elif kind==2:
   assert first in parents and 1<=entry[0]<=42
   name=entry[2:2+entry[0]].decode('latin1');p=parents[first]+'/'+name
   if entry[1]&16:
    child=struct.unpack_from('<I',entry,44)[0];assert child not in parents;parents[child]=p
   else:assert p not in files;files.add(p)
  elif kind==5:assert offset==len(raw)-80;terminal=True
  else:raise AssertionError('Unknown capture record')
 assert terminal
 return files,dict(files=len(files),directories=len(parents),capture_sha256=hashlib.sha256(raw).hexdigest())
before,b=inventory(k/'seed001/before/artifacts/directories.bin');cases={};sets={}
for case in ['dashboard001','xbe001','freeldr001']:
 files,row=inventory(k/case/'artifacts/directories.bin');a=json.loads((k/case/'allocation.json').read_text());assert row['files']==a['files'] and row['directories']==a['directories']
 row.update(added=sorted(files-before),absent=sorted(before-files));cases[case]=row;sets[case]=files
record=dict(passed=True,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='Path inventory from existing complete directory captures; no payload durability claim.',before=b,cases=cases,entry_sample_only=sorted(sets['xbe001']-sets['dashboard001']),dashboard_sample_only=sorted(sets['dashboard001']-sets['xbe001']),loader_samples_same_paths=sets['xbe001']==sets['freeldr001'],physical_access=False,recollection=False)
dest.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
