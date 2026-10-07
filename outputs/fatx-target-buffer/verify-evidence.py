"""Verify selected completed debugger kits without changing capture classifications."""
import hashlib,json,subprocess,sys
from pathlib import Path
ws=Path(__file__).resolve().parents[2];sha=lambda b:hashlib.sha256(b).hexdigest();read=lambda p:json.loads(p.read_text())
assert sys.argv[1:] and set(sys.argv[1:])<=set(['fatx-target-buffer','fatx-cache-buffer','fatx-paging-buffer'])
results=[]
for kit in sys.argv[1:]:
 root=ws/'outputs'/kit;out=root/'001';t=read(out/'trace.json');a=read(out/'buffer-analysis.json')
 assert sha((root/'trace.py').read_bytes())==t['source_sha256'] and sha((root/'sites.json').read_bytes())==t['sites_sha256']
 assert sha((out/'trace.json').read_bytes())==a['trace_sha256']
 assert t['guest_resumed'] and not t['armed_breakpoints_remaining']
 assert not t.get('pending_write_count') and not t.get('pending_cache_count')
 assert a['cold_checks_passed'] and not a['physical_qualified'] and not a['ordinary_qualified']
 for name,digest in a['evidence_sha256'].items():assert sha((out/name).read_bytes())==digest
 for stage in read(out/'collection.json')['stages'].values():assert sha((out/stage['output']).read_bytes())==stage['sha256']
 count=0
 for e in t['events']:
  if not e.get('buffer_file'):continue
  data=(out/'artifacts'/e['buffer_file']).read_bytes();assert sha(data)==e['buffer_sha256'] and len(data)==e['length'];count+=1
 assert count==a['captured_buffers_verified']
 assert (ws/('work/runs/nt5-'+kit+'-001/cleanup.json')).exists()
 if kit!='fatx-target-buffer':
  sites=read(root/'sites.json');assert sha((root/'review-sites.py').read_bytes())==sites['source_sha256']
  assert sha((ws/'outputs/fatx-install-buffer/write-layouts.json').read_bytes())==sites['layouts_sha256']
 checked=[]
 for rel in subprocess.check_output(['git','ls-files','--',root.relative_to(ws).as_posix()],cwd=ws,text=True).splitlines():
  assert subprocess.check_output(['git','show',':'+rel],cwd=ws)==(ws/rel).read_bytes(),rel;checked.append(rel)
 assert checked
 results.append(dict(kit=kit,buffers_verified=count,staged_files=len(checked),physical_qualified=False))
print(json.dumps(dict(evidence_verified=True,cases=results)))
