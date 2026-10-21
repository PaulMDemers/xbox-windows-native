"""Fresh owned emulator: actual compiled wrong-kernel refusal, not4034 proof."""
import datetime,hashlib,json,struct,sys,time,traceback
from pathlib import Path
from protocol import Remote,monitor
K=Path(__file__).resolve().parent;assert sys.argv[1:] == ['emu001']
O=K/'emu001';P=Path('C:/xwn632/emu001');assert not (O/'trace.json').exists()
review=json.loads((K/'binary-review001.json').read_text());xbe=(P/'default.xbe').read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(xbe)==review['xbe_sha256']
r=dict(passed=False,physical_access=False,guest_memory_writes=False,guest_register_writes=False,mode_changes=False,scope='Native4627 rejection before memory reader; not4034 extraction or Windows proof',captures=[])
g=None;point=False;stopped=True
def save():(O/'trace.json').write_text(json.dumps(r,indent=2)+'\n')
def read(a,n,label):
 data=g.read(a,n);p=P/'private'/(label+'.bin');assert not p.exists();p.write_bytes(data)
 r['captures'].append(dict(path=str(p),bytes=len(data),sha256=sha(data)));save();return data
try:
 g=Remote(5637);r['initial_stop']=g.ask('?');assert g.ask('qqemu.PhyMemMode')=='0'
 point=True;assert g.ask('Z1,%x,1'%review['checkpoint']['va'])=='OK'
 g.send('c');stopped=False;r['stop']=g.recv(90);stopped=True
 regs=struct.unpack('<16I',bytes.fromhex(g.ask('g'))[:64]);assert regs[8]==review['checkpoint']['va']
 caller,phase,address=struct.unpack('<3I',read(regs[4],12,'stack'))
 assert phase==255 and address==review['record']
 assert read(regs[8],12,'checkpoint')==bytes.fromhex(review['checkpoint']['bytes'])
 call=next(c for c in review['calls'] if caller==c['va']+5)
 assert read(caller-5,5,'caller')==bytes.fromhex(call['bytes'])
 header=read(0x10000,4096,'header');assert header[:4]==b'XBEH'
 for offset in (0x104,0x108,0x10c,0x11c,0x120):assert header[offset:offset+4]==xbe[offset:offset+4]
 table=struct.unpack_from('<I',header,0x120)[0]-0x10000
 for i in range(4):
  at=table+56*i
  assert header[at:at+24]==xbe[at:at+24] and header[at+28:at+56]==xbe[at+28:at+56]
  assert struct.unpack_from('<I',header,at+24)[0]==1
 text=next(s for s in review['sections'] if s['name']=='.text')
 assert sha(read(text['va'],text['raw_size'],'text'))==text['sha256']
 raw=read(address,192,'record');words=struct.unpack('<7I',raw[:28])
 r['record_header']=words;save()
 assert words[:4]==(0x632c0de,0,1,4627)
 assert words[6]==0 and raw[28:]==bytes(164)
 assert words[4:6]==(0,0),'Read-only optical D log expected unavailable'
 r.update(passed=True,native_wrong_kernel_refused=True,kernel_memory_reader_calls=0,output_profile_zero=True)
except BaseException as e:r['failure']=repr(e);r['traceback']=traceback.format_exc()
finally:
 try:
  if g:
   if not stopped:r['interrupt']=g.interrupt();stopped=True
   if point:assert g.ask('z1,%x,1'%review['checkpoint']['va'])=='OK';point=False
   r['physical_mode_zero']=g.ask('qqemu.PhyMemMode')=='0'
   g.send('c');stopped=False;g.s.close();g=None;time.sleep(5)
  r['final_status']=monitor(5636,'info status');monitor(5636,'stop');monitor(5636,'quit',True);r['orderly_quit_sent']=True
 except BaseException as e:r['cleanup_error']=repr(e)
 r['remaining_breakpoint']=point;r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps({n:r.get(n) for n in ('passed','failure','cleanup_error')}))
assert r['passed'] and not r.get('cleanup_error')
