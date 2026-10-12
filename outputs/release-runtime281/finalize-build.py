"""Hash all completed build/host evidence, without running any consumed test."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'final-review.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();files={}
review=json.loads((k/'source-review.json').read_text());assert review['passed']
for name,h in review['files'].items():assert sha(Path(name))==h;files[name]=h
for label,capsule in [('edges-host001','runtime281-edges001'),('edges-host002','runtime281-edges002'),
 ('interface-host001','runtime281-interface001'),('interface-host002','runtime281-interface002'),('wrappers-host001','runtime281-wrappers001')]:
 r=json.loads((k/(label+'.json')).read_text());assert r['passed']==(label!='interface-host001')
 base=Path('E:/Codex-archive/xbox-windows-native')/capsule
 for name,h in r['files'].items():p=base/name;assert sha(p)==h;files[str(p)]=h
build=json.loads((k/'renderer-build001.json').read_text())
assert all(sha(k/n)==h for n,h in build['inputs'].items())
assert all(sha(k.parent/'release-worker280'/n)==h for n,h in build['worker_inputs'].items())
exe=Path('E:/Codex-archive/xbox-windows-native/runtime281-build001/xemu-runtime281.exe');assert sha(exe)==build['executable_sha256'];files[str(exe)]=sha(exe)
r=dict(passed=True,build_closed=True,all_host_sessions_closed=True,guest_in_this_kit=False,
 runtime_kit='outputs/release-pair282; consult its actual records',compiled_sha256=sha(exe),
 private_files_verified=len(files),files=files,original_build_sources_unchanged=True,physical_changed=False,
 host_only_tests=True,runtime_release_claim=False,performance_claim=False,native_gpu_grant=False)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:v for a,v in r.items() if a!='files'},indent=2))
