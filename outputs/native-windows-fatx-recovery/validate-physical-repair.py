"""Check the independent post-repair snapshot against the exact offline rehearsal."""
import hashlib,json,pathlib,struct,subprocess,sys
k=pathlib.Path(__file__).resolve().parent;pre=k.parent/'native-windows-fatx-preflight';post=k/'artifacts/postscan';expected=k/'artifacts/rehearsal'
assert json.loads((k/'physical-repair.json').read_text())['completed'] and json.loads((k/'physical-postscan.json').read_text())['completed']
assert (post/'fat-metadata.bin').read_bytes()==(expected/'fat-metadata.bin').read_bytes()
def records(path):
 b=path.read_bytes();assert len(b)%80==0;r={}
 for at in range(0,len(b),80):
  typ,head,c,off=struct.unpack_from('<4I',b,at)
  key=(typ,head,c,off)
  if typ==2:key=(typ,head,c,off)
  assert key not in r;r[key]=b[at:at+80]
 return r
assert records(post/'directories.bin')==records(expected/'directories.bin'),'Unexpected directory difference'
subprocess.run([sys.executable,str(pre/'analyze.py'),'--capture',str(post),'--output',str(k/'physical-post-allocation.json')],check=True)
audit=json.loads((k/'physical-post-allocation.json').read_text());assert audit['allocation_consistent']
r=dict(scope=__doc__,exact_directory_entries_match_rehearsal=True,fat_unchanged=True,allocation_consistent=True,errors=len(audit['errors']),orphans=audit['orphan_cluster_count'],passed=True,windows_boot_ready=False)
(k/'physical-repair-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
