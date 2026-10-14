"""Read-only analysis of interrupted394; no historical gate changes."""
import hashlib,json,struct,sys
from pathlib import Path
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
K=Path(__file__).resolve().parent;O=K/'candidate001';A=K/'artifacts/candidate001'
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_text())
c=read(O/'collection.json');assert c['completed'] and c['startup_restored'] and c['driver_restored']
p=A/'E/xwndemo394candidate001/cmd';a=(p/'saved.bmp').read_bytes();b=(p/'reopened.bmp').read_bytes()
expected=read(K/'package.json')['helpers'][-1];assert sha(a)==expected['sha256'] and len(a)==len(b)==expected['bytes']
first=next(i for i,(x,y) in enumerate(zip(a,b)) if x!=y)
assert b[:first]==a[:first] and not any(b[first:])
h=hivex.Hivex(str(A/'E/winnt/system32/config/system'))
def path(parts):
 n=h.root()
 for p in parts:n=h.node_get_child(n,p);assert n,p
 return n
def values(n):
 out={}
 for v in h.node_values(n):
  typ,data=h.value_value(v)
  out[h.value_key(v)]=dict(type=typ,hex=data.hex(),value=data.decode('utf-16le').rstrip('\0') if typ in [1,2] else struct.unpack('<I',data)[0] if typ==4 and len(data)==4 else None)
 return out
selection=values(path(['Select']));current=selection['Current']['value']
services=path(['ControlSet%03d'%current,'Services']);matches={}
for n in h.node_children(services):
 name=h.node_name(n)
 if any(t in name.lower() for t in ['fat','xwn']):matches[name]=values(n)
r=dict(closed=True,scope='Interrupted physical394 analysis; not a workload PASS',cmd_trace=(p/'file-trace.log').read_text().splitlines(),
 correct_saved_bmp_sha256=sha(a),unfinished_copy_sha256=sha(b),bytes_each=len(a),exact_prefix_bytes=first,zero_tail_bytes=len(b)-first,
 interpretation='Consistent with an unfinished copy. Cold evidence does not identify the blocked operation or distinguish a stall from slow/incomplete progress before reset.',
 native_api_started=c['files']['/E/xwndemo394candidate001/file-api.log'] is not None,
 supervisor_started=c['files']['/E/xwndemo394candidate001/attempt.log'] is not None,
 selected_control_set=current,storage_and_project_services=matches,
 original_startup_driver_restored=True,allocation=read(O/'allocation.json'),
 normal_shutdown_count=read(O/'audit.json')['normal_shutdown_count'],physical_candidate_qualified=False)
dest=O/'partial-analysis.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['exact_prefix_bytes','zero_tail_bytes','native_api_started','supervisor_started','selected_control_set','normal_shutdown_count']},indent=2))
for name,row in matches.items():
 if 'fat' in name.lower():print(name,json.dumps(row,indent=2))
