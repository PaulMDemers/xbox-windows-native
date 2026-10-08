"""Offline review bundle only: exact emulator-tested display chain and historical file rollback."""
import datetime,hashlib,json,sys,zipfile
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
def sha(data):return hashlib.sha256(data).hexdigest()
def read(p):return json.loads(p.read_text())
def file_sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
dest=k/'package-review.json';assert not dest.exists();art=k/'artifacts';art.mkdir(exist_ok=False)
fixture=read(ws/'outputs/video-windows-timing156/fixture-candidate001.json')
assert read(ws/'outputs/video-windows-timing156/series-closure.json')['timing_qualified']
assert read(ws/'outputs/video-window-foreground/pair-review.json')['passed']
records=fixture['protected']+[dict(volume='F',**r) for r in fixture['payloads']]
sources=[('F/winnt/system32/drivers/xboxvnt5.sys','outputs/video-shared-framebuffer/candidate001/artifacts/xboxvnt5.sys'),
 ('E/Applications/XWNFBoot/loader/xboxbvid.dll','outputs/video-shared-framebuffer/candidate001/artifacts/xboxbvid.dll'),
 ('F/winnt/system32/xwnown.dll','outputs/video-clip-upload/candidate001/artifacts/xwnown.dll')]
candidate={};rows=[]
for target,source in sources:
    v,path=target.split('/',1);data=(ws/source).read_bytes()
    expected=next(r['sha256'] for r in records if r['volume']==v and r['path']==path)
    assert sha(data)==expected
    candidate[target]=data;rows.append(dict(target=target,source=source,bytes=len(data),sha256=expected))
mini=pefile.PE(data=candidate[sources[0][0]]);provider=pefile.PE(data=candidate[sources[1][0]])
imports={i.name.decode() for d in mini.DIRECTORY_ENTRY_IMPORT if d.dll.lower()==b'bootvid.dll' for i in d.imports}
exports={e.name.decode() for e in provider.DIRECTORY_ENTRY_EXPORT.symbols if e.name}
assert imports=={'XwnFbAcquire','XwnFbRelease','XwnFbReleaseOwner'} and imports<=exports
baseline=read(ws/'outputs/fatx0101-physical/installed-state.json');assert baseline['passed']
capture=read(ws/'outputs/release-0.1.0/capture-summary.json');rollback={};bundles=[]
targets={'F/winnt/system32/drivers/xboxvnt5.sys','F/winnt/system32/framebuf.dll','E/Applications/XWNFBoot/loader/xboxbvid.dll'}
for bundle in capture['bundles']:
    p=Path(bundle['path']);assert file_sha(p)==bundle['sha256'];bundles.append(dict(path=str(p),sha256=bundle['sha256']))
    with zipfile.ZipFile(p) as z:
        for target in targets:
            if target in z.namelist():rollback[target]=z.read(target)
assert set(rollback)==targets
historical=[]
for path,data in rollback.items():
    known=baseline['checks'].get('/'+path)
    if known:assert sha(data)==known['expected']==known['sha256']
    historical.append(dict(target=path,bytes=len(data),sha256=sha(data),matches_last_physical_check=bool(known)))
def bundle(name,entries):
    p=art/name
    with zipfile.ZipFile(p,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for path,data in entries.items():z.writestr(path,data)
    with zipfile.ZipFile(p) as z:
        assert set(z.namelist())==set(entries)
        assert all(z.read(path)==data for path,data in entries.items())
    return dict(path=str(p),bytes=p.stat().st_size,sha256=file_sha(p),entries_readback_verified=True)
r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope=__doc__,passed=True,
    physical_access=False,physical_qualified=False,deployment_ready=False,source_script_sha256=file_sha(Path(__file__)),
    candidate=rows,provider_imports=sorted(imports),provider_exports=sorted(exports),historical_rollback=historical,
    old_archives_unchanged=bundles,bundles=[bundle('candidate-display157.zip',candidate),bundle('historical-display-rollback157.zip',rollback)],
    pins={p:file_sha(ws/p) for p in ['outputs/video-windows-timing156/fixture-candidate001.json','outputs/video-windows-timing156/series-closure.json','outputs/video-window-foreground/pair-review.json','outputs/fatx0101-physical/installed-state.json','outputs/release-0.1.0/capture-summary.json']},
    pending=['Fresh read-only physical hashes/configuration/geometry and live rollback capture; historical provider is not in last installed-state checks.',
      'Review exact Windows display binding update to xwnown in the real physical registry; retain native device policy and all current settings.',
      'Fresh ordinary emulator trial reconstructed from the physical baseline with only the display chain/bindings changed; retain strict cold gates.',
      'Bounded hardware boot/drawing/app-save/restart trial followed by cold file/event/hive/allocation audit. No physical speed or new mode qualification yet.'])
dest.write_text(json.dumps(r,indent=2)+'\n');print('Three candidate payloads and historical file rollback bundled/readback-verified; deployment_ready FALSE')
