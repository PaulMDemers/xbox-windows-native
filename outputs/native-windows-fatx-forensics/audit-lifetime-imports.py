"""Resolve the guest probe's names against the exact local NT5 DLL exports."""
from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,'work/python-packages')
import pefile
kit=Path(__file__).resolve().parent
import argparse
p=argparse.ArgumentParser();p.add_argument('--artifact',default='xwnlife');a=p.parse_args();assert a.artifact in ['xwnlife','xwnlifeverify','xwnlongsoak']
probe=kit/('artifacts/'+a.artifact+'.exe'); pe=pefile.PE(str(probe))
imports=[];libraries={}
for group in pe.DIRECTORY_ENTRY_IMPORT:
 name=group.dll.decode().lower();path=Path('work/abi-libraries')/name
 if not path.exists():path=kit.parent/'native-windows-physical-f/package/F/winnt/system32'/name
 dll=pefile.PE(str(path));exports={e.name.decode() if e.name else e.ordinal for e in dll.DIRECTORY_ENTRY_EXPORT.symbols}
 libraries[name]=hashlib.sha256(path.read_bytes()).hexdigest()
 for imp in group.imports:
  symbol=imp.name.decode() if imp.name else imp.ordinal
  imports.append({'dll':name,'name':symbol,'resolved':symbol in exports})
r={'sha256':hashlib.sha256(probe.read_bytes()).hexdigest(),
 'subsystem_version':[pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion],
 'imports':imports,'libraries':libraries,'all_resolved':all(i['resolved'] for i in imports)}
(kit/(a.artifact+'-import-audit.json')).write_text(json.dumps(r,indent=2)+'\n')
assert r['all_resolved'] and r['subsystem_version']==[5,0]
print(r['sha256'],len(imports),'imports resolved')
