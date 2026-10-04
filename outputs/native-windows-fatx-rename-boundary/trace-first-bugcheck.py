"""Read the first native bugcheck on an owned ManualCapture emulator run.

Requires an initial state-*.json from capture-runtime.py and no automatic
capture process. Holds the monitor lease while waiting for the breakpoint.
No register/data writes; raw stack capture stays in ignored work/runs.
"""
from pathlib import Path
import json,re,struct,sys,time
root=Path(__file__).resolve().parents[2];run=root/'work/runs'/sys.argv[1];assert run.resolve().parent==(root/'work/runs').resolve() and run.name.startswith('nt5-fatx-boot-rename-');sys.path[:0]=[str(root/'outputs/native-windows-prebuild'),str(root/'outputs/native-windows-physical-bootvideo')]
from monitor_capture import command,acquire_monitor_lock
from debug_remote import Remote
pub=json.loads((root/'outputs/native-windows-nt5-kernel/kernel-publics.json').read_text())['symbols']
deadline=time.monotonic()+420
while True:
 assert time.monotonic()<deadline and not (run/'cleanup.json').exists()
 paths=sorted(run.glob('state-*.json'));s=json.loads(paths[-1].read_text()) if paths else {}
 if 'kernel_base' in s:break
 time.sleep(2)
base=int(s['kernel_base'],16);entry=base+pub['_KeBugCheckEx@20']['rva'];r={'scope':'Exploratory read-only first-bugcheck breakpoint; alters timing, no result/data/register changes','run':run.name,'entry':hex(entry)}
with acquire_monitor_lock(4594):
 g=None;active=False;running=False
 try:
  command(4594,'stop');g=Remote(4595);g.s.settimeout(300);g.ask('qSupported');g.ask('?');g.bp(entry);active=True;g.send('c');running=True
  g.recv();running=False;regs=g.regs();r['registers']=regs;assert regs['eip']==entry
  raw=g.read(regs['esp'],min(2048,4096-(regs['esp']&4095)));(run/'first-bugcheck-stack.bin').write_bytes(raw);r['stack_words']=[hex(x) for x in struct.unpack('<'+'I'*(len(raw)//4),raw)];r['arguments']=r['stack_words'][1:6]
  r['frame_chain']=[];fp=regs['ebp']
  for _ in range(24):
   if not regs['esp']<=fp<regs['esp']+0x4000:break
   words=struct.unpack('<8I',g.read(fp,32));r['frame_chain'].append({'frame':hex(fp),'words':[hex(x) for x in words]});fp=words[0]
  (run/'first-bugcheck-register-memory.json').write_text(json.dumps({k:g.read(v,64).hex() for k,v in regs.items() if k in ['ebx','esi','edi'] and v>=0x80000000},indent=2)+'\n')
 except Exception as e:r['error']=repr(e)
 finally:
  if g:
   try:
    if running:g.s.sendall(b'\x03');g.recv();running=False
    if active:g.bp(entry,False);active=False
   except Exception as e:r['cleanup_error']=repr(e)
   finally:g.s.close()
  command(4594,'cont');r['breakpoint_removed']=not active;(run/'first-bugcheck-trace.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k!='stack_words'},indent=2))
