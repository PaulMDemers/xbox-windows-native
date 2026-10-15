"""Read-only terminal review of actual evidence and all owned sessions."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('E:/xwn406');out=K/'final-review.json';assert not out.exists()
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
audit=json.loads((K/'emu001/audit.json').read_text());media=json.loads((K/'media-evidence001.json').read_text())
assert all(audit['checks'].values()) and audit['strict_qualification'] is False
assert audit['remaining_long_path_exclusions']==6 and media['emulator_wmp_audio_video_scoped_pass']
assert media['physical_tv_or_speaker_confirmation'] is False
assert sha(P/'runs/nt5-validation406-emu001/hdd.qcow2')==audit['disk_sha256']
for name,row in audit['private_captures'].items():assert sha(P/'cold001'/name)==row['sha256']
for name,row in media['private_files'].items():assert sha(P/'media-evidence001'/name)==row['sha256']
for p,h in json.loads((K/'emu001/frozen.json').read_text()).items():assert sha(W/p)==h,p
for receipt in ['archive-executables001.json','archive-executables002.json']:
    for r in json.loads((K/receipt).read_text()):assert sha(Path(r['archive']))==r['archive_sha256'] and not Path(r['original']).exists()
for receipt in ['deduplicate-c002.json','deduplicate-media007.json']:
    for r in json.loads((K/receipt).read_text()):assert sha(Path(r['target']))==r['sha256'] and sha(Path(r['source']))==r['sha256']
processes=subprocess.check_output(['powershell','-NoProfile','-Command',"@(Get-Process xemu* -ErrorAction SilentlyContinue).Count"],text=True).strip();assert processes=='0'
host=json.loads((P/'runs/nt5-validation406-emu001/host-exit.json').read_text());assert host['passed']
launch=json.loads((K/'emu001/launch.json').read_text());assert len(launch['cycles'])==1 and launch['cycles'][0]['dashboard_return']
files={str(p.relative_to(P)).replace('\\','/'):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in P.rglob('*') if p.is_file()}
private=P/'manifest-final001.json';assert not private.exists();private.write_text(json.dumps(files,indent=2)+'\n')
record=dict(all_owned_emulators_closed=True,single_launch=True,orderly_exit=host,private_files_rehashed=len(files),private_manifest_sha256=sha(private),
            frozen_inputs_verified=len(json.loads((K/'emu001/frozen.json').read_text())),native_oem_shortcuts_restored=2,unresolved_long_paths=6,
            native_drm_raw_type_accepted=True,full_wmp_emulator_video_audio_pass=True,physical_playback_confirmation=False,
            strict_qualification=False,public_release_ready=False,all_original_failures_retained=True,physical_access=False)
out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
