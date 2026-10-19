"""Cold PSAPI export and DLL identity, before any new guest boot."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pefile
sys.path.insert(0,str(K.parent/'crypto-persistence423'));from ntfs_read002 import Reader,sha
out=K/'dynamic-import001.json';assert not out.exists()
c=json.loads((K/'ntfs-cold0-002.json').read_text());assert c['complete']
p=Path(c['private_path']);m=json.loads((p/'manifest.json').read_text())
disk=p.parent/'disk.qcow2';before=sha(disk);assert before==c['disk_sha256']
with Reader(disk) as reader:raw=reader.read('WINNT/system32/psapi.dll')
assert hashlib.sha256(raw).hexdigest()==m['winnt/system32/psapi.dll']['sha256']
pe=pefile.PE(data=raw);symbol=next(s for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name==b'GetProcessMemoryInfo')
assert not symbol.forwarder and sha(disk)==before
out.write_text(json.dumps(dict(passed=True,dll_sha256=hashlib.sha256(raw).hexdigest(),dll_bytes=len(raw),export='GetProcessMemoryInfo',export_rva=symbol.address,first_reader_manifest=c['manifest_sha256'],disk_unchanged=True,physical_access=False),indent=2)+'\n')
print('PASS NT5 GetProcessMemoryInfo export in exact cold PSAPI')
