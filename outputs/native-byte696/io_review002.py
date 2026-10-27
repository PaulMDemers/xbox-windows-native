"""Actual linked native byte-read/render bytes; explicit Unicorn port models.
Starts after the checked handoff. Does not model Xbox timing, bus or CPU transition.
Exact full transition is exercised separately in fresh diskless CPU fixtures.
"""
import datetime,hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn696/build002')
sys.path.insert(0,str(W/'work/python-packages'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE,UC_HOOK_INSN,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
from oracle import expected_framebuffer
out=K/'io-review002.json';assert not out.exists()
x=json.loads((K/'extract002.json').read_text());blob=(P/'stub.bin').read_bytes();o=x['offsets']
assert x['passed'] and hashlib.sha256(blob).hexdigest()==x['template_sha256']
cases=[]
def case(name,want,**kw):
 d=dict(name=name,want=want,pci_id=0x01b410de,command=0x00b00001,bar=0xc001,entry=0,
        zeros=0,wait_status=0,terminal=0x10,data=1,final=0,base=0x1eff000);d.update(kw);cases.append(d)
case('success',1);case('delayed',1,zeros=3)
case('unknown_bits_preserved',1,entry=0x40,wait_status=0x40,zeros=2,terminal=0x50,final=0x40)
case('last_poll_success',1,zeros=99999)
case('timeout',7,zeros=100000)
case('timeout_late_completion_no_ack',7,zeros=100000,final=0x10)
case('busy',5,entry=0x800);case('busy_and_terminal',5,entry=0x836)
for v in [2,4,0x10,0x20,0x36]:case('inherited_'+hex(v),6,entry=v)
case('wrong_device',2,pci_id=0x70108086)
case('absent_device',2,pci_id=0xffffffff,command=0xffffffff,bar=0xffffffff)
case('io_disabled',3,command=0x00b00000)
case('wrong_bar',4,bar=0xd001);case('bar_not_io',4,bar=0xc000)
for v in [2,4,0x20,0x12,0x14,0x30,0x36,0xff]:case('bus_error_'+hex(v),8,terminal=v)
case('final_busy',9,final=0x800);case('final_pending',9,final=0x10)
case('error_and_final_busy',9,terminal=0x12,final=0x800)
for v in [0,2,255]:case('unexpected_cable_'+str(v),10,data=v)
case('relocated_success',1,base=0x1edc000)
r={'passed':False,'scope':__doc__,'template_sha256':x['template_sha256'],'poll_limit':100000,'cases':[]}
try:
 for c in cases:
  base=c['base'];fb=0x3000000
  u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base-4096,12288);u.mem_map(fb-4096,3686400+8192)
  u.mem_write(base-4096,b'\x5a'*12288);u.mem_write(base,blob)
  u.mem_write(base+0x508,struct.pack('<L',fb));u.mem_write(base+0x540,struct.pack('<L',3))
  u.mem_write(fb-4096,b'\xa5'*4096);u.mem_write(fb+3686400,b'\xa5'*4096)
  initial=bytearray(b'\x20'*3686400)
  for y in range(8,80):initial[(y*1280+8)*4:(y*1280+1272)*4]=struct.pack('<L',0x00ff00)*1264
  u.mem_write(fb,bytes(initial));u.reg_write(UC_X86_REG_EBP,base);u.reg_write(UC_X86_REG_ESP,base+4096);u.reg_write(UC_X86_REG_EFLAGS,2)
  original=0x80005010;selector=[original];pci_events=[];writes=[];counts={'word':0,'poll':0,'data':0,'ack':0}
  steps=[0];done=[False];min_sp=[base+4096];last=[0xffffffff]
  def inp(uc,port,size,user):
   if port==0xcf8 and size==4:
    value=selector[0];pci_events.append(['in',port,value]);return value
   if port==0xcfc and size==4:
    value={0x80000900:c['pci_id'],0x80000904:c['command'],0x80000914:c['bar']}[selector[0]]
    pci_events.append(['in',port,value]);return value
   assert selector[0]==original and c['pci_id']==0x01b410de and c['command']&1 and c['bar']==0xc001
   if port==0xc000 and size==2:
    counts['word']+=1;assert counts['word']<=2
    if counts['word']==1:return c['entry']
    assert counts['ack']==1 or counts['poll']==100000
    return c['final']
   if port==0xc000 and size==1:
    assert writes[:3]==[[0xc004,1,0x21],[0xc008,1,4],[0xc002,1,0x0a]]
    assert not counts['ack'] and not c['entry']&0x836
    counts['poll']+=1;assert counts['poll']<=100000
    last[0]=c['wait_status'] if counts['poll']<=c['zeros'] else c['terminal']
    return last[0]
   if port==0xc006 and size==1:
    assert counts['poll'] and last[0]&0x36==0x10 and not counts['ack']
    counts['data']+=1;assert counts['data']==1;return c['data']
   raise AssertionError(('unexpected read',port,size))
  def output(uc,port,size,value,user):
   if port==0xcf8 and size==4:
    pci_events.append(['out',port,value]);selector[0]=value;return
   assert selector[0]==original and counts['word']==1 and not c['entry']&0x836
   if port==0xc000 and size==2:
    assert counts['poll'] and last[0]&0x36 and value==last[0]&0x36
    counts['ack']+=1;assert counts['ack']==1
   else:
    assert [port,size,value]==[[0xc004,1,0x21],[0xc008,1,4],[0xc002,1,0x0a]][len(writes)]
   writes.append([port,size,value])
  def step(uc,pc,size,user):
   steps[0]+=1;min_sp[0]=min(min_sp[0],uc.reg_read(UC_X86_REG_ESP))
   if pc==base+o['hold']:done[0]=True;uc.emu_stop()
  def write(uc,access,address,size,value,user):
   assert (fb<=address and address+size<=fb+3686400) or (base+0x5a0<=address and address+size<=base+0x5c8) or (base+0xe00<=address and address+size<=base+4096) or (address==base+0x540 and size==4),hex(address)
  u.hook_add(UC_HOOK_INSN,inp,None,1,0,UC_X86_INS_IN);u.hook_add(UC_HOOK_INSN,output,None,1,0,UC_X86_INS_OUT)
  u.hook_add(UC_HOOK_CODE,step);u.hook_add(UC_HOOK_MEM_WRITE,write)
  u.emu_start(base+o['probe'],base+o['code_end'],count=3000000)
  assert done[0] and selector[0]==original and min_sp[0]>=base+0xe00
  expected_pci=[['in',0xcf8,original]]
  for reg,v in [(0x80000900,c['pci_id']),(0x80000904,c['command']),(0x80000914,c['bar'])]:expected_pci.extend([['out',0xcf8,reg],['in',0xcfc,v]])
  expected_pci.append(['out',0xcf8,original]);assert pci_events==expected_pci
  admitted=c['want'] not in [2,3,4,5,6];mapped=c['want'] not in [2,3,4]
  expected_polls=min(c['zeros']+1,100000) if admitted else 0
  terminal=admitted and c['zeros']<100000
  data_read=terminal and not c['terminal']&0x26
  assert counts=={'word':int(mapped)+int(admitted),'poll':expected_polls,'data':int(data_read),'ack':int(terminal)},counts
  raw=struct.unpack('<10L',u.mem_read(base+0x5a0,40))
  expected_raw=(original,c['pci_id'],c['command'],c['bar'],c['entry'] if mapped else 0xffffffff,
                (c['terminal'] if terminal else c['wait_status']) if admitted else 0xffffffff,
                c['data'] if data_read else 0xffffffff,c['final'] if admitted else 0xffffffff,c['want'],expected_polls)
  assert raw==expected_raw,(c['name'],raw,expected_raw)
  assert u.mem_read(fb,3686400)==expected_framebuffer(raw[1:10],c['want'])
  assert u.mem_read(base-4096,4096)==u.mem_read(base+4096,4096)==b'\x5a'*4096
  assert u.mem_read(fb-4096,4096)==u.mem_read(fb+3686400,4096)==b'\xa5'*4096
  assert struct.unpack('<L',u.mem_read(base+0x540,4))[0]==4
  r['cases'].append({'name':c['name'],'input':c,'raw':list(raw),'counts':counts,'writes':writes,
   'instructions':steps[0],'stack_bytes_used':base+4096-min_sp[0],'exact_pixels_and_guards':True,'cf8_restored':True})
  del u
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS linked byte-read/render models:',len(r['cases']))
