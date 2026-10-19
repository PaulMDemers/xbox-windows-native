"""Build and read back the requested private Windows ZIP; no network operations."""
from pathlib import Path
import hashlib,json,shutil,sys,zipfile
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(W/'tools'));import tester_bundle as b
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
s=json.loads((K/'windows-stage001.json').read_text());assert s['completed']
assert json.loads((K/'windows-hives001.json').read_text())['passed']
stage=Path(s['root']);plan=Path(s['plan']);assert sha(plan)==s['plan_sha256']
dest=Path('E:/Xbox-Test-Kits/2026-10-19/Windows-2000-Xbox-E720p.zip');out=K/'windows-package001.json';assert not dest.exists() and not out.exists()
m=json.loads(plan.read_text());total=sum(x['bytes'] for x in m['files'])
assert shutil.disk_usage('E:/').free-total-16*1024**2>20*1024**3
r={'completed':False,'destination':str(dest),'console_bytes':s['console_bytes'],'required_e_free_bytes':int(1.25*1024**3),'other_console_boot_tested':False,'RCT_included':False,'source_installation':'Fresh read-only development-console E/720p snapshot; registry and active boot chain unchanged'}
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    digest=b.build(stage,plan,dest,private_windows=True)
    checked=b.verify(dest);assert checked==m
    tree=b.verify_tree(dest,stage);assert tree['bytes_verified']
    # Independently inspect every archive member and exclude game/firmware names.
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        for name in z.namelist():
            assert not any(x in name.lower() for x in ('rct.exe','rollercoaster','xwn582-kit','xwn586-kit','eeprom.bin','hddkey.bin'))
        startup=next(x for x in z.namelist() if x.lower().endswith('/startup/xwnsetup.cmd'))
        text=z.read(startup).decode('ascii');assert 'C:\\xwndemo372\\display-settings.exe' in text
        assert z.read('E/xwndemo372/display-settings.exe')==(stage/'E/xwndemo372/display-settings.exe').read_bytes()
    assert sha(dest)==digest
    dest.with_suffix('.zip.sha256').write_text(digest+'  '+dest.name+'\n',encoding='ascii')
    r.update(completed=True,sha256=digest,archive_bytes=dest.stat().st_size,files=len(m['files']),directories=len(m['directories']),readback_verified=True,source_tree_verified=True,remaining_e_bytes=shutil.disk_usage('E:/').free)
except BaseException as e:r['error']=repr(e);raise
finally:save()
print(json.dumps(r))
