"""Preserve collected evidence and leave the diagnostic trace ready for one boot; never launch."""
import importlib.util
import json
import os
import ftplib
from pathlib import Path

k=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('trial',k/'trial.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=json.loads((k/'trial.json').read_text())
assert r.get('collected_utc') and not r['startup_enabled'] and r['bounded_gdi_passed']
out=k/'next-boot.json';assert not out.exists(), 'Do not repeat recorded preparation'
previous=(m.art/'after-video-trace.bin').read_bytes()
assert m.sha(previous)==r['collected']['video-trace.bin']['sha256']
assert len(previous)==4096 and previous[:16]==m.trace_seed[:16]
with ftplib.FTP() as f:
    f.connect(os.environ['XWN_FTP_HOST'],timeout=20)
    f.login(os.environ['XWN_FTP_USER'],os.environ['XWN_FTP_PASSWORD'])
    expected=json.loads((m.ws/'outputs/native-windows-physical-f/physical-cache-preflight.json').read_text())['ownership_marker']
    assert json.loads(m.get(f,'/F/xwn-deploy-v1.json'))==expected
    assert all(m.verify(f).values())
    assert m.sha(m.get(f,m.startup))==m.release['startup_sha256']
    assert m.get(f,m.trace)==previous, 'Trace changed after collection'
    result=dict(requested_utc=m.utc(),preserved_trace_sha256=m.sha(previous),launches=0,ready=False)
    out.write_text(json.dumps(result,indent=2)+'\n')
    m.put(f,m.trace,m.trace_seed)
    result.update(ready=True,verified_utc=m.utc(),seed_sha256=m.sha(m.trace_seed),
                  limit='Ready for one manual boot only; installed diagnostic driver still requires a fresh seed each boot.')
    out.write_text(json.dumps(result,indent=2)+'\n')
print('Collected trace preserved; clean diagnostic seed verified; no launch issued')
