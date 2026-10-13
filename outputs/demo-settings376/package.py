"""Small demo add-on only: original utility, commands, guides; no OS/media."""
import hashlib,json,zipfile
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=Path('E:/xwn376/package001')
assert not O.exists();O.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
exe=Path(read(K/'build-review001.json')['binary']).read_bytes()
assert sha(exe)==read(K/'build-review001.json')['binary_sha256']
files={'display-settings.exe':exe}
for name,mode in [('Outline dragging','outline'),('Full window dragging','full'),('Display status','status')]:
    files[name+'.cmd']=('@echo off\r\nC:\\xwndemo372\\display-settings.exe '+mode+'\r\npause\r\n').encode()
files['DEMO.txt']=('Windows on Xbox - E demo\r\n\r\nUse the Outline dragging / Full window dragging command files here.\r\nThe setting is saved for this Windows user.\r\nSave a note or Paint BMP here, close and reopen it.\r\nUse Start - Shut Down - Restart when finished.\r\nWindows C is dashboard E; do not use Windows F as scratch.\r\nNo GPU acceleration is claimed.\r\n').encode()
startup=b'@echo off\r\nif exist C:\\xwndemo372\\outline-applied.txt goto ready\r\nC:\\xwndemo372\\display-settings.exe outline > C:\\xwndemo372\\outline-first.txt\r\nif errorlevel 1 goto ready\r\necho Applied > C:\\xwndemo372\\outline-applied.txt\r\n:ready\r\nexit\r\n'
for n,b in files.items():(O/n).write_bytes(b)
(O/'demo-startup.cmd').write_bytes(startup)
r=dict(files={n:dict(bytes=len(b),sha256=sha(b)) for n,b in files.items()},startup=dict(bytes=len(startup),sha256=sha(startup)),private_demo_addon=True,contains_windows_firmware_hives=False,physical_qualified=False)
(O/'MANIFEST.json').write_text(json.dumps(r,indent=2)+'\n')
entries={**files,'demo-startup.cmd':startup,'MANIFEST.json':(O/'MANIFEST.json').read_bytes()}
for n in ['DEMO','DISPLAY','RECOVERY','BUILD','PUBLIC-RELEASE']:entries['docs/'+n+'.md']=(W/'docs'/ (n+'.md')).read_bytes()
zipout=O/'xwn-demo-addon.zip'
with zipfile.ZipFile(zipout,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for n,b in sorted(entries.items()):
        info=zipfile.ZipInfo(n,(2026,10,13,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,b)
with zipfile.ZipFile(zipout) as z:
    assert set(z.namelist())==set(entries)
    for n,b in entries.items():assert z.read(n)==b
r.update(package_root=str(O),archive=str(zipout),archive_sha256=sha(zipout.read_bytes()),archive_entries=len(entries),readback_verified=True)
(K/'package001.json').write_text(json.dumps(r,indent=2)+'\n');print('Demo add-on assembled and every ZIP entry readback verified')
