"""Native initialization observation only; no Windows boot, no guest patch."""
import datetime,hashlib,json,struct,sys,traceback
from pathlib import Path
from protocol import Remote,monitor
K=Path(__file__).resolve().parent;assert sys.argv[1:]==['emu002']
O=K/'emu002';P=Path('C:/xwn633/emu002');assert not (O/'trace.json').exists()
review=json.loads((K/'review001.json').read_text());elf=(P/'image-crom.elf').read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(elf)==review['elf_sha256']
r=dict(passed=False,physical_access=False,mode_programming=True,guest_memory_writes=False,guest_register_writes=False,windows_boot=False,normal_shutdown=False,captures=[])
g=None;point=False;stopped=True
def save():(O/'trace.json').write_text(json.dumps(r,indent=2)+'\n')
def read(a,n,label):
 assert 0<n<=1048576
 data=b''.join(g.read(a+off,min(65536,n-off)) for off in range(0,n,65536));p=P/'private'/(label+'.bin');assert not p.exists();p.write_bytes(data)
 r['captures'].append(dict(path=str(p),bytes=len(data),sha256=sha(data)));save();return data
try:
 g=Remote(5639);r['initial_stop']=g.ask('?');assert g.ask('qqemu.PhyMemMode')=='0'
 point=True;assert g.ask('Z1,%x,1'%review['ret'])=='OK'
 g.send('c');stopped=False;r['stop']=g.recv(120);stopped=True
 regs=struct.unpack('<16I',bytes.fromhex(g.ask('g'))[:64]);assert regs[8]==review['ret'] and regs[0]==1
 assert read(regs[8],1,'return')==b'\xc3'
 s=review['sections']['.text'];expected=elf[s['offset']:s['offset']+s['size']]
 assert read(s['va'],s['size'],'native-text')==expected
 state=struct.unpack('<9I',read(review['symbols']['XwnHdState311']['va'],36,'state'));r['state']=state;save()
 assert state[:5]==(5,0,1,19,19) and 1<=state[5]<=10000 and 6<=state[6]<=600000
 mode=struct.unpack('<8I',read(review['symbols']['vmode']['va'],32,'vmode'));r['vmode_prefix']=mode;assert mode[4:8]==(720,480,0,0)
 fp=struct.unpack('<16I',read(0xfd680800,64,'fp'));r['fp']=fp
 actual=json.loads((K.parent/'mode-switch631/physical-collection002.json').read_text())['decoded']['stages'][0]['fp'];assert list(fp)==actual
 scanout=struct.unpack('<I',read(0xfd600800,4,'scanout'))[0];assert scanout==55<<20
 general=struct.unpack('<I',read(0xfd680600,4,'general'))[0];assert general==0x100030
 r['crtc_index']=read(0xfd6013d4,1,'crtc-index')[0];assert r['crtc_index']==0x28
 r['crtc_format']=read(0xfd6013d5,1,'crtc-format')[0];assert r['crtc_format']==0x83
 r.update(passed=True,scanout=scanout,width=720,height=480,pitch_verified_by_compiled_adapter=2880,actual_partial_register_readback=True,native_success_before_windows=True)
except BaseException as e:r['failure']=repr(e);r['traceback']=traceback.format_exc()
finally:
 try:
  if g:
   if not stopped:r['interrupt']=g.interrupt();stopped=True
   if point:assert g.ask('z1,%x,1'%review['ret'])=='OK';point=False
   r['physical_mode_zero']=g.ask('qqemu.PhyMemMode')=='0';g.s.close();g=None
  # This intentionally bounded preflight ends before executing the return to boot.
  r['final_status']=monitor(5638,'info status');monitor(5638,'quit',True);r['orderly_quit_sent']=True
 except BaseException as e:r['cleanup_error']=repr(e)
 r['remaining_breakpoint']=point;r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps({n:r.get(n) for n in ('passed','failure','cleanup_error')}))
assert r['passed'] and not r.get('cleanup_error')
