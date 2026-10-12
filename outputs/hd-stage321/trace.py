"""Single resident-pinned loader return capture; no guest state mutation."""
import datetime,hashlib,json,re,struct,sys,time,traceback
from pathlib import Path
from protocol import Remote,monitor
k=Path(__file__).resolve().parent;out=k/'candidate001';run=Path('D:/xwn321/runs/nt5-hd321-candidate001');private=Path('D:/xwn321/capture001')
sys.path.insert(0,str(k.parent/'surface-bridge260'));from atomic_json import write_json
plan=json.loads((k/'plan.json').read_text());dest=out/'trace.json';assert not dest.exists() and not private.exists();private.mkdir(parents=True)
r=dict(status='waiting',physical_access=False,diagnostic=True,ordinary_qualified=False,guest_memory_writes=False,guest_register_writes=False,captures=[],breakpoint_installed=False,breakpoint_removed=False,physical_mode_restored=False,resumed=False)
g=None;stopped=False;physical=False;points=[]
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():write_json(dest,r)
def read(address,size,label):
 data=g.read(address,size);p=private/(label+'.bin');assert not p.exists();p.write_bytes(data);r['captures'].append(dict(path=str(p),address=address,bytes=size,sha256=hashlib.sha256(data).hexdigest()));save();return data
try:
 deadline=time.monotonic()+90
 while not (run/'startup-ready.json').exists():
  assert time.monotonic()<deadline and not (run/'cleanup.json').exists(),'No active owned runner';time.sleep(.2)
 r['attach_stop']=monitor(5084,'stop');stopped=True
 g=Remote(5085);r['initial_stop']=g.ask('?');assert g.ask('qqemu.PhyMemMode')=='0'
 for bp in plan['condition_points']+[plan['breakpoint']]:
  assert g.ask('Z1,%x,1'%bp)=='OK';points.append(bp)
 r['breakpoint_installed']=True;r['status']='armed';save()
 g.send('c');stopped=False;write_json(out/'trace-armed.json',dict(armed=True,utc=utc(),point=plan['breakpoint']))
 r['conditions']=[]
 for i,bp in enumerate(plan['condition_points']):
  reply=g.recv(90);stopped=True;regs=struct.unpack('<16I',bytes.fromhex(g.ask('g'))[:64]);r['conditions'].append(dict(point=bp,reply=reply,registers=list(regs)));save();assert regs[8]==bp and regs[10]&3==0
  text=bytearray()
  for off in range(0,plan['text']['bytes'],65536):text+=read(plan['text']['va']+off,min(65536,plan['text']['bytes']-off),'condition%d-text-%d'%(i,off))
  assert hashlib.sha256(text).hexdigest()==plan['text']['sha256']
  expected_address=regs[4]+0x5c if i==0 else regs[2]+0x38+regs[3]*4
  n=1 if i==0 else 4;expected=int.from_bytes(read(expected_address,n,'condition%d-expected'%i),'little')
  r['conditions'][-1].update(actual=(regs[0]&255) if i==0 else regs[0],expected=expected,zero_flag=bool(regs[9]&0x40),expected_address=expected_address,index=regs[3]);save()
  assert g.ask('z1,%x,1'%bp)=='OK';points.remove(bp);g.send('c');stopped=False
 r['stop_reply']=g.recv(90);stopped=True;r['stop_utc']=utc();save()
 raw=bytes.fromhex(g.ask('g'));regs=struct.unpack('<16I',raw[:64]);r['registers']=list(regs);save();assert regs[8]==plan['breakpoint'] and regs[10]&3==0
 text=bytearray()
 for off in range(0,plan['text']['bytes'],65536):text+=read(plan['text']['va']+off,min(65536,plan['text']['bytes']-off),'text-%d'%off)
 assert hashlib.sha256(text).hexdigest()==plan['text']['sha256'],'Actual loader text mismatch'
 assert read(plan['call'],5,'callsite')==bytes.fromhex(plan['call_bytes'])
 io,request,state,pad=struct.unpack('<4I',read(regs[4],16,'call-arguments'));r['argument_pointers']=[io,request,state,pad];save();assert state==plan['state']['va'] and plan['state']['size']==40
 req=list(struct.unpack('<8I',read(request,32,'request')));r['request']=req;save();assert req[:5]==[2,67108864,57671680,9437184,316160] and req[5:7]==[0,3] and req[7]&4
 values=struct.unpack('<10I',read(state,40,'state'));r['state']=dict(zip(['stage','error','mutated','smb_attempts','smb_completed','sync_polls','vblank_polls','vpll','pcrtc','failure_stage'],values));r['result_signed']=struct.unpack('<i',struct.pack('<I',regs[0]))[0];save()
 r['monitor_registers']=monitor(5084,'info registers')
 assert g.ask('Qqemu.PhyMemMode:1')=='OK';physical=True
 index=read(0xfd6013d4,1,'current-crtc-index')[0];value=read(0xfd6013d5,1,'current-crtc-data')[0];r['current_crtc']=dict(index=index,value=value);r['mmio']={}
 for a in plan['read_mmio']:r['mmio'][hex(a)]=struct.unpack('<I',read(a,4,'mmio-%x'%a))[0]
 r['status']='captured';r['resident_pins_passed']=True;save()
except Exception as e:r.update(status='failed',error=repr(e),traceback=traceback.format_exc());save()
finally:
 if g:
  try:
   if not stopped:r['teardown_stop']=g.interrupt();stopped=True
   for bp in list(points):
    assert g.ask('z1,%x,1'%bp)=='OK';points.remove(bp)
   r['breakpoint_removed']=not points
   if physical:assert g.ask('Qqemu.PhyMemMode:0')=='OK';physical=False
   r['physical_mode_restored']=g.ask('qqemu.PhyMemMode')=='0'
   if stopped:g.send('c');stopped=False;r['resumed']=True
  except Exception as e:r['teardown_error']=repr(e)
  finally:g.s.close()
 r['closed_utc']=utc();save()
print(json.dumps({n:r.get(n) for n in ['status','state','result_signed','current_crtc','mmio','error','breakpoint_removed','physical_mode_restored','resumed']},indent=2))
