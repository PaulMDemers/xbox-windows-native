"""Unique modern-Windows control of authored samples, never Xbox qualification."""
import hashlib, json, platform, subprocess, sys, time
from pathlib import Path
W=Path(__file__).resolve().parents[2]
K=Path(__file__).resolve().parent
P=Path('E:/xwn436/host001')
B=Path('E:/xwn436/build002')
assert not P.exists() and not (K/'host001.json').exists()
sys.path.insert(0,str(W/'work/python-packages'))
sys.path.insert(0,str(W/'tools'))
import pefile
import graphics_sample
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=json.loads((B/'build.json').read_text())
assert sha(B/'ladder.exe')==build['executable_sha256']
assert sha(W/'src/samples/graphics-ladder/ladder.c')==build['source_sha256']
pe=pefile.PE(str(B/'ladder.exe'))
assert pe.FILE_HEADER.Machine==0x14c
assert (pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
assert pe.OPTIONAL_HEADER.Subsystem==3
modules=Path('E:/xwn425/modules001')
pins=json.loads((W/'outputs/crypto-path425/modules001.json').read_text())['modules']
imports=[]
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    dll=entry.dll.decode().lower()
    assert dll in ('kernel32.dll','user32.dll','gdi32.dll')
    path=modules/dll
    assert sha(path)==pins[dll]
    target=pefile.PE(str(path))
    exports={s.name.decode():s for s in target.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
    for imp in entry.imports:
        assert imp.name
        name=imp.name.decode()
        assert name in exports and not exports[name].forwarder
        imports.append(dict(dll=dll,name=name,nt5_dll_sha256=pins[dll]))
P.mkdir(parents=True)
record=dict(schema=1,platform=platform.platform(),executable_sha256=sha(B/'ladder.exe'),
            reviewer_sha256=sha(Path(__file__)),oracle_sha256=sha(W/'tools/graphics_sample.py'),
            imports=imports,rows=[],scope='Actual modern host API control, not Windows 2000 or Xbox runtime')
for rung,backend in [('00','default')]+[(r,b) for r in ('01','02') for b in ('default','hel','hal')]:
    prefix=P/(rung+'-'+backend)
    cmd=[str(B/'ladder.exe'),rung,backend,str(prefix),'quiet']
    row=dict(rung=rung,backend=backend,command=cmd)
    start=time.monotonic()
    try:
        proc=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30,
                            creationflags=subprocess.CREATE_NO_WINDOW)
        row['exit_code']=proc.returncode
        (Path(str(prefix)+'.exit')).write_text(str(proc.returncode)+'\n',encoding='ascii')
        (Path(str(prefix)+'.stdout')).write_bytes(proc.stdout)
        (Path(str(prefix)+'.stderr')).write_bytes(proc.stderr)
        try:
            row['review']=graphics_sample.review(prefix,Path(str(prefix)+'.exit'))
        except Exception as exc:
            row['review_failure']=str(exc)
    except subprocess.TimeoutExpired:
        row['timeout']=True
    row['seconds']=time.monotonic()-start
    row['files']={p.name:sha(p) for p in P.glob(prefix.name+'*') if p.is_file()}
    record['rows'].append(row)
    (K/'host001.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({r['rung']+'-'+r['backend']:{k:r[k] for k in ('exit_code','review_failure','review') if k in r} for r in record['rows']},indent=2))
