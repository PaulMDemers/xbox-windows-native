"""Prepare a new physical controller for unchanged, emulator-tested466 bytes."""
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'boot-refusal462';Q=K.parent/'marker-handoff466'
assert not (K/'physical.py').exists()
for n in ['decode.py','refusal_decode.py']:(K/n).write_bytes((Q/n).read_bytes())
s=(P/'physical.py').read_text()
s=s.replace("P=W/'work/boot-refusal462/physical001'","P=Path('C:/xwn467/physical001')")
s=s.replace("REMOTE='/E/Applications/XWNBoot462a';BUILD=Path('E:/xwn462/build001/default.xbe')","REMOTE='/E/Applications/XWNBoot466a';BUILD=Path('C:/xwn466/build001/default.xbe')")
s=s.replace('baseline,connect,get,','baseline,connect as connect_base,get,')
s=s.replace("read=lambda p:","def connect(timeout=45):return connect_base(timeout=timeout)\nread=lambda p:")
a=s.index('def verify():');z=s.index('\ndef startup(',a)
s=s[:a]+'''def verify():
 ticket();q=K.parent/'marker-handoff466'
 assert read(q/'final-review.json')['passed']
 assert read(q/'source-review002.json')['passed']
 t=read(q/'emu003/trace.json');assert t['passed'] and not t.get('cleanup_error')
 assert t['physical_mode_restored'] and not t['remaining_breakpoints']
 assert read(q/'emu003/audit.json')['host_exit']['passed']
 assert read(q/'emu003/actual-controls.json')['passed']
 for n in ['host001','stub-host001']:
  h=read(q/(n+'.json'));assert h['status']=='passed'
  for p,v in h['files'].items():assert sha(local(p).read_bytes())==v['sha256'],p
 b=read(q/'build001.json');assert b['status']=='compiled'
 for p,v in b['files'].items():assert sha(local(p).read_bytes())==v['sha256'],p
 data=BUILD.read_bytes();assert sha(data)==b['sha256']=='74a479078f378b8f02c54d4bd146765a7d860031116f636a3658a6616c2bedf5'
 return data
'''+s[z:]
s=s.replace(" listing=names(f,START);", " assert sha(get(f,TARGET))=='6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'\n listing=names(f,START);")
s=s.replace(" for drive in ['C:/','E:/']:assert shutil.disk_usage(drive).free-16*1024**2>=20*1024**3"," assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3")
s=s.replace("case='462physical001',cookie='46200101',purpose='log preparation then original handoff'","case='467physical001',cookie='46600101',purpose='two bounded SMC markers then original handoff'")
s=s.replace(r'SITE EXEC E:\Applications\XWNBoot462a\default.xbe',r'SITE EXEC E:\Applications\XWNBoot466a\default.xbe')
(K/'physical.py').write_text(s)
