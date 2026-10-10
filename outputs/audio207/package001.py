"""Assemble a coordinator-only package after real installation and persistent playback pass."""
import hashlib,json,pathlib,shutil,zipfile
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for case,field in [('candidate004','scoped_audio_passed'),('install001','scoped_installation_passed'),('installed001','scoped_audio_passed'),('installed002','scoped_audio_passed')]:
    assert json.loads((k/case/'audit.json').read_text())[field]
    assert json.loads((k/case/'closure.json').read_text())['closed']
for n,h in json.loads((k/'frozen-installed002.json').read_text()).items():assert sha(repo/n)==h,n
assert json.loads((k/'hardware-runner-review001.json').read_text())['passed']
assert json.loads((k/'hardware-runner-source-review001.json').read_text())['passed']
source=repo.parent/'work/reactos001'
pins=json.loads((k/'source-build004.json').read_text())
assert all(sha(source/'drivers/wdm/audio/drivers/ac97'/n)==h for n,h in pins['sources'].items())
root=k/'artifacts/hardware-package001';root.mkdir(exist_ok=False)
payload=root/'payload';payload.mkdir();sources=root/'corresponding-source';sources.mkdir()
def copy(src,dest):
    dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(src,dest)
    assert sha(src)==sha(dest),('Copy readback mismatch',src,dest)
wizard=pathlib.Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/setup-wizard-automation201/artifacts/build006/wizard.exe')
assert sha(wizard)=='b3a42114e2d083d3d124cb54199a8d6c3fd63fee5a9ef6b196e4599d28b84fbb'
for dest,src in {
    'install/runner.exe':k/'artifacts/hardwarehelpers001/physical-install-runner.exe',
    'install/install.exe':k/'artifacts/install001/install.exe',
    'install/xwnaci207.inf':k/'xwnaci207.inf',
    'install/xwnaci207.sys':k/'artifacts/build004/ac97xnt5.sys',
    'install/wizard.exe':wizard,
    'verify/runner.exe':k/'artifacts/hardwarehelpers001/physical-playback-runner.exe',
    'verify/state.exe':k/'artifacts/state001/state.exe',
    'verify/probe.exe':k/'artifacts/state001/probe-installed.exe',
    'verify/wizard.exe':wizard,
}.items():copy(src,payload/dest)
for n in ['PHYSICAL-TRIAL.md','SOURCE-REBUILD.md','source-build004.json','toolchain-observed001.json','build-review004.json','install-review002.json','state-review001.json','hardware-runner-review001.json','hardware-runner-source-review001.json']:
    copy(k/n,payload/n)
for case in ['candidate004','install001','installed001','installed002']:
    for n in ['audit.json','closure.json']:copy(k/case/n,payload/'evidence'/case/n)
licenses={'Microsoft-AC97-MIT.txt':source/'drivers/wdm/audio/drivers/ac97/license.txt'}
for n in ['COPYING','COPYING.LIB','COPYING3','COPYING3.LIB']:licenses[n+'.txt']=source/n
for n,p in licenses.items():copy(p,payload/'licenses'/n)
archive=k/'artifacts/corresponding-source001/reactos0016.tar.gz';assert archive.is_file()
assert sha(archive)=='0855bd035eda24d9c41fe020a7a129edfea8380cc8f4c94ba2f0972e63a1f8d4'
assert json.loads((k/'source-archive-review001.json').read_text())['passed']
copy(archive,sources/archive.name)
for n in ['0210-waveonly-cumulative.patch','SOURCE-REBUILD.md','source-build004.json','toolchain-observed001.json','Build-Install.ps1','Build-State.ps1','Build-HardwareRunners001.ps1','build-driver.sh']:
    copy(k/n,sources/n)
for n in ['extract-install-providers.py','extract-state-provider.py']:
    copy(k/n,sources/'outputs/audio207'/n)
