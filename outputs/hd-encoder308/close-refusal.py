"""Preserve already downloaded refusal evidence; no relaunch or log re-collection."""
import hashlib,json,sys,re
from pathlib import Path
k=Path(__file__).resolve().parent
sys.path.insert(0,str(k.parent/'demo-audio-level256'));import common001 as c
sys.path.insert(0,str(k.parent/'surface-bridge260'));from atomic_json import write_json
p=k/'physical001/trial.json';r=c.read(p);assert r['launch_requested'] and not r.get('collected')
log=k/'physical001/hd308.txt';kernel=Path('D:/xwn308/physical001/kernel308.bin');data=log.read_bytes();lines=data.decode('ascii').splitlines()
assert lines[-1]=='COMPLETE error=35 log_ok=1 mode_changes=2'
assert [int(re.search(r'stage=(\d+)',s)[1]) for s in lines if s.startswith('MODE ')]==[1,3]
assert len([s for s in lines if s.startswith('ENC ')])==56
zero=[s for s in lines if s.startswith('ENC ') and 'index=6c ' in s];assert len(zero)==4 and all(s.endswith('status=00000000 value=00000000') for s in zero)
with c.connect(timeout=8) as f:
 r['fixed_after']=c.check_fixed(f);r['after']={path:c.sha(c.get(f,path)) for path in r['before']};r['startup_and_five_hives_unchanged']=r['before']==r['after']
 r['xbe_after_sha256']=c.sha(c.get(f,r['remote']+'/default.xbe'))
assert r['startup_and_five_hives_unchanged'] and r['xbe_after_sha256']==r['xbe_readback_sha256']
r.update(collected=True,dashboard_returned=True,return_utc=c.utc(),inventory_completed=False,qualification_passed=False,native_error=35,mode_changes=2,completed_stages=[1,3],log_bytes=len(data),log_sha256=c.sha(data),private_kernel=dict(path=str(kernel),bytes=kernel.stat().st_size,sha256=c.sha(kernel.read_bytes())),collection_method='Prior collection downloaded both artifacts, then original strict decoder correctly rejected incomplete modes. This closure only reads local evidence and rechecks installed baseline; no log re-download or relaunch.',original_decoder_failure='Expected three modes; actual diagnostic refused after720p and recovered640x480. Status0/value0 for6c in both passes/stages.',encoder_gate_waived=False)
write_json(p,r);print({n:r[n] for n in ['collected','qualification_passed','native_error','startup_and_five_hives_unchanged']})
