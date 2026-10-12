"""Owned HD-mode diagnostic: native pins, page translations and full pixel oracle."""
import datetime,hashlib,json,re,struct,sys,time,traceback
from pathlib import Path
from protocol import Remote,monitor
from oracle import oracle
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case=='emu001'
out=k/case;root=Path('E:/xwn289')/case;private=root/'private'
sys.path.insert(0,str(k.parent/'surface-bridge260'));from atomic_json import write_json
sys.path.insert(0,str(k.parent/'owned-runtime272'));from model import translate
review=json.loads((k/'binary-review001.json').read_text());xbe=(root/'default.xbe').read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(xbe)==review['xbe_sha256'] and not (out/'trace.json').exists()
r=dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),passed=False,
 guest_memory_writes=False,guest_register_writes=False,mode_changes=True,physical_access=False,
 scope='Standalone stock-kernel mode API and framebuffer memory; not physical interlace/Windows handoff',stops=[],captures=[])
g=None;point=False;stopped=True;physical=False

def save():write_json(out/'trace.json',r)
def capture(data,label):
 p=private/(label+'.bin');assert not p.exists();p.write_bytes(data)
 r['captures'].append(dict(path=str(p),bytes=len(data),sha256=sha(data)));save();return data

def read(a,n,label):return capture(g.read(a,n),label)
def cmd(s,quit=False):
 response=monitor(4894,s,quit);r.setdefault('commands',[]).append(dict(command=s,reply=response));save();return response
try:
 g=Remote(4895);r['initial_stop']=g.ask('?');assert g.ask('qqemu.PhyMemMode')=='0'
 point=True;assert g.ask('Z1,%x,1'%review['checkpoint']['va'])=='OK'
 for index,expected_phase in enumerate([11,22,33,44]):
  g.send('c');stopped=False;stop=g.recv(90);stopped=True
  regs=struct.unpack('<16I',bytes.fromhex(g.ask('g'))[:64]);assert regs[8]==review['checkpoint']['va']
  prefix='stop'+str(index+1)
  caller,phase,record=struct.unpack('<3I',read(regs[4],12,prefix+'-stack'))
  row=dict(phase=phase,caller=caller,record_address=record);r['stops'].append(row);save()
  assert record==review['record']
  assert read(regs[8],12,prefix+'-checkpoint')==bytes.fromhex(review['checkpoint']['bytes'])
  call=next(c for c in review['calls'] if caller==c['va']+5)
  assert read(caller-5,5,prefix+'-caller')==bytes.fromhex(call['bytes'])
  header=read(0x10000,4096,prefix+'-header');assert header[:4]==b'XBEH'
  for offset in [0x104,0x108,0x10c,0x11c,0x120]:assert header[offset:offset+4]==xbe[offset:offset+4]
  table=struct.unpack_from('<I',header,0x120)[0]-0x10000
  for i in range(4):
   at=table+56*i
   assert header[at:at+24]==xbe[at:at+24] and header[at+28:at+56]==xbe[at+28:at+56]
   assert struct.unpack_from('<I',header,at+24)[0]==1
  text=next(s for s in review['sections'] if s['name']=='.text')
  assert sha(read(text['va'],text['raw_size'],prefix+'-text'))==text['sha256']
  h=list(struct.unpack('<36I',read(record,144,prefix+'-record')));row['record']=h;save()
  assert phase==expected_phase,('Guest refusal/error',phase,h[4])
  assert h[:4]==[0x289c0de,1,144,[0,11,22,33][index]] and h[4]==0
  assert (h[6]&255)==4 and h[6]&0xe0000==0xe0000 and h[18]==16384
  if phase==44:continue
  w,height=[(1280,720),(1920,1080),(640,480)][index];n=w*height*4
  assert h[5]==index+1 and h[7]==index+1 and h[8:12]==[w,height,32,60] and h[19]==0
  va,pa,allocation,scanout=h[12:16]
  assert 0<pa<0x4000000-n and n<=allocation<=n+4095 and scanout==pa
  register_text=cmd('info registers')
  cr={name:int(value,16) for name,value in re.findall(r'\b(CR0|CR3|CR4)=([0-9a-fA-F]+)',register_text)}
  assert cr['CR0']&0x80000000;row['paging']=cr
  cache={}
  def physical_word(a,length):
   global physical
   assert length==4 and a+4<=0x4000000
   page=a&~4095
   if page not in cache:
    assert g.ask('Qqemu.PhyMemMode:1')=='OK';physical=True
    try:cache[page]=read(page,4096,prefix+'-pagetable-'+hex(page))
    finally:assert g.ask('Qqemu.PhyMemMode:0')=='OK';physical=False
   return cache[page][a-page:a-page+4]
  row['translations']=[]
  for offset in list(range(0,n,4096))+[n-1]:
   translated,detail=translate(physical_word,cr['CR3'],cr['CR4'],va+offset)
   assert translated==pa+offset
   row['translations'].append(dict(virtual=va+offset,physical=translated,**detail))
  save()
  dest=private/(prefix+'-framebuffer.bin');assert not dest.exists()
  cmd('pmemsave 0x%x 0x%x "%s"'%(pa,n,dest.as_posix()))
  data=dest.read_bytes();r['captures'].append(dict(path=str(dest),bytes=len(data),sha256=sha(data)));save()
  assert len(data)==n and data==oracle(w,height),'Independent full pixel mismatch'
  assert read(va,4096,prefix+'-virtual-first')==data[:4096]
  assert read(va+n-4096,4096,prefix+'-virtual-last')==data[-4096:]
  row.update(exact_framebuffer_bytes=n,all_pages_translated=True,physical_equals_scanout=True);save()
 r['passed']=True;save()
except BaseException as e:r['error']=repr(e);r['traceback']=traceback.format_exc();save()
finally:
 try:
  if g:
   if not stopped:r['interrupt']=g.interrupt();stopped=True
   if physical:assert g.ask('Qqemu.PhyMemMode:0')=='OK';physical=False
   if point:assert g.ask('z1,%x,1'%review['checkpoint']['va'])=='OK';point=False
   r['physical_mode_restored']=g.ask('qqemu.PhyMemMode')=='0'
   g.send('c');stopped=False;g.s.close();g=None
   time.sleep(12)
  r['final_status']=cmd('info status');cmd('stop');cmd('quit',True);r['orderly_quit_sent']=True
 except BaseException as e:r['cleanup_error']=repr(e)
 r['remaining_breakpoint']=point;r['closed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps({n:r.get(n) for n in ['passed','error','cleanup_error']},indent=2))
