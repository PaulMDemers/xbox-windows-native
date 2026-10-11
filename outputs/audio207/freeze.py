"""Freeze inputs for the two lifecycle-only ordinary emulator cases."""
import hashlib,json,pathlib
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (k/'frozen.json').exists()
names=['Run.ps1','supervise.py','probe.c','runner.c','audit.py','typed-state.py','analyze-capture.py','prepare-fixture.py','0207-aci-lifecycle.patch','build-review.json','host-tests002.json','capture-tests001.json','artifacts/build001/ac97xnt5.sys','artifacts/probe001/probe.exe','artifacts/probe001/runner.exe']
paths=[k/n for n in names+['Invoke-Audio.ps1']]
paths += [repo/'outputs'/n for n in ['setup-wizard-automation201/restart_gate201.h','setup-wizard-automation201/setup_gate201.h','setup-wizard-automation201/restore.py','video-surface-history/Invoke-Exclusive.ps1','native-windows-prebuild/monitor_capture.py','native-windows-prebuild/launch_unleashx.py','gpu-reset-banner152/ftp_deadline.py','video-text-oracle206/common.py','fatx-mapped-eof/coldio.py','fatx-mapped-eof/allocation.py','native-windows-paint-save/prepare-fixture.py']]
(k/'frozen.json').write_text(json.dumps({str(p.relative_to(repo)).replace('\\','/'):sha(p) for p in paths},indent=2)+'\n')
source=repo.parent/'work/reactos001/drivers/wdm/audio/drivers/ac97'
r=dict(base_commit='afc0127e8f937ab68503d715d948844973756aa1',base_manifest='outputs/native-windows-nt5-kernel/patch-check-0016.json',base_tree='5c302cf16ce08e7f2748be580e3d2e60d7d2441b',patch_sha256=sha(k/'0207-aci-lifecycle.patch'),sources={p.name:sha(p) for p in source.iterdir() if p.is_file()},driver_sha256=sha(k/'artifacts/build001/ac97xnt5.sys'),build_directory=str(repo.parent/'work/build001'),compiler='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc',physical_access=False)
(k/'source-build001.json').write_text(json.dumps(r,indent=2)+'\n')
