import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'review001.json';assert not out.exists()
r=json.loads((K/'build001.json').read_text());h=json.loads((K/'host001.json').read_text())
p=Path('E:/xwn428/build001/probe.exe');assert r['compiled'] and h['passed'] and sha(p)==r['binary_sha256']
for n,v in r['inputs'].items():assert sha(K/n)==v
assert sha(K/'pattern.h')==h['source_sha256'] and sha(K/'oracle.py')==h['oracle_sha256']
pe=pefile.PE(str(p));assert pe.FILE_HEADER.Machine==0x14c and pe.OPTIONAL_HEADER.Subsystem==3
assert (pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
mods=json.loads((W/'outputs/crypto-path425/modules001.json').read_text())['modules'];imports={};providers={}
for d in pe.DIRECTORY_ENTRY_IMPORT:
 name=d.dll.decode().lower();q=Path('E:/xwn425/modules001')/name
 assert name in ('gdi32.dll','user32.dll','kernel32.dll') and sha(q)==mods[name]
 provider=pefile.PE(str(q));exports={s.name for s in provider.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
 assert all(i.name in exports for i in d.imports)
 imports[name]=[i.name.decode() for i in d.imports];providers[name]=sha(q)
record=dict(passed=True,binary_sha256=sha(p),imports=imports,providers=providers,
 sources=r['inputs'],host_checks=h['checks'],guest_or_hardware_execution=False,
 scope='Read-only existing escapes and bounded user-mode GDI. No mode, MMIO, driver or settings mutation. No reboot request.')
out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'passed':True,'imports':sum(map(len,imports.values()))}))
