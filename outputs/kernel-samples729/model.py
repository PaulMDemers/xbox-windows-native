"""Actual nxdk729 COFF, bounded independent MMIO fault/behavior models.
Simulated CR reads validate guards; they are not physical kernel context evidence.
"""
import datetime,hashlib,json,struct,sys,os,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn729/build001')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'model001.json';assert not out.exists()
b=(P/'probe.obj').read_bytes()
R={'passed':False,'scope':__doc__,'object_sha256':sha(P/'probe.obj'),'harness_sha256':sha(Path(__file__)),'cases':[]}
GPU=0xfd000000;deadline=time.monotonic()+120
def run(name,want=0x729,nmm=2,ncr=1,nunlock=1,flags=0x202,cpu0=0x80010031,cpu3=0xf000,cpu4=0x610,behavior='reassert',fault='',cr_bad=None,mm_bad=None,seq=1,unlock_value=3,delay_at=4):
 assert time.monotonic()<deadline
 machine,nsec,_,symptr,nsyms,optsz,_=struct.unpack_from('<HHLLLHH',b);assert machine==0x14c and not optsz
 strings=b[symptr+18*nsyms:];sections=[];symbols={};indices={};i=0
 for j in range(nsec):
  h=struct.unpack_from('<8sLLLLLLHHL',b,20+40*j)
  sections.append({'base':0x100000+j*0x10000,'size':h[3],'raw':h[4],'reloc':h[5],'count':h[7]})
 while i<nsyms:
  symbol_name,value,sec,typ,storage,aux=struct.unpack_from('<8sLhHBB',b,symptr+18*i)
  symbol_name=(strings[struct.unpack('<L',symbol_name[4:])[0]:] if symbol_name[:4]==b'\0'*4 else symbol_name).split(b'\0')[0].decode()
  if sec>0:indices[i]=sections[sec-1]['base']+value;symbols[symbol_name]=indices[i]
  elif symbol_name=='_memcpy':indices[i]=0x300000
  elif symbol_name=='_memset':indices[i]=0x300100
  i+=aux+1
 c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32)
 c.mem_map(0x300000,4096)
 # Harness cdecl memcpy, preserves ESI/EDI. This is not the nxdk libc implementation.
 c.mem_write(0x300000,bytes.fromhex('57568b7c240c8b7424108b4c241489f8fcf3a45e5fc3'))
 c.mem_write(0x300100,bytes.fromhex('578b7c24088b44240c8b4c241089fafcf3aa89d05fc3'))
 for s in sections:
  c.mem_map(s['base'],0x10000)
  if s['size']:c.mem_write(s['base'],b[s['raw']:s['raw']+s['size']])
 for s in sections:
  for j in range(s['count']):
   off,idx,typ=struct.unpack_from('<LLH',b,s['reloc']+j*10);assert idx in indices
   addr=s['base']+off;old=struct.unpack('<L',c.mem_read(addr,4))[0]
   assert typ in (6,20)
   value=old+indices[idx]-(addr+4 if typ==20 else 0)
   c.mem_write(addr,struct.pack('<L',value&0xffffffff))
 c.mem_map(0x200000,0x40000)

 c.mem_write(0x200000,b'G'*0x40000);c.mem_map(GPU,0x1000000)
 c.mem_write(0x208000,struct.pack('<II',0x20ff00,0x201000))
 c.reg_write(x.UC_X86_REG_ESP,0x208000);c.reg_write(x.UC_X86_REG_EFLAGS,flags)
 FB=0x3000000
 state={'selector':0x12345678,'ticks':0,'seq':seq,'gate':0,'nmm':0,'after_output_reads':0,'cr_attempt':0,'unlock':0,'write_reads':0,'blank_reads':0,'gate_reads':0};trace=[];mw=[];sw=[];outs=[];samples=[];cw=[];io=[]
 cr={9:0x25,0x11:9,0x21:255,0x44:0,0x39:255,0x13:0x80,0x19:0x51,0x25:0x10,0x28:0x83,0x2d:0xe0,0x1b:0x85,0x14:0,0x17:0xe3,0x22:0xfe,0x1f:3}
 if cr_bad:cr[cr_bad[0]]=cr_bad[1]
 sels={0x6013d4:0x67,0xc03c4:0x72,0xc03ce:0x91};original_sels=sels.copy()
 mm={0x680630:3,0x680880:0x21101100,0x680508:0x3c20d,0x68050c:0x100a0400,0x100200:0x3070003,0x600804:3,0x600800:FB,0x680838:1279,0x680818:719}
 if mm_bad:mm[mm_bad[0]]=mm_bad[1]
 def access(uc,kind,addr,width,value,_):
  off=addr-GPU;assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200
  io.append((kind,off,width,value if kind==u.UC_MEM_WRITE else None))
  if kind==u.UC_MEM_WRITE:
   if off in sels:assert width==1;sels[off]=value
   elif off==0xc03c5:
    assert width==1 and sels[0xc03c4]==1 and value in (1,0x21);sw.append(value);state['seq']=value
    if value==1:
     assert state['gate']==4 and state['gate_reads']==1
     if behavior=='on-seq' and state['cr_attempt']:cr[0x1b]=0x85
   elif off==0x6013d5:
    assert width==1 and state['gate']==5 and mm[0x680630]==2
    i=sels[0x6013d4];cw.append((i,value))
    if i==0x1f:
     assert value==0x57 and not state['unlock'];state['unlock']=1;cr[i]=unlock_value
    else:
     assert i==0x1b and value==5 and state['unlock'] and not state['cr_attempt']
     state['cr_attempt']=1
     if behavior!='ignored':cr[i]=value
   else:
    assert off==0x680630 and width==4,('forbidden GPU data write',hex(off),width,value)
    assert value==[2,3][len(mw)];mw.append((off,value));state['nmm']+=1
    if not (fault=='drop2' and value==2 or fault=='restore630' and value==3):mm[off]=value
    if fault=='wide2' and value==2:mm[off]=0x10002
    if value==3 and state['cr_attempt'] and behavior not in ('sticky','on-output','on-seq','blank-delay','late') and fault!='restore630':cr[0x1b]=0x85
   return
  if off in sels:
   assert width==1;value=sels[off]
   if fault=='selector' and off==0x6013d4 and value==0x67 and state['gate']==4:value^=1
  elif off==0xc03c5:
   assert width==1 and sels[0xc03c4]==1;value=state['seq']
   if fault=='blank' and state['gate']==5:value=1
   if fault=='restore_seq' and state['gate']==4:value=0x21
  elif off==0x6013d5:
   assert width==1 and sels[0x6013d4] in cr;i=sels[0x6013d4];value=cr[i]
   if state['gate']==4 and fault=='restore_cr'+str(i):value^=1
   if i==0x11 and fault=='unlock11' and state['unlock'] and state['gate']==5:value^=0x80
   if i==0x1b:
    if state['gate']==5 and state['nmm']==2:
     if behavior=='blank-delay' and state['blank_reads']==delay_at:cr[i]=value=0x85
     state['blank_reads']+=1
    if state['gate']==4 and state['seq']==0x21:state['gate_reads']+=1
    if fault=='prewrite1b' and state['unlock'] and state['nmm']==1 and not state['cr_attempt']:value=5
    if state['gate']==4 and state['seq']==1:
     if behavior=='late' and state['after_output_reads']==4:cr[i]=value=0x85
     if behavior=='oscillate' and state['after_output_reads'] in (2,4,6):value=5
     if fault=='restore1b':value=5
     state['after_output_reads']+=1
    if state['cr_attempt']:
     if behavior=='direct-diff' and state['write_reads']==0:value=0x85
     state['write_reads']+=1
    samples.append((mm[0x680630],value))
  else:
   assert width==4 and off in mm;value=mm[off]
   if off==0x680630 and fault=='postblank630' and state['gate']==5 and not mw:value=2
   if off==0x680630 and fault=='prewrite630' and state['unlock'] and not state['cr_attempt'] and state['gate']==5:value=3
  uc.mem_write(addr,value.to_bytes(width,'little'))
 def pout(uc,port,width,value,_):
  if port==0x80d3:
   assert width==1 and value==[5,4][len(outs)]
   if value==4 and state['nmm']==2:assert state['blank_reads']==33
   outs.append(value);state['gate']=value
   if value==4 and behavior=='on-output' and state['cr_attempt']:cr[0x1b]=0x85
   return
  raise AssertionError('unexpected port')

 steps=[0,0]
 regs=[x.UC_X86_REG_EAX,x.UC_X86_REG_ECX,x.UC_X86_REG_EDX,x.UC_X86_REG_EBX,x.UC_X86_REG_ESP,x.UC_X86_REG_EBP,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI]
 def code(uc,pc,n,_):
  steps[0]+=1;raw=bytes(uc.mem_read(pc,n));assert raw[:2]!=b'\x0f\x22'
  if raw[:2]==b'\x0f\x20':
   mod=raw[2];assert mod>>6==3;reg=(mod>>3)&7;assert reg in (0,3,4)
   uc.reg_write(regs[mod&7],{0:cpu0,3:cpu3,4:cpu4}[reg]);uc.reg_write(x.UC_X86_REG_EIP,pc+n)
  if not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200:steps[1]+=1
 def ramwrite(uc,kind,addr,size,value,_):
  if GPU<=addr<GPU+0x1000000:return
  assert (0x201000<=addr and addr+size<=0x2011f4) or (0x207000<=addr and addr+size<=0x208008),(hex(addr),size)
 c.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,None,GPU,GPU+0xffffff)
 c.hook_add(u.UC_HOOK_MEM_WRITE,ramwrite);c.hook_add(u.UC_HOOK_CODE,code)
 c.hook_add(u.UC_HOOK_INSN,pout,None,1,0,x.UC_X86_INS_OUT)
 c.emu_start(symbols['_probe729'],0x20ff00,timeout=2000000,count=15000)
 assert c.reg_read(x.UC_X86_REG_EIP)==0x20ff00 and c.reg_read(x.UC_X86_REG_ESP)==0x208004
 v=list(struct.unpack('<125I',c.mem_read(0x201000,500)))
 assert v[0]==want,(name,hex(v[0]),hex(want))
 assert v[2]==v[4] and not v[3]&0x200 and v[2]&0x200==flags&0x200
 assert v[5:8]==[cpu0,cpu3,cpu4]
 assert c.reg_read(x.UC_X86_REG_EFLAGS)&0x200==flags&0x200
 assert sels==original_sels
 assert bytes(c.mem_read(0x200000,0x1000))==b'G'*0x1000
 assert bytes(c.mem_read(0x2011f4,0x5e0c))==b'G'*0x5e0c
 assert bytes(c.mem_read(0x208008,0xff8))==b'G'*0xff8
 assert state['nmm']==nmm and state['cr_attempt']==ncr and state['unlock']==nunlock,(name,state)
 assert cw==([(0x1f,0x57)] if nunlock else [])+([(0x1b,5)] if ncr else [])
 if ncr:
  at=next(i for i,v in enumerate(io) if v==(u.UC_MEM_WRITE,0x6013d5,1,5))
  assert io[at+1:at+4]==[(u.UC_MEM_READ,0x6013d5,1,None),(u.UC_MEM_WRITE,0x6013d4,1,0x1b),(u.UC_MEM_READ,0x6013d5,1,None)]
 assert mw==[(0x680630,v) for v in (2,3)][:nmm]
 assert sw in ([],[0x21,1]) and outs in ([],[5,4])
 if nmm==2:
  # Independent explicit stage vectors; late samples are observations, not admission guesses.
  pairs=[(3,0x85),(3,0x85),(2,0x85),(3,0x85),(3,0x85),(3,0x85)]
  changes=0
  if behavior=='sticky':pairs[3:]=[(3,5)]*3
  if behavior in ('on-output','on-seq','blank-delay'):pairs[3]=(3,5)
  if behavior=='late':pairs[3:5]=[(3,5)]*2;changes=1
  if behavior=='oscillate':changes=6
  if fault=='drop2':pairs[2]=(3,0x85)
  if fault=='wide2':pairs[2]=(0x10002,0x85)
  if fault=='restore630':pairs[3:]=[(2,5)]*3
  if fault=='restore1b':pairs[4:]=[(3,5)]*2
  assert v[20:26]==[a for a,b in pairs] and v[26:32]==[b for a,b in pairs],(name,v[20:32],pairs)
  assert v[32:38]==[(a<<16)|b if a<=0xffff else 0xffffffff for a,b in pairs]
  assert v[38:40]==[32,changes]
 if nmm==2:
  expected_blank=[0x85]*32;initial_blank=0x85
  if behavior in ('sticky','on-output','on-seq','late','blank-delay') or fault=='restore630':expected_blank=[5]*32;initial_blank=5
  if behavior=='blank-delay':expected_blank=[0x85 if i+1>=delay_at else 5 for i in range(32)]
  expected_mm=2 if fault=='restore630' else 3
  sequence=[initial_blank]+expected_blank
  expected_changes=sum(a!=b for a,b in zip(sequence,sequence[1:]))
  assert v[54:86]==[expected_mm]*32 and v[86:118]==expected_blank,(name,v[54:118])
  assert v[118:122]==[32,expected_changes,min(sequence),max(sequence)]
  gate_value=expected_blank[-1]
  if behavior=='on-output':gate_value=0x85
  assert v[122:125]==[expected_mm,gate_value,0x21],(name,v[122:125],gate_value)
  assert state['blank_reads']==33 and state['gate_reads']==1
 else:
  assert v[54:118]==[0xffffffff]*64 and v[118:122]==[0]*4
  if outs:assert v[122:125]==[3,0x85,0x21]
  else:assert v[122:125]==[0xffffffff]*3
 if nunlock:assert v[45]==unlock_value
 if ncr:
  reads=[0x85,0x85] if behavior=='ignored' else [0x85,5] if behavior=='direct-diff' else [5,5]
  assert v[47:50]==[2,0x85,0x20085] and v[50:52]==reads
  assert v[52]==(reads[0]<<16)|reads[1]
 if want==0x729:assert v[18:20]==[1,1]
 if want>=0x729:assert v[42]==v[18]|(v[19]<<1)|((v[38]==32 and v[39]==0)<<2)|(v[38]<<8)|(v[1]<<16)|(ncr<<24)
 if want>=0x729:assert v[43:45]==[ncr,nunlock] and v[53]==nmm|(ncr<<8)|(nunlock<<16)

 R['cases'].append({'name':name,'code':v[0],'raw_result':v,'mmio_writes':mw,'crtc_data_writes':cw,'direct_indexed_order_exact':bool(ncr),'steps':steps[0],'critical_instructions':steps[1]})
