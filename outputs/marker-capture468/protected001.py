"""Independent cold before/after bytes for five hives and three baseline binaries."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'emu001/protected.json';assert not out.exists()
sys.path.insert(0,str(W/'outputs/release-readiness403'));from stock_io002 import ColdIO,readers
source=Path('/mnt/c/xwn468/preparation001/seed.qcow2');child=Path('/mnt/c/xwn468/runs/nt5-capture468-emu001/hdd.qcow2')
names=['Applications/XWNEBoot/default.xbe','WINNT/system32/drivers/xwnfatx.sys','WINNT/system32/drivers/xboxvnt5.sys']
names+=['WINNT/system32/config/'+n for n in ['SYSTEM','SOFTWARE','DEFAULT','SAM','SECURITY']]
r=dict(passed=False,physical_access=False,files=[])
try:
 with ColdIO(source) as a,ColdIO(child) as b:
  wa=readers(a,source)['E'];wb=readers(b,child)['E']
  for name in names:
   before=wa.read(name);after=wb.read(name);assert before==after,name
   r['files'].append(dict(path=name,bytes=len(after),sha256=hashlib.sha256(after).hexdigest(),byte_exact=True))
 r.update(passed=True,hives=5,baseline_binaries=3,hive_semantics_requalified=False)
except BaseException as e:r['error']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
