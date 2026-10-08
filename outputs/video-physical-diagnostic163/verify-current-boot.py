"""Compare functional display compatibility without qualifying the known dump error."""
import struct,sys
from common import *
dest=k/'diagnostic-review.json';assert not dest.exists();out=k/'candidate001'
a=read(out/'audit.json');control=read(k.parent/'video-physical-rehearsal162/control001/audit.json')
before=(out/'artifacts/before-video-trace.bin').read_bytes();after=(out/'artifacts/video-trace.bin').read_bytes()
assert len(before)==len(after)==4096 and before[:16]==after[:16]==b'XWN-VID-TRACE01\n'
n,d=struct.unpack_from('<II',before,16);count,dropped=struct.unpack_from('<II',after,16)
assert 1<=count<=254 and dropped==d==0
assert struct.unpack_from('<I',after,32)[0]==1
assert not any(struct.unpack_from('<I',before,32+i*16)[0] in [0x30,0x31,0x32] for i in range(n))
delta=[list(struct.unpack_from('<4I',after,32+i*16)) for i in range(count)]
shared=[v for v in delta if v[0] in [0x30,0x31,0x32]];acquire=[v for v in shared if v[0]==0x30]
shared_ok=bool(acquire) and all(v[1]==0 and v[2]>=0x80000000 and v[2]%4096==0 and v[3]==0x3c00000 for v in acquire) and all(v[1]==0 for v in shared)
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
h=hivex.Hivex(str(out/'artifacts/after-system'))
paths=read(k.parent/'video-physical-review159/binding-edit.json')['changes'];bindings=[]
for v in paths:
    node=h.root()
    for part in v['path'].split('\\'):node=h.node_get_child(node,part);assert node
    value=h.node_get_value(node,v['name']);typ,data=h.value_value(value)
    bindings.append(dict(path=v['path'],type=typ,hex=data.hex(),matched=typ==v['type'] and data.hex()==v['after_hex']))
fields=['source','event_id','type','strings','data_hex']
same_errors=len(a['warnings_errors'])==len(control['warnings_errors']) and all(all(x[f]==y[f] for f in fields) for x,y in zip(a['warnings_errors'],control['warnings_errors']))
r=dict(display_compatibility_passed=a['workload_passed'] and a['integrity_passed'] and shared_ok and all(v['matched'] for v in bindings) and a['actual_caps']==control['actual_caps'],
    strict_qualification_passed=a['strict_qualification_passed'],physical_qualified=False,deployment_ready=False,
    same_baseline_error_signature=same_errors,current_boot_trace_records=len(delta),trace_restarts_per_boot=True,dropped=dropped,shared_events=shared,shared_acquire_observed=shared_ok,
    bindings=bindings,actual_caps=a['actual_caps'],warnings_errors=a['warnings_errors'],
    limits='Ordinary emulator diagnostic on captured physical core/hives. Guest live pixel checks, trace acquire and bindings observed; no exhaustive module/PTE proof. Same dump warning is retained as strict failure, not waived. No physical performance, release promotion or new-mode qualification.')
r['trace_reset_source_sha256']=sha(k.parent/'video-trace-reuse/0093-video-reuse-existing-trace.patch')
r['prior_failed_verifier_sha256']=sha(k/'verify-diagnostic.py')
save(dest,r);print(json.dumps(r,indent=2))
