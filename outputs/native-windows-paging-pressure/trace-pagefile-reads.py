"""Bounded read-only execution trace of native IoPageRead during the guest probe.

Execution breakpoints affect timing. This is separate from the unassisted
retention run; no register, return value or guest-data writes are performed.
"""
from pathlib import Path
import argparse,json,struct,sys,time
kit=Path(__file__).resolve().parent;root=kit.parents[1]
sys.path[:0]=[str(root/'outputs/native-windows-prebuild'),str(root/'outputs/native-windows-physical-bootvideo')]
from monitor_capture import command,acquire_monitor_lock
from debug_remote import Remote
p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args()
run=root/'work/runs'/a.run
assert run.resolve().parent==(root/'work/runs').resolve() and a.run.startswith('nt5-fatx-boot-pressure-')
report={'scope':'Exploratory read-only execution-breakpoint trace; not an unassisted timing result',
        'run':a.run,'pagefile_reads':[],'other_names':[]}
deadline=time.monotonic()+420
while True:
 assert time.monotonic()<deadline,'Guest pressure probe did not start'
 assert not (run/'cleanup.json').exists(),'Owned VM ended before trace'
 paths=sorted(run.glob('state-*.json'))
 try:s=json.loads(paths[-1].read_text()) if paths else {}
 except (ValueError,OSError):s={}
 if any(p['image'].lower()=='xwnpaging.exe' for p in s.get('processes',[])):break
 time.sleep(2)
pubs=json.loads((root/'outputs/native-windows-nt5-kernel/kernel-publics.json').read_text())
report['pdb_sha256']=pubs['pdb_sha256'];base=int(s['kernel_base'],16)
entry=base+pubs['symbols']['_IoPageRead@20']['rva'];report['entry']=hex(entry)
report['mdl_byte_count_offset']=20 # Exact NT5 _MDL layout, recorded in mdl-layout.json.
def u(g,at):return struct.unpack('<I',g.read(at,4))[0]
def name(g,fo):
 n,m,b=struct.unpack('<HHI',g.read(fo+48,8));assert n<=m and n<=1024
 return g.read(b,n).decode('utf-16le') if n else ''
with acquire_monitor_lock(4594):
 g=None;active=False;running=False
 try:
  command(4594,'stop');g=Remote(4595);g.s.settimeout(20);g.ask('qSupported');g.ask('?')
  g.bp(entry);active=True;g.send('c');running=True
  for _ in range(512):
   g.recv();running=False;regs=g.regs();assert regs['eip']==entry
   fo,mdl,offset,event,iosb=struct.unpack('<5I',g.read(regs['esp']+4,20));filename=name(g,fo)
   if filename.lower().endswith('\\pagefile.sys'):
    report['pagefile_reads'].append({'name':filename,'file_object':hex(fo),
      'file_offset':struct.unpack('<q',g.read(offset,8))[0],
      'requested_bytes':u(g,mdl+20),'io_status_block':hex(iosb)})
   elif filename not in report['other_names']:report['other_names'].append(filename)
   if len(report['pagefile_reads'])>=8:break
   g.bp(entry,False);active=False;g.send('s');running=True;g.recv();running=False
   g.bp(entry);active=True;g.send('c');running=True
  report['pagefile_read_submissions_observed']=len(report['pagefile_reads'])>=8
 except Exception as ex:
  report['error']=repr(ex)
 finally:
  if g:
   try:
    if running:g.s.sendall(b'\x03');g.recv();running=False
    if active:g.bp(entry,False);active=False
    report['breakpoints_removed']=not active
   finally:g.s.close()
  command(4594,'cont')
  (run/'pagefile-read-trace.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
