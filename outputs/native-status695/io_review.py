"""Execute exact linked native read/render bytes under Unicorn with explicit IO models.
This starts AFTER the handoff checkpoint. It does not model CPU transition or hardware.
Separate diskless CPU fixtures exercise the entire linked transition.
"""
import datetime,hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn695/build001')
sys.path.insert(0,str(W/'work/python-packages'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE,UC_HOOK_INSN,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
from oracle import expected_framebuffer
sha=lambda b:hashlib.sha256(b).hexdigest()
out=K/'io-review001.json';assert not out.exists()
x=json.loads((K/'extract001.json').read_text());blob=(P/'stub.bin').read_bytes()
assert x['passed'] and sha(blob)==x['template_sha256']
o=x['offsets'];r={'passed':False,'scope':__doc__,'template_sha256':sha(blob),'cases':[]}
cases=[('clean',0x01b410de,0x00b00001,0xc001,0,1),
 ('unknown_bit_preserved',0x01b410de,1,0xc001,0x40,1),
 ('busy',0x01b410de,1,0xc001,0x800,5),
 ('busy_and_terminal',0x01b410de,1,0xc001,0x836,5),
 *[('terminal_'+hex(v),0x01b410de,1,0xc001,v,6) for v in [2,4,0x10,0x20,0x36]],
 ('wrong_device',0x70108086,1,0xc001,0,2),
 ('absent_device',0xffffffff,0xffffffff,0xffffffff,0xffff,2),
 ('io_disabled',0x01b410de,0x00b00000,0xc001,0,3),
 ('wrong_bar',0x01b410de,1,0xd001,0,4),
 ('bar_not_io',0x01b410de,1,0xc000,0,4),
 ('status_all_ones',0x01b410de,1,0xc001,0xffff,5),
 ('relocated',0x01b410de,1,0xc001,0,1)]
try:
 for name,pci_id,cmd,bar,status,want in cases:
  base=0x1edc000 if name=='relocated' else 0x1eff000;fb=0x3000000
  u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base-4096,12288);u.mem_map(fb-4096,3686400+8192)
  u.mem_write(base-4096,b'\x5a'*12288);u.mem_write(base,blob)
  u.mem_write(base+0x508,struct.pack('<L',fb));u.mem_write(base+0x540,struct.pack('<L',3))
  u.mem_write(fb-4096,b'\xa5'*4096);u.mem_write(fb+3686400,b'\xa5'*4096)
  initial=bytearray(b'\x20'*3686400)
  for y in range(8,80):initial[(y*1280+8)*4:(y*1280+1272)*4]=struct.pack('<L',0x00ff00)*1264
  u.mem_write(fb,bytes(initial));u.reg_write(UC_X86_REG_EBP,base);u.reg_write(UC_X86_REG_ESP,base+4096)
  u.reg_write(UC_X86_REG_EFLAGS,2)
  original=0x80005010;selector=[original];events=[];steps=[0];done=[False];min_sp=[base+4096]
  def inp(uc,port,size,user):
   if port==0xcf8 and size==4:value=selector[0]
   elif port==0xcfc and size==4:
    assert selector[0] in [0x80000900,0x80000904,0x80000914]
    value={0x80000900:pci_id,0x80000904:cmd,0x80000914:bar}[selector[0]]
   elif port==0xc000 and size==2:
    assert pci_id==0x01b410de and cmd&1 and bar==0xc001
    value=status
   else:raise AssertionError(('unexpected read',port,size))
   events.append(['in',port,size,value]);return value
  def output(uc,port,size,value,user):
   assert port==0xcf8 and size==4,('forbidden device/status write',port,size,value)
   events.append(['out',port,size,value]);selector[0]=value
  def step(uc,pc,size,user):
   steps[0]+=1;min_sp[0]=min(min_sp[0],uc.reg_read(UC_X86_REG_ESP))
   if pc==base+o['hold']:done[0]=True;uc.emu_stop()
  def write(uc,access,address,size,value,user):
   assert (fb<=address and address+size<=fb+3686400) or (base+0x5a0<=address and address+size<=base+0x5b8) or (base+0xe00<=address and address+size<=base+4096) or (address==base+0x540 and size==4),hex(address)
  u.hook_add(UC_HOOK_INSN,inp,None,1,0,UC_X86_INS_IN)
  u.hook_add(UC_HOOK_INSN,output,None,1,0,UC_X86_INS_OUT)
  u.hook_add(UC_HOOK_CODE,step);u.hook_add(UC_HOOK_MEM_WRITE,write)
  u.emu_start(base+o['probe'],base+o['code_end'],count=1000000)
  assert done[0] and selector[0]==original and min_sp[0]>=base+0xe00
  raw=struct.unpack('<6L',u.mem_read(base+0x5a0,24));actual_status=status if want in [1,5,6] else 0xffffffff
  assert raw==(original,pci_id,cmd,bar,actual_status,want)
  expected_events=[['in',0xcf8,4,original]]
  for reg,val in [(0x80000900,pci_id),(0x80000904,cmd),(0x80000914,bar)]:
   expected_events.extend([['out',0xcf8,4,reg],['in',0xcfc,4,val]])
  expected_events.append(['out',0xcf8,4,original])
  if want in [1,5,6]:expected_events.append(['in',0xc000,2,status])
  assert events==expected_events
  assert u.mem_read(fb,3686400)==expected_framebuffer(raw[1:5],want)
  assert u.mem_read(base-4096,4096)==u.mem_read(base+4096,4096)==b'\x5a'*4096
  assert u.mem_read(fb-4096,4096)==u.mem_read(fb+3686400,4096)==b'\xa5'*4096
  assert struct.unpack('<L',u.mem_read(base+0x540,4))[0]==4
  r['cases'].append({'name':name,'result':want,'raw':list(raw),'instructions':steps[0],
   'stack_bytes_used':base+4096-min_sp[0],'events':events,'exact_pixels_and_guards':True})
  del u
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS exact native IO and rendering in',len(r['cases']),'models; no device/status writes')
