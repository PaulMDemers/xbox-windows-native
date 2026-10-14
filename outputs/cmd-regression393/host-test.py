import json,os,subprocess,hashlib
from pathlib import Path
K=Path(__file__).resolve().parent; root=Path('E:/xwn393/host002');assert not root.exists();root.mkdir(parents=True)
src=(K/'commands.cmd').read_text();pkg=json.loads((K.parent/'demo-validation385/package.json').read_text());data=Path(pkg['helpers'][-1]['source']).read_bytes()
operations=[('COPY_BMP','copy /b input.bmp saved.tmp >>files.log 2>&1'),('MOVE_BMP','move saved.tmp saved.bmp >>files.log 2>&1'),('REOPEN_BMP','copy /b saved.bmp reopened.bmp >>files.log 2>&1'),('WRITE_NOTE','echo XWN385 text persistence check>note.tmp 2>>files.log'),('MOVE_NOTE','move note.tmp note.txt >>files.log 2>&1'),('REOPEN_NOTE','copy /b note.txt note-reopened.txt >>files.log 2>&1')]
results=[]
for name in ['success']+[t for t,c in operations]+['stale']:
 d=root/name;d.mkdir();(d/'input.bmp').write_bytes(data)
 s=src.replace('cd /d C:'+chr(92)+'xwncmd393','cd /d '+str(d)).replace('THIS_TOKEN_IS_ABSENT','THIS_TOKEN_IS_ABSENT')
 if name=='stale':(d/'saved.tmp').write_bytes(b'preexisting')
 if name not in ['success','stale']:
  command=dict(operations)[name];assert s.count(command)==1
  s=s.replace(command,'cmd /d /c "echo injected-error 1>&2 & exit 7" >>files.log 2>&1')
 script=d/'test.cmd';script.write_bytes(s.replace(chr(10),chr(13)+chr(10)).encode());proc=subprocess.run([str(Path('E:/xwn385/cmd-host001/cmd-nt5.exe')),'/d','/c',str(script)],cwd=d,capture_output=True,timeout=30)
 rows=(d/'file-trace.log').read_text().splitlines();marker=(d/'file-complete.txt').exists()
 if name=='success':
  assert marker and rows.count('FILE_SUCCESS')==1
  for t,c in operations:assert rows.count('RC '+t+' 0')==1
  for n in ['saved.bmp','reopened.bmp']:assert (d/n).read_bytes()==data
  for n in ['note.txt','note-reopened.txt']:assert (d/n).read_bytes()==b'XWN385 text persistence check'+bytes([13,10]),repr((d/n).read_bytes())
  assert not (d/'saved.tmp').exists() and not (d/'note.tmp').exists()
 elif name=='stale':assert not marker and rows[-1]=='STALE_REFUSAL' and 'HOST_RUNNER_REACHED' not in rows and (d/'saved.tmp').read_bytes()==b'preexisting'
 else:
  assert not marker and rows.count('FILE_FAILED')==1 and rows.count('RC '+name+' 7')==1
  assert 'injected-error' in (d/'files.log').read_text()
  for t,c in operations[1+next(i for i,v in enumerate(operations) if v[0]==name):]:assert not any(r.startswith('RC '+t+' ') for r in rows)
 results.append({'case':name,'passed':True,'returncode':proc.returncode,'rows':rows})
record={'scope':'Actual pinnedNT5 CMD5.00.2195.6995 on modern host NTFS, NOT NT5 runtime qualification; runner replaced by inert marker; explicit command-failure injection','cases':results,'command_processor_sha256':hashlib.sha256(Path('E:/xwn385/cmd-host001/cmd-nt5.exe').read_bytes()).hexdigest(),'startup_sha256':hashlib.sha256((K/'commands.cmd').read_bytes()).hexdigest()}
(K/'host002.json').write_text(json.dumps(record,indent=2)+chr(10));print('8 actual batch control-flow cases passed')
