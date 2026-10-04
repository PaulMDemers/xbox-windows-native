from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'work/python-packages');import pefile
kit=Path(__file__).resolve().parent;driver=kit/'artifacts/xwnfatx.sys';pe=pefile.PE(str(driver));root=Path('outputs/native-windows-physical-mmcomplete/package')
targets={'ntoskrnl.exe':root/'WINNT/system32/ntoskrnl.exe','hal.dll':root/'loader/halxboxnt5.dll'};exports={}
for lib,path in targets.items():
 pp=pefile.PE(str(path));exports[lib]={s.name.decode() if s.name else s.ordinal for s in pp.DIRECTORY_ENTRY_EXPORT.symbols}
imports=[];missing=[]
for imp in pe.DIRECTORY_ENTRY_IMPORT:
 lib=imp.dll.decode().lower()
 for sym in imp.imports:
  name=sym.name.decode() if sym.name else sym.ordinal;row={'library':lib,'name':name,'resolved':name in exports.get(lib,set())};imports.append(row)
  if not row['resolved']:missing.append(row)
report={'scope':'Compile/import research only; no driver loading, filesystem mounting or ABI compatibility is established.','driver_sha256':hashlib.sha256(driver.read_bytes()).hexdigest(),'imports':imports,'missing':missing,'total_imports':len(imports),'kernel_sha256':hashlib.sha256(targets['ntoskrnl.exe'].read_bytes()).hexdigest()}
(kit/'vfat-nt5-compatible-imports.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'total':len(imports),'missing':missing},indent=2))
