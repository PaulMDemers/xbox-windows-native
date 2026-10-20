"""Review the exact two compiled tools and the source bytes copied to the build."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K.parents[1]/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((K/'build001.json').read_text());assert b['status']=='compiled'
out=K/'binary-review001.json';assert not out.exists();rows=[]
for p,h in b['files'].items():
 if Path(p).suffix in ['.c','.h']:
  assert sha(K/Path(p).name)==h['sha256']
for row in b['rows']:
 p=Path(row['path'].replace('/mnt/c/','C:/'));assert sha(p)==row['sha256']
 pe=pefile.PE(str(p));assert pe.FILE_HEADER.Machine==0x14c
 assert pe.OPTIONAL_HEADER.MajorSubsystemVersion==5
 imports={d.dll.decode():[v.name.decode() for v in d.imports] for d in pe.DIRECTORY_ENTRY_IMPORT}
 assert all(n.lower() in ['kernel32.dll','user32.dll','gdi32.dll','advapi32.dll'] for n in imports)
 flat={n for v in imports.values() for n in v}
 assert not flat&{'DebugActiveProcess','WaitForDebugEvent','WriteProcessMemory','CreateRemoteThread'}
 if p.name=='run615.exe':
  assert {'GetProcessTimes','QueryPerformanceCounter','QueryPerformanceFrequency','GetTickCount',
          'LoadLibraryA','GetProcAddress','CreateProcessA','SetCommTimeouts'}<=flat
 rows.append(dict(name=p.name,sha256=row['sha256'],imports=imports))
assert {r['name'] for r in rows}=={'run615.exe','verify615.exe'}
out.write_text(json.dumps(dict(passed=True,rows=rows,source_build_exact=True),indent=2)+'\n')