for n in ['install.c','install-runner.c','state.c','probe-installed.c','installed-runner.c','physical-install-runner.c','physical-playback-runner.c']:
    copy(k/n,sources/'outputs/audio207'/n)
for p in (k.parent/'setup-wizard-automation201').glob('*.h'):copy(p,sources/'outputs/setup-wizard-automation201'/p.name)
copy(k.parent/'setup-wizard-automation201/wizard006.c',sources/'outputs/setup-wizard-automation201/wizard006.c')
readme='''# Experimental Xbox ACI package207

Prepared for a coordinator-controlled first physical trial. Do not deploy merely
because this package exists. Read PHYSICAL-TRIAL.md and create the fresh rollback
bundle before staging. This chat has performed no physical access or deployment.

The exact-ID native driver supports the experimental analog stereo PCM path for
ACI10DE:01B1. Separate APU01B0 remains unsupported. Digital-output/HDMI adapters,
hardware mixer controls, capture and protected-content playback are unqualified.

Ordinary xemu playback, genuine Windows SetupAPI installation and two subsequent
installed-driver playback boots passed with normal restarts and cold integrity.
The subsequent boots verified one started xwnaci207 device/module, no loaded legacy
module and one WinMM render device. Strict whole-boot qualification still FAILS
on Ftdisk49. Known unrelated wizard cancellation was recorded; this is not an
integrated prompt-free boot. Physical codec behavior and audibility remain untested.

Use separate unused guest directories for install/ and verify/. Each contains a
physical-mode runner.exe and its exact sibling files. The installer is not run
again for the subsequent playback boot. Neither runner is a generic dialog
clicker or a forced-restart helper. All executable and document hashes appear in
MANIFEST.json. The INF's pretest draft comment is preserved in the exact tested
bytes; this README and manifest record the completed validation. Source and build
inputs are in audio207-corresponding-source.zip;
retain it and the component licenses with the binary package.
'''
(payload/'README.md').write_text(readme)
def manifest(folder,extra):
    r=dict(extra);r['files']={str(p.relative_to(folder)).replace(chr(92),'/'):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(folder.rglob('*')) if p.is_file()}
    (folder/'MANIFEST.json').write_text(json.dumps(r,indent=2)+'\n');return r
source_manifest=manifest(sources,dict(base_tree=pins['base_tree'],upstream_commit=pins['base_commit'],patch='0210-waveonly-cumulative.patch'))
payload_manifest=manifest(payload,dict(coordinator_trial_ready=True,physical_qualified=False,strict_whole_boot_passed=False,apu_supported=False,driver_sha256=pins['driver_sha256'],scope='Experimental native ACI analog stereo PCM; emulator-qualified installation and subsequent playback only',source_archive_sha256=sha(archive)))
zips=[]
for folder,name in [(payload,'audio207-aci-experimental.zip'),(sources,'audio207-corresponding-source.zip')]:
    dest=root/name
    with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(folder.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(folder)).replace(chr(92),'/'),compress_type=zipfile.ZIP_STORED if p.name.endswith('.tar.gz') else zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(dest) as z:assert z.testzip() is None
    zips.append(dest)
deliver=pathlib.Path('C:/Users/Paul/Documents/Codex/2026-10-09/xbox-windows2000-audio/outputs')
required=sum(p.stat().st_size for p in zips)+128*1024**2
assert shutil.disk_usage('C:/').free-required>=20*1024**3,'Projected C reserve guard for deliverables'
deliver.mkdir(exist_ok=True)
for p in zips:copy(p,deliver/p.name)
report=dict(coordinator_trial_ready=True,physical_qualified=False,source_tree=pins['base_tree'],driver_sha256=pins['driver_sha256'],packages=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p),delivered_path=str(deliver/p.name)) for p in zips],validation_cases=['candidate004','install001','installed001','installed002'],strict_whole_boot_passed=False,physical_access=False)
dest=k/'package001.json';assert not dest.exists();dest.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
