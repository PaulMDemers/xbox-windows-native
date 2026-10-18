"""Execute proposed outer gate + exact498 as i386; all Xbox APIs modeled."""
import datetime,hashlib,json,os,re,shutil,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn503/host001');out=K/'host001.json'
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not out.exists() and not O.exists()
assert shutil.disk_usage('/mnt/c').free-32*1024**2>=20*1024**3
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
O.mkdir(parents=True)
names=['indicator.S','entry498.S','combined.S','host.S','host.c','host-tail.c','decode.py','host001.py','prepare001.py']
tools=[Path('/usr/bin')/n for n in ['gcc','as','ld','objdump']]
r=dict(started=utc(),passed=False,physical_access=False,new_XBE=False,scope='Actual Linux i386 assembly execution with modeled Xbox SMBus/delay/file/firmware services',source_pins={n:sha(K/n) for n in names},tool_pins={str(p):sha(p) for p in tools},cases=[])
def save():out.write_bytes((json.dumps(r,indent=2)+'\n').encode())
try:
 for n in names:shutil.copyfile(K/n,O/n)
 r['compiler_version']=subprocess.check_output(['gcc','--version'],text=True).splitlines()[0]
 r['commands']=[['gcc','-m32','-c','combined.S','-o','combined.o'],['gcc','-m32','-O2','-g','-fno-pie','-no-pie','-fno-stack-protector','-Wall','-Wextra','-Werror','-MMD','host.c','host.S','combined.o','-o','host']]
 for cmd in r['commands']:
  with (O/'build.log').open('ab') as f:subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=60)
 dis=subprocess.check_output(['objdump','-dr','-Mintel',str(O/'combined.o')],text=True);(O/'disassembly.txt').write_bytes(dis.encode())
 assert not re.search(r'\t(?:cli|sti|in|out|rdmsr|wrmsr|hlt)\s',dis)
 assert not re.search(r'\b(?:cr[034]|idtr|gdtr)\b',dis)
 r['dependencies']=subprocess.check_output(['ldd',str(O/'host')],text=True)
 prior=json.loads((K.parent/'entry-receipt498/host001.json').read_text());assert prior['passed']
 cases=[[*v['parameters'],0,0] for v in prior['cases']]
 for fault in range(7):
  for flags in [0x202,0x602]:
   for led,delay in [(1,0),(2,0),(3,0),(4,0),(0,1),(0,2)]:cases.append([fault,1 if fault else 0,flags,0,led,delay])
 for led in range(5):
  for delay in [1,2]:cases.append([0,0,0x602,0,led,delay])
 for i,case in enumerate(cases):
  target=O/f'case{i:03}.bin'
  p=subprocess.run([str(O/'host'),*map(str,case),str(target)],cwd=O,capture_output=True,timeout=3)
  (O/f'case{i:03}.stdout').write_bytes(p.stdout);(O/f'case{i:03}.stderr').write_bytes(p.stderr)
  row=dict(index=i,parameters=case,exit_code=p.returncode);r['cases'].append(row);save()
  assert p.returncode==0,(case,p.stderr.decode(errors='replace'))
  row.update(json.loads(p.stdout));row['receipt_sha256']=sha(target)
 r.update(passed=True,case_count=len(cases),inherited_file_cases=len(prior['cases']),register_flag_success_cases=128,added_indicator_failure_cases=len(cases)-len(prior['cases']),all_reentries_refused=True,privileged_state_or_raw_IO_instructions=False)
 assert all(sha(K/n)==h for n,h in r['source_pins'].items())
except BaseException as e:r['error']=repr(e);raise
finally:
 r.update(finished=utc(),closed=True,files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()});save()
 print({k:r[k] for k in ['passed','closed','scope']})
