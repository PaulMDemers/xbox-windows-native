"""Fresh exact-linked latch caller execution with modeled raw IN/OUT and sender.
No physical access or closed runtime reopening; unchanged native sender is not emulated here.
"""
import datetime,hashlib,json,re,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('C:/xwn665/build001')
sys.path[:0]=[str(W/'work/python-packages'),str(W/'outputs/udp655')]
import unicorn as u
from unicorn import x86_const as x
from receiver import decode
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=json.loads((K/'build001.json').read_text());cfg=json.loads(Path('C:/xwn665/config.json').read_text())
assert build['status']=='compiled-unqualified' and sha(B/'image-crom.bin')==build['artifacts']['image-crom.bin']['sha256']
blob=(B/'image-crom.bin').read_bytes();elf='/mnt/c/xwn665/build001/image-crom.elf'
nm=subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-n',elf],text=True,timeout=25)
sym={a[2]:int(a[0],16) for line in nm.splitlines() if len(a:=line.split())==3}
dis=subprocess.check_output(['wsl','-d','Ubuntu','--','objdump','-d','--disassemble=XwnExport657',elf],text=True,timeout=25)
halts=re.findall(r'^\s*([0-9a-f]+):\s+f4\s+hlt',dis,re.M);assert len(halts)==1;halt=int(halts[0],16)
out=K/'compiled001.json';assert not out.exists()
r=dict(passed=False,physical_access=False,source_sha256=sha(Path(__file__)),image_sha256=sha(B/'image-crom.bin'),cases=[],scope='Exact linked freeze/encode/LED/timer/classification/latch/halt. Raw IN/OUT and NativeSend656 outcomes modeled; no physical NIC/timing proof.')
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 for name in ['normal','wrap','frozen','backward','show-busy','show-status','show-completion','entry-busy','entry-status','entry-completion','final-busy','entry-retained','if-final-busy','final-status','final-completion','encoder-reject','txfail','unsafe','incomplete','no-use']+['admission'+str(i) for i in range(2,7)]+['unsafe-admission','cpu-cr0','cpu-if','cpu-features','cpu-ram','cpu-stack','cpu-multiple-early','cpu-multiple-late','cpu-early-late','cpu-inconsistent']+['ctx-00','ctx-01','ctx-10','ctx-11','ctx-pre-missing','ctx-post-missing','ctx-both-missing','ctx-invalid-pre','ctx-invalid-post','ctx-post-unmutated','ctx-pre-change','ctx-post-change','ctx-other-early','ctx-late']:
  uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x02600000,0x100000);uc.mem_write(0x02600000,blob)
  uc.mem_map(0x027f0000,0x10000);esp=0x027fe000;end=0x026ff000
  sizes=[8,9,63,47,47];ptrs=[0x026f0000+i*0x400 for i in range(5)];raw=[]
  for i,(ptr,n) in enumerate(zip(ptrs,sizes)):
   values=[i*1000+j for j in range(n)];raw.append(values);uc.mem_write(ptr,struct.pack('<'+'I'*n,*values))
  if name.startswith('ctx-'):
   pre=raw[3];post=raw[4];raw[1][2]=1
   pre[0]=post[0]=1;pre[4]=pre[5]=post[4]=post[5]=514
   if name in ['ctx-00','ctx-01']:pre[4]=pre[5]=2
   if name in ['ctx-00','ctx-10']:post[4]=post[5]=2
   if name in ['ctx-pre-missing','ctx-both-missing']:pre[0]=0
   if name in ['ctx-post-missing','ctx-both-missing']:post[0]=0
   if name=='ctx-invalid-pre':pre[0]=2
   if name=='ctx-invalid-post':post[0]=2
   if name=='ctx-post-unmutated':raw[1][2]=0
   if name=='ctx-pre-change':pre[5]=2
   if name=='ctx-post-change':post[5]=2
   for ptr,values in zip(ptrs,raw):uc.mem_write(ptr,struct.pack('<'+'I'*len(values),*values))
  result=2 if name=='encoder-reject' else -1
  uc.mem_write(esp,struct.pack('<7I',end,result&0xffffffff,*ptrs));uc.reg_write(x.UC_X86_REG_ESP,esp);uc.reg_write(x.UC_X86_REG_EFLAGS,2);uc.mem_write(sym['eeprom']+0x40,b'\x02\x12\x34\x56\x78\x9a')
  d=dict(halted=False,reads=0,timer_reads=0,tick=0xfffff000 if name=='wrap' else 100,ports=[],byphase={},packet=None,sends=0)
  def word(a):return struct.unpack('<I',uc.mem_read(a,4))[0]
  def phase():return word(sym['Phase659'])
  def inp(uc,port,size,user):
   ph=phase();assert ph in [2,3,5];d['reads']+=1;d['byphase'][ph]=d['byphase'].get(ph,0)+1
   if port==0x8008:
    assert ph==3 and size==4;d['timer_reads']+=1
    if name=='backward':d['tick']-=1
    elif name!='frozen':d['tick']+=4000
    return d['tick']&0xffffffff
   assert port==0xc000 and size in [1,2]
   if size==2:
    return 0x800 if (ph==2 and name=='entry-busy') or (ph==5 and name in ['final-busy','entry-retained','if-final-busy']) or (ph==3 and name in ['show-busy','entry-retained']) else 0
   return 0x26 if (ph==3 and name=='show-status') or (ph==2 and name=='entry-status') or (ph==5 and name=='final-status') else 0 if (ph==3 and name=='show-completion') or (ph==2 and name=='entry-completion') or (ph==5 and name=='final-completion') else 0x10
  def output(uc,port,size,value,user):
   ph=phase();assert ph in [2,3,5]
   assert port in [0xc004,0xc008,0xc006,0xc000,0xc002]
   assert size==(2 if port in [0xc006,0xc000] else 1)
   if port==0xc008:assert value in [7,8] # no reset command
   if port==0xc004:assert value==0x20
   if port==0xc002:assert value==0x1a
   if d['packet'] is None:d['packet']=bytes(uc.mem_read(sym['Packet657'],772))
   else:assert d['packet']==bytes(uc.mem_read(sym['Packet657'],772))
   d['ports'].append([ph,port,size,value])
  def stopped(uc,a,size,user):d['halted']=True;uc.emu_stop()
  def network(uc,a,size,user):
   assert phase()==4 and d['sends']==0
   assert word(sym['Encode659'])==0 and word(sym['EntryError659'])==0 and word(sym['ShowError659'])==0
   sp=uc.reg_read(x.UC_X86_REG_ESP);args=struct.unpack('<5I',uc.mem_read(sp+4,20));ptr,n,mac,ip,port=args
   assert n==772 and port==cfg['port'] and list(uc.mem_read(ip,4))==list(map(int,cfg['expected_peer'].split('.')))
   assert bytes(uc.mem_read(mac,6))==b'\x02\x12\x34\x56\x78\x9a'
   assert bytes(uc.mem_read(ptr,n))==d['packet'];d['sends']+=1
   admission=1 if name in ['unsafe-admission','if-final-busy'] or name.startswith(('cpu-','ctx-')) else int(name[-1]) if name.startswith('admission') else 0
   used=int(name=='unsafe-admission' or (not admission and name!='no-use'));safe=int(used and name not in ['unsafe','unsafe-admission'])
   completed=0 if not used else 1 if name in ['txfail','unsafe'] else 2 if name=='incomplete' else 3
   error=1 if admission else 3 if name in ['txfail','unsafe'] else 0
   values=[used,error,4 if name=='unsafe' else 0,used,3 if used else 0,completed,safe,0,0,0,0,0,7,6 if name=='unsafe' else 5 if name=='txfail' else 0,0,0]
   uc.mem_write(sym['NativeResult656'],struct.pack('<16I',*values));uc.mem_write(sym['NativeAdmissionError656'],struct.pack('<I',admission))
   av=[1,0,0x027fe000,0x4000000,0x1020]
   if name in ['cpu-cr0','cpu-multiple-early','cpu-early-late']:av[0]=0x80000001
   if name in ['cpu-if','cpu-multiple-early','if-final-busy'] or name.startswith('ctx-'):av[1]=0x200
   if name=='ctx-other-early':av[0]=0
   if name=='ctx-late':av[3]=0
   if name=='cpu-features':av[4]=0x20
   if name in ['cpu-ram','cpu-multiple-late','cpu-early-late']:av[3]=0
   if name in ['cpu-stack','cpu-multiple-late']:av[2]=0x02800000
   d['admission_bytes']=struct.pack('<5I',*av)
   uc.mem_write(sym['NativeAdmission656'],d['admission_bytes'])
   # Model effects on producer memory; frozen capture must remain exact.
   uc.mem_write(ptrs[1],b'\xee'*36)
   dest=word(sp);uc.reg_write(x.UC_X86_REG_EAX,error);uc.reg_write(x.UC_X86_REG_ESP,sp+4);uc.reg_write(x.UC_X86_REG_EIP,dest)
  uc.hook_add(u.UC_HOOK_INSN,inp,None,1,0,x.UC_X86_INS_IN);uc.hook_add(u.UC_HOOK_INSN,output,None,1,0,x.UC_X86_INS_OUT)
  uc.hook_add(u.UC_HOOK_CODE,stopped,None,halt,halt)
  uc.hook_add(u.UC_HOOK_CODE,network,None,sym['NativeSend656'],sym['NativeSend656'])
  uc.emu_start(sym['XwnExport657'],end,timeout=45000000,count=20000000)
  assert d['halted'] and phase()==6 and uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200==0
  expected_show={'frozen':1,'backward':1,'show-busy':2,'entry-retained':2,'show-status':3,'show-completion':4}.get(name,0)
  expected_mask=0x11 if name.startswith('admission') else {'frozen':0xc6,'backward':0xc6,'show-busy':0xc4,'entry-retained':0xc4,'if-final-busy':0x55,'show-status':0x4c,'show-completion':0x84,'entry-busy':0xff,'entry-status':0xff,'entry-completion':0xff,'encoder-reject':0x10,'txfail':0x33,'unsafe':0xf0,'unsafe-admission':0xf0,'incomplete':0x03,'no-use':0x03,'cpu-cr0':0x50,'cpu-if':0x55,'cpu-features':0xa5,'cpu-ram':0x5f,'cpu-stack':0xf5,'cpu-multiple-early':0x05,'cpu-multiple-late':0x05,'cpu-early-late':0x50,'cpu-inconsistent':0x01}.get(name,15)
  expected_bits={'cpu-cr0':1,'cpu-if':2,'if-final-busy':2,'cpu-features':4,'cpu-ram':8,'cpu-stack':16,'cpu-multiple-early':3,'cpu-multiple-late':24,'cpu-early-late':9}.get(name,0)
  if name.startswith('ctx-'):expected_bits=3 if name=='ctx-other-early' else 10 if name=='ctx-late' else 2
  expected_stage=1 if expected_bits&7 else 2 if expected_bits&24 else 0
  assert word(sym['CpuBits665'])==expected_bits and word(sym['CpuStage665'])==expected_stage
  if 'admission_bytes' in d:assert bytes(uc.mem_read(sym['NativeAdmission656'],20))==d['admission_bytes']
  expected_sends=int(name not in ['frozen','backward','show-busy','show-status','show-completion','entry-busy','entry-status','entry-completion','entry-retained','encoder-reject']);assert d['sends']==expected_sends and word(sym['SendCalled665'])==expected_sends
  if name.startswith('ctx-'):expected_mask=0x05 if name=='ctx-other-early' else 0x55
  assert word(sym['OriginalMask665'])==expected_mask
  expected_context={'cpu-if':4,'if-final-busy':4,'ctx-00':6,'ctx-01':7,'ctx-10':8,'ctx-11':9,'ctx-pre-missing':1,'ctx-post-missing':2,'ctx-both-missing':3,'ctx-invalid-pre':4,'ctx-invalid-post':4,'ctx-post-unmutated':4,'ctx-pre-change':5,'ctx-post-change':5,'ctx-late':9}.get(name,0)
  expected_mask=[0x50,0x55,0xf5,0x5f,0xff,0xa5,0x03,0x30,0x33,0x0f][expected_context]
  assert word(sym['Context665'])==expected_context
  assert word(sym['ShowError659'])==expected_show and word(sym['Mask659'])==expected_mask
  assert word(sym['EntryError659'])==({'entry-busy':2,'entry-status':3,'entry-completion':4}.get(name,0))
  assert word(sym['FinalError659'])==({'final-busy':2,'entry-retained':2,'if-final-busy':2,'final-status':3,'final-completion':4}.get(name,0))
  if name!='encoder-reject':
   assert word(sym['Encode659'])==0
   packet=bytes(uc.mem_read(sym['Packet657'],772));assert packet==d['packet']
   parsed=decode(packet,bytes.fromhex(cfg['attempt']),bytes.fromhex(cfg['build_id']))
   for key,values in zip(['request','state','trace','pre','post'],raw):assert parsed[key]==values,key
   assert parsed['result']==-1 and parsed['post_kind']==2
  else:assert word(sym['Encode659'])==0xffffffff and d['timer_reads']==0
  for ph in [2,3,5]:
   ports=[v[1:] for v in d['ports'] if v[0]==ph]
   assert len(ports)%5==0
   for i in range(0,len(ports),5):assert [v[0] for v in ports[i:i+5]]==[0xc004,0xc008,0xc006,0xc000,0xc002]
  final_values=[v[3] for v in d['ports'] if v[0]==5 and v[1]==0xc006]
  assert final_values==([] if name in ['final-busy','entry-retained','if-final-busy'] else [expected_mask] if name in ['final-status','final-completion'] else [expected_mask,1])
  entry_values=[v[3] for v in d['ports'] if v[0]==2 and v[1]==0xc006]
  assert entry_values==([] if name=='entry-busy' else [0xe1] if name in ['entry-status','entry-completion'] else [0xe1,1])
  requested=[];reg=None
  for ph,port,size,value in d['ports']:
   if port==0xc008:reg=value
   if port==0xc006 and reg==8:requested.append(value)
  if name=='entry-retained':assert requested==[0xe1]
  if name in ['final-busy','if-final-busy']:assert requested==[0xe1,0,5]
  if name in ['normal','wrap']:
   assert d['timer_reads']==12000 and len(d['ports'])==35
  if name=='frozen':assert d['timer_reads']==200001
  if name=='backward':assert d['timer_reads']==2
  assert d['reads']<300000
  r['cases'].append(dict(name=name,halted=True,show_error=expected_show,final_mask=expected_mask,context=expected_context,entry_mask_requests=entry_values,last_mask_requested=requested[-1] if requested else None,cpu_bits=expected_bits,cpu_stage=expected_stage,entry_error=word(sym['EntryError659']),final_error=word(sym['FinalError659']),timer_reads=d['timer_reads'],raw_reads=d['reads'],out_instructions=len(d['ports']),network_calls=d['sends'],no_reset=True));save()
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print('PASS',len(r['cases']),'exact linked control cases')
