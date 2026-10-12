"""Close one consumed attempt from cold records; never launches or repeats audits."""
import hashlib,json,sys
from pathlib import Path
import proof
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ('control001','candidate001')
out=k/case;root=Path('E:/xwn282')/case;dest=out/'final-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(out/'trace.json');c=read(out/'host-closure.json');audit=read(out/'audit.json');delta=read(out/'disk-delta.json');prepared=read(out/'prepared.json')
assert c['closed'] and c['host_exit']==0 and not c['fallback_kill']
assert t['physical_mode_restored'] and not t['remaining_breakpoint'] and not t.get('cleanup_error') and not t.get('frontend_cleanup_error')
assert t['orderly_quit_sent']
for name,digest in prepared['dependencies'].items():assert sha(Path(name))==digest,name
captures={}
for stop in t['checkpoints']:
 for x in stop.get('reads',[]):
  p=Path(x['private_file']);assert sha(p)==x['sha256'];captures[str(p)]=sha(p)
for m in t['monitor']:
 if 'private_reply' in m:
  p=Path(m['private_reply']);assert sha(p)==m['sha256'];captures[str(p)]=sha(p)
for p in (root/'watch').iterdir():
 if p.is_file():captures[str(p)]=sha(p)
try:result=proof.qualify(out,root)
except BaseException as e:result=dict(scoped_unchanged_guest_reuse_passed=False,error=repr(e))
reuse=out/'reuse-proof.json';assert not reuse.exists();reuse.write_text(json.dumps(result,indent=2)+'\n')
r=dict(closed=True,case=case,scoped_unchanged_guest_reuse_passed=result['scoped_unchanged_guest_reuse_passed'],
 strict_passed=result['scoped_unchanged_guest_reuse_passed'] and audit['passed'],trace_passed=t['passed'],
 trace_error=t.get('error'),terminal_phase=t.get('terminal_phase'),original_whole_disk_equality=audit['disk_all_bytes_unchanged'],
 disk_changed_bytes=delta['changed_bytes'],file_system_bytes_inherited_unchanged=delta['all_file_system_bytes_inherited_unchanged'],
 frozen_dependencies=len(prepared['dependencies']),private_captures_verified=len(captures),private_captures=captures,
 host_exit=c['host_exit'],release_mode_requested=case.startswith('candidate'),physical_changed=False,
 ordinary_qualified=False,native_gpu_grant=False,performance_qualified=False,no_windows_shutdown_claim=True,
 actual_HalHaltRoutine_entry_traced=False,never_relaunch_recollect_or_parent=True)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:b for a,b in r.items() if a!='private_captures'},indent=2))
