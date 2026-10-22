"""Fresh exact-linked indication execution: only raw IN/OUT hardware is modeled.
No callback/function replacement, physical access or closed runtime reopening.
"""
import datetime,hashlib,json,re,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('C:/xwn659/build001')
sys.path[:0]=[str(W/'work/python-packages'),str(W/'outputs/udp655')]
import unicorn as u
from unicorn import x86_const as x
from receiver import decode
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=json.loads((K/'build001.json').read_text());cfg=json.loads(Path('C:/xwn659/config.json').read_text())
assert build['status']=='compiled-unqualified' and sha(B/'image-crom.bin')==build['artifacts']['image-crom.bin']['sha256']
blob=(B/'image-crom.bin').read_bytes();elf='/mnt/c/xwn659/build001/image-crom.elf'
nm=subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-n',elf],text=True,timeout=25)
sym={a[2]:int(a[0],16) for line in nm.splitlines() if len(a:=line.split())==3}
dis=subprocess.check_output(['wsl','-d','Ubuntu','--','objdump','-d','--disassemble=XwnExport657',elf],text=True,timeout=25)
halts=re.findall(r'^\s*([0-9a-f]+):\s+f4\s+hlt',dis,re.M);assert len(halts)==1;halt=int(halts[0],16)
out=K/'compiled001.json';assert not out.exists()
r=dict(passed=False,physical_access=False,source_sha256=sha(Path(__file__)),image_sha256=sha(B/'image-crom.bin'),cases=[],scope='Exact linked freeze/encode/entry latch/original show658/delay656/final latch/halt. Only raw hardware IN/OUT responses modeled; no physical timing or LED proof.')
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 for name in ['normal','wrap','frozen','backward','show-busy','show-status','show-completion','entry-busy','final-busy','encoder-reject']:
  uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x02600000,0x100000);uc.mem_write(0x02600000,blob)
  uc.mem_map(0x027f0000,0x10000);esp=0x027fe000;end=0x026ff000
  sizes=[8,9,63,47,47];ptrs=[0x026f0000+i*0x400 for i in range(5)];raw=[]
  for i,(ptr,n) in enumerate(zip(ptrs,sizes)):
   values=[i*1000+j for j in range(n)];raw.append(values);uc.mem_write(ptr,struct.pack('<'+'I'*n,*values))
  result=2 if name=='encoder-reject' else -1
  uc.mem_write(esp,struct.pack('<7I',end,result&0xffffffff,*ptrs));uc.reg_write(x.UC_X86_REG_ESP,esp);uc.reg_write(x.UC_X86_REG_EFLAGS,2)
  d=dict(halted=False,reads=0,timer_reads=0,tick=0xfffff000 if name=='wrap' else 100,ports=[],byphase={},packet=None)
  def word(a):return struct.unpack('<I',uc.mem_read(a,4))[0]
  def phase():return word(sym['Phase659'])
  def inp(uc,port,size,user):
   ph=phase();assert ph in [2,3,4];d['reads']+=1;d['byphase'][ph]=d['byphase'].get(ph,0)+1
   if port==0x8008:
    assert ph==3 and size==4;d['timer_reads']+=1
    if name=='backward':d['tick']-=1
    elif name!='frozen':d['tick']+=4000
    return d['tick']&0xffffffff
   assert port==0xc000 and size in [1,2]
   if size==2:
    return 0x800 if (ph==2 and name=='entry-busy') or (ph==4 and name=='final-busy') or (ph==3 and name=='show-busy') else 0
   return 0x26 if ph==3 and name=='show-status' else 0 if ph==3 and name=='show-completion' else 0x10
  def output(uc,port,size,value,user):
   ph=phase();assert ph in [2,3,4]
   assert port in [0xc004,0xc008,0xc006,0xc000,0xc002]
   assert size==(2 if port in [0xc006,0xc000] else 1)
   if port==0xc008:assert value in [7,8] # no reset command
   if port==0xc004:assert value==0x20
   if port==0xc002:assert value==0x1a
   if d['packet'] is None:d['packet']=bytes(uc.mem_read(sym['Packet657'],772))
   else:assert d['packet']==bytes(uc.mem_read(sym['Packet657'],772))
   d['ports'].append([ph,port,size,value])
  def stopped(uc,a,size,user):d['halted']=True;uc.emu_stop()
  def forbidden(uc,a,size,user):raise AssertionError('network code entered')
  uc.hook_add(u.UC_HOOK_INSN,inp,None,1,0,x.UC_X86_INS_IN);uc.hook_add(u.UC_HOOK_INSN,output,None,1,0,x.UC_X86_INS_OUT)
  uc.hook_add(u.UC_HOOK_CODE,stopped,None,halt,halt)
  uc.hook_add(u.UC_HOOK_CODE,forbidden,None,sym['NativeSend656'],sym['NativeSend656'])
  uc.emu_start(sym['XwnExport657'],end,timeout=45000000,count=20000000)
  assert d['halted'] and phase()==5 and uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200==0
  expected_show={'frozen':1,'backward':1,'show-busy':2,'show-status':3,'show-completion':4}.get(name,0)
  expected_mask={'frozen':0x50,'backward':0x50,'show-busy':0xa5,'show-status':0xf5,'show-completion':0x5f,'entry-busy':0x55,'encoder-reject':0xf0}.get(name,15)
  assert word(sym['ShowError659'])==expected_show and word(sym['Mask659'])==expected_mask
  assert word(sym['EntryError659'])==(2 if name=='entry-busy' else 0)
  assert word(sym['FinalError659'])==(2 if name=='final-busy' else 0)
  if name!='encoder-reject':
   assert word(sym['Encode659'])==0
   packet=bytes(uc.mem_read(sym['Packet657'],772));assert packet==d['packet']
   parsed=decode(packet,bytes.fromhex(cfg['attempt']),bytes.fromhex(cfg['build_id']))
   for key,values in zip(['request','state','trace','pre','post'],raw):assert parsed[key]==values,key
   assert parsed['result']==-1 and parsed['post_kind']==2
  else:assert word(sym['Encode659'])==0xffffffff and d['timer_reads']==0
  for ph in [2,3,4]:
   ports=[v[1:] for v in d['ports'] if v[0]==ph]
   assert len(ports)%5==0
   for i in range(0,len(ports),5):assert [v[0] for v in ports[i:i+5]]==[0xc004,0xc008,0xc006,0xc000,0xc002]
  if name in ['normal','wrap']:
   assert d['timer_reads']==12000 and len(d['ports'])==35
  if name=='frozen':assert d['timer_reads']==200001
  if name=='backward':assert d['timer_reads']==2
  assert d['reads']<300000
  r['cases'].append(dict(name=name,halted=True,show_error=expected_show,final_mask=expected_mask,entry_error=word(sym['EntryError659']),final_error=word(sym['FinalError659']),timer_reads=d['timer_reads'],raw_reads=d['reads'],out_instructions=len(d['ports']),no_network_or_reset=True));save()
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print('PASS',len(r['cases']),'exact linked control cases')
