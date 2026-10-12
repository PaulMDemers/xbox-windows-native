"""Actual relocated code/stack checkpoints, no guest edits or Windows load."""
import pathlib,sys,json,hashlib,struct,re,datetime,traceback
from protocol import Remote,monitor
K=pathlib.Path(__file__).resolve().parent;case=sys.argv[1];assert case in ('control001','candidate001');O=K/case;R=pathlib.Path('E:/xwn294')/case
sys.path.insert(0,str(K.parent/'launcher-relocation293'));from review import elf
sys.path.insert(0,str(K.parent/'surface-bridge260'));from atomic_json import write_json
prep=json.loads((O/'prepared.json').read_text());review=json.loads((K.parent/'launcher-relocation293/binary-review004.json').read_text())['rows'][prep['mode']]
b,sections,symbols=elf(R/'image-crom.elf');text=sections['.text'];assert hashlib.sha256(b).hexdigest()==review['elf_sha256']
r=dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),passed=False,scope='Two launcher startup checkpoints only; no loaded Windows, no HD changes',physical_access=False,guest_memory_writes=False,guest_register_writes=False,captures=[],stops=[])
assert not (O/'trace.json').exists();g=None;point=None;stopped=True
save=lambda:write_json(O/'trace.json',r)
def capture(data,name):
 p=R/'private'/(name+'.bin');assert not p.exists();p.write_bytes(data);r['captures'].append(dict(path=str(p),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()));save();return data
def cmd(s,quit=False):
 v=monitor(4944,s,quit);r.setdefault('commands',[]).append(dict(command=s,reply=v));save();return v
try:
 g=Remote(4945);r['initial_stop']=g.ask('?');assert g.ask('qqemu.PhyMemMode')=='0'
 for i,name in enumerate(['BootResetAction','BootFromDevice']):
  point=symbols[name]['va'];assert g.ask('Z1,%x,1'%point)=='OK';g.send('c');stopped=False;reply=g.recv(90);stopped=True
  regs=struct.unpack('<16I',bytes.fromhex(g.ask('g'))[:64]);row=dict(name=name,eip=regs[8],esp=regs[4],stop=reply);r['stops'].append(row);save();assert regs[8]==point
  assert review['bss_end']<regs[4]<review['stack_top']
  txt=cmd('info registers');cr={n:int(v,16) for n,v in re.findall(r'\b(CR0|CR3|CR4)=([0-9a-fA-F]+)',txt)};row['control_registers']=cr;assert not cr['CR0']&0x80000000
  # Header config/checksum fields0..63 are mutable image-builder metadata.
  p=R/'private'/('stop%d-text.bin'%i);cmd('pmemsave 0x%x 0x%x "%s"'%(text['va']+64,text['size']-64,p.as_posix()));actual=p.read_bytes();r['captures'].append(dict(path=str(p),bytes=len(actual),sha256=hashlib.sha256(actual).hexdigest()));save()
  assert actual==b[text['offset']+64:text['offset']+text['size']],'Resident instruction mismatch'
  capture(g.read(point,32),'stop%d-function'%i);capture(g.read(regs[4],64),'stop%d-stack'%i)
  if i==1:
   capture(g.read(symbols['vmode']['va'],64),'stop1-vmode')
   capture(g.read(0xfd600800,4),'stop1-scanout')
  assert g.ask('z1,%x,1'%point)=='OK';point=None
 r['passed']=True;save()
except BaseException as e:r['error']=repr(e);r['traceback']=traceback.format_exc();save()
finally:
 try:
  if g:
   if not stopped:r['interrupt']=g.interrupt();stopped=True
   if point:assert g.ask('z1,%x,1'%point)=='OK';point=None
   r['physical_mode_restored']=g.ask('qqemu.PhyMemMode')=='0';g.s.close();g=None
  # Stop before BootFromDevice performs the absent-payload lookup. No guest shutdown claim.
  cmd('stop');cmd('quit',True);r['orderly_quit_sent']=True
 except BaseException as e:r['cleanup_error']=repr(e)
 r['remaining_breakpoint']=point;r['closed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps({n:r.get(n) for n in ['passed','error','cleanup_error']}))
