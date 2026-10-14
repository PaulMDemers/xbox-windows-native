"""Read-only independent CMD regression verification and negative mutations."""
from pathlib import Path
import json,hashlib
K=Path(__file__).resolve().parent;O=K/'candidate001';A=O/'artifacts/cmd393'
ops=['COPY_BMP','MOVE_BMP','REOPEN_BMP','WRITE_NOTE','MOVE_NOTE','REOPEN_NOTE']
pkg=json.loads((K.parent/'demo-validation387/package.json').read_text());expected=pkg['helpers'][-1]
rows=(A/'file-trace.log').read_text().splitlines()
files={n:(A/n).read_bytes() if (A/n).exists() else None for n in ['file-complete.txt','saved.bmp','reopened.bmp','note.txt','note-reopened.txt','saved.tmp','note.tmp']}
def valid(rows,files):
 return (rows.count('BEGIN')==1 and rows.count('FILE_SUCCESS')==1 and not any(t in rows for t in ['FILE_FAILED','STALE_REFUSAL']) and [s for s in rows if s.startswith('RC ')]==['RC '+n+' 0' for n in ops] and files['file-complete.txt']==b'COMPLETE\r\n' and files['saved.tmp'] is None and files['note.tmp'] is None and all(files[n] is not None and len(files[n])==expected['bytes'] and hashlib.sha256(files[n]).hexdigest()==expected['sha256'] for n in ['saved.bmp','reopened.bmp']) and all(files[n]==b'XWN385 text persistence check\r\n' for n in ['note.txt','note-reopened.txt']))
assert valid(rows,files);count=0
for op in ops:
 for replacement in ['RC '+op+' 1','']:
  changed=[replacement if s=='RC '+op+' 0' else s for s in rows];assert not valid(changed,files);count+=1
for n in files:
 changed=dict(files);changed[n]=b'changed' if files[n] is not None else b'stale';assert not valid(rows,changed);count+=1
for extra in ['FILE_SUCCESS','FILE_FAILED','STALE_REFUSAL','RC MOVE_BMP 0']:
 assert not valid(rows+[extra],files);count+=1
r=dict(passed=True,actual_cmd_steps=len(ops),independent_negative_cases=count,original_artifacts_unchanged=True,physical_qualified=False,log_sha256=hashlib.sha256((A/'file-trace.log').read_bytes()).hexdigest())
p=K/'actual-controls.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n');print(r)
