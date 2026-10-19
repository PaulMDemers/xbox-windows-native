"""Paired read-only installed PSAPI identity/export check; no console writes."""
import importlib.util,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pefile
s=importlib.util.spec_from_file_location('pair551psapi',K.parent/'windows-pair532/controller.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
p.verify();out=K/'psapi001.json';assert not out.exists()
r=dict(passed=False,console_C_accessed=False,remote_writes=[])
raw=p.m.cold_pair('/E/winnt/system32/psapi.dll',r,out);assert raw
expected=p.read(K.parent/'scene-cost550/dynamic-import001.json')['dll_sha256'];assert p.m.sha(raw)==expected
pe=pefile.PE(data=raw);symbol=next(v for v in pe.DIRECTORY_ENTRY_EXPORT.symbols if v.name==b'GetProcessMemoryInfo');assert not symbol.forwarder
dest=Path('C:/xwn551/psapi001.dll');assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
r.update(passed=True,sha256=expected,bytes=len(raw),export='GetProcessMemoryInfo',export_rva=symbol.address,private_path=str(dest))
p.m.write_json(out,r);print('PASS paired installed Xbox PSAPI matches PC and exports memory counter API')