try:
 run('unlock57',unlock_value=0x57)
 run('on-seq',behavior='on-seq')
 for delay in (1,4,32):run('blank-delay-'+str(delay),behavior='blank-delay',delay_at=delay)
 for f in (0x202,0x246,2):run('reassert-flags-'+hex(f),flags=f)
 for behavior,want in [('sticky',0x7295),('on-output',0x729),('late',0x729),('oscillate',0x729),('ignored',0x7298),('direct-diff',0x7298)]:run('behavior-'+behavior,behavior=behavior,want=want)
 for a,val in [(0x1b,5),(0x22,255),(0x19,0x50)]:run('baseline-cr'+hex(a),want=0x7292,nmm=0,ncr=0,nunlock=0,cr_bad=(a,val))
 run('baseline630',want=0x7292,nmm=0,ncr=0,nunlock=0,mm_bad=(0x680630,2))
 run('baseline-seq',want=0x7292,nmm=0,ncr=0,nunlock=0,seq=0)
 for fault,want,mm,cr,unlock in [('blank',0x7293,0,0,0),('postblank630',0x7293,0,0,0),('restore630',0x7295,2,1,1),('restore_seq',0x7295,2,1,1),('restore1b',0x7295,2,1,1),('drop2',0x7298,2,0,0),('wide2',0x7298,2,0,0),('prewrite1b',0x7299,2,0,1),('prewrite630',0x7299,2,0,1),('unlock11',0x7299,2,0,1),('selector',0x7296,2,1,1)]:run(fault,want=want,nmm=mm,ncr=cr,nunlock=unlock,fault=fault)
 for i in (0x11,0x22,0x19):run('restore-cr'+hex(i),want=0x7295,fault='restore_cr'+str(i))

 for cr0 in (0,1,0x40000001,0x80000000):run('cpu0-'+hex(cr0),cpu0=cr0,want=0x7291,nmm=0,ncr=0,nunlock=0)
 run('PAE-refused',cpu4=0x630,want=0x7291,nmm=0,ncr=0,nunlock=0)
 run('other-kernel-CR3',cpu3=0x23000)
 R['passed']=True;R['case_count']=len(R['cases'])
except BaseException as e:R['failure']=repr(e);raise
finally:R['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(R,indent=2)+'\n')
print('PASS compiled729 cases',len(R['cases']))
