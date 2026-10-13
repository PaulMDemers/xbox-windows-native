import hashlib,json,re,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(W/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=K/'binary-review001.json';assert not dest.exists()
b=json.loads((K/'build001.json').read_text());assert b['status']=='compiled'
p=Path('E:/xwn354/build001/diagnostic001/xwnown.dll');assert sha(p)==b['cases']['diagnostic001']['sha256']
pe=pefile.PE(str(p));assert pe.FILE_HEADER.Machine==0x14c and pe.OPTIONAL_HEADER.Subsystem==1 and pe.OPTIONAL_HEADER.CheckSum==pe.generate_checksum()
providers={};imports={};archive=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
for entry in pe.DIRECTORY_ENTRY_IMPORT:
 n=entry.dll.decode().lower();assert n in ['win32k.sys','ntoskrnl.exe']
 src=archive/n;exports={v.name for v in pefile.PE(str(src)).DIRECTORY_ENTRY_EXPORT.symbols if v.name and not v.forwarder}
 assert all(v.name in exports for v in entry.imports)
 imports[n]=[v.name.decode() for v in entry.imports];providers[n]=dict(path=str(src),sha256=sha(src))
tool='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-'
linux='/mnt/e/xwn354/build001/diagnostic001/xwnown.dll'
dis=subprocess.check_output(['wsl','-d','Ubuntu','--',tool+'objdump','-d',linux],text=True)
nm=subprocess.check_output(['wsl','-d','Ubuntu','--',tool+'nm',linux],text=True)
out=Path('E:/xwn354/review001');out.mkdir();(out/'all-disassembly.txt').write_text(dis);(out/'symbols.txt').write_text(nm)
assert not re.search(r'\b(?:wrmsr|wbinvd|invd|invlpg|cli|sti|movnti|fxsave|fxrstor)\b',dis)
assert not re.search(r'\bmov\s+%\w+,\s*%cr\d',dis)
assert len(re.findall(r'\brdmsr\b',dis))==1 and len(re.findall(r'\bcpuid\b',dis))==1
sites=[]
for n in ['_XwnMemoryState354','_m354_reg','_m354_cpuid','_m354_msr','_m354_read','_m354_cpu']:
 m=re.search(r'^([0-9a-fA-F]+) [Tt] '+re.escape(n)+r'$',nm,re.M);assert m,n
 rva=int(m[1],16)-pe.OPTIONAL_HEADER.ImageBase;s=pe.get_section_by_rva(rva)
 assert s and s.Characteristics&0x08000000 and s.Characteristics&0x20000000
 sites.append(dict(name=n,rva=rva,section=s.Name.rstrip(b'\0').decode()))
log=p.parent.parent/'diagnostic001.log';warnings=[v.strip() for v in log.read_text().splitlines() if 'warning:' in v]
assert all("defined but not used [-Wunused-function]" in v and any(n in v for n in ['XwnProfileCalibration','XwnProfileAccumulate']) for v in warnings)
dest.write_text(json.dumps(dict(passed=True,sha256=sha(p),imports=imports,providers=providers,resident_sites=sites,
 warnings=warnings,disassembly_sha256=sha(out/'all-disassembly.txt'),source_tree=b['source_tree'],
 no_privileged_writes=True,exception_handler_imports=imports.get('ntoskrnl.exe'),runtime_qualified=False,physical_access=False),indent=2)+'\n')
print('354 import/residency/read-only instruction review passed')
