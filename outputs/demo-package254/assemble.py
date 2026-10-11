"""Deterministic private overlay assembly from exact qualified inputs, not compilation or deployment."""
import argparse,hashlib,json,zipfile
from pathlib import Path

k=Path(__file__).resolve().parent;repo=k.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
assert not args.output.exists(),'Preserve previous assembly'
stage=repo/'outputs/demo-physical253';physical=read(stage/'combined001/audit.json')
review=read(stage/'combined001/binding-transition-review.json')
assert review['supplemental_scoped_combined_passed'] and read(stage/'accepted-state.json')['passed']
assert sha((stage/'combined001/audit.json').read_bytes())==review['original_audit_sha256']
repeat=read(repo/'outputs/demo-audition255/playback001/audit.json')
assert repeat['scoped_runtime_passed'] and repeat['typed_state']['binding_metadata_unchanged']
assert read(repo/'outputs/demo-audition255/accepted-state.json')['passed']
package=read(stage/'package.json');files={};sources={}
for row in package['video']:
    source=stage/'artifacts/payload'/row['name'];data=source.read_bytes();assert sha(data)==row['sha256']
    name='overlay/'+row['path'].lstrip('/');files[name]=data;sources[name]=dict(source=row['source'],sha256=sha(data))
audio=repo/'outputs/demo-physical252/artifacts/payload/install'
for name,expected in {
    'xwnaci207.sys':'c5736457d9f4b7c6dafc730eb19bc0eda6c6820cee8e21580d357708df36cd75',
    'xwnaci207.inf':'85e83ac9eb8270e0ead7d34a086357caf7ea66ec50f72c5e9a2c3028fd869b49',
    'install.exe':'f141c9160378ffc3b467e9e82b0716dcd481364e2ee595e18a669fd911b0e410'}.items():
    source=audio/name;data=source.read_bytes();assert sha(data)==expected
    target='audio-setup/'+name;files[target]=data;sources[target]=dict(source=str(source.relative_to(repo)),sha256=sha(data))
for row in package['helpers']:
    data=(stage/'artifacts/payload'/row['name']).read_bytes();assert sha(data)==row['sha256']
    name='validation/'+row['name'];files[name]=data;sources[name]=dict(source=row['source'],sha256=sha(data))
for name in ['README.md','RECOVERY.md']:
    files[name]=(k/name).read_bytes()
changes=read(stage/'binding-edit.json')['changes']
files['video-binding-changes.json']=(json.dumps(changes,indent=2)+'\n').encode()
manifest=dict(format_version=1,name='demo253-audio004-video118-preview',release_qualified=False,
    strict_qualification_passed=physical['strict_qualification_passed'],scoped_combined_physical_passed=True,
    physical_audit_sha256=sha((stage/'combined001/audit.json').read_bytes()),
    physical_binding_transition_review_sha256=sha((stage/'combined001/binding-transition-review.json').read_bytes()),
    unchanged_driver_reboot_audit_sha256=sha((repo/'outputs/demo-audition255/playback001/audit.json').read_bytes()),
    known_limits=physical['limits'],files={n:dict(bytes=len(b),sha256=sha(b)) for n,b in sorted(files.items())},sources=sources,
    excludes=['Windows binaries','BIOS/firmware/keys','complete system hives','automatic deployment','unqualified PCI/USB prototypes'])
files['MANIFEST.json']=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
args.output.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(args.output,'x',compression=zipfile.ZIP_STORED) as z:
    for name,data in sorted(files.items()):
        entry=zipfile.ZipInfo(name,date_time=(2026,10,11,0,0,0));entry.create_system=3;entry.external_attr=0o100644<<16;entry.compress_type=zipfile.ZIP_STORED
        z.writestr(entry,data)
with zipfile.ZipFile(args.output) as z:
    assert z.namelist()==sorted(files) and all(z.read(n)==b for n,b in files.items())
r=dict(path=str(args.output.resolve()),sha256=sha(args.output.read_bytes()),bytes=args.output.stat().st_size,entries=len(files),readback_verified=True,deterministic_assembly=True,compiled=False,deployed=False,release_qualified=False)
args.output.with_suffix('.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
