"""Exact654 wrapper/capture/single-comparison LED instructions; setup and hardware callbacks modeled."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'))
sys.path.insert(0,str(W/'outputs/timing-review650'))
import unicorn as u
from unicorn import x86_const as x
from decode import load_profiles
p=load_profiles()[3]
B=Path('C:/xwn654/build001');record=json.loads((K/'build001.json').read_text())
blob=(B/'image-crom.bin').read_bytes();digest=hashlib.sha256(blob).hexdigest()
assert digest==record['outputs']['image-crom.bin']['sha256']
nm=subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-n','/mnt/c/xwn654/build001/image-crom.elf'],text=True,timeout=25)
symbols={a[2]:int(a[0],16) for line in nm.splitlines() if len(a:=line.split())==3}
required=['XwnHdTry720','XwnHdState311','XwnDiag651Status','XwnReadback651Pre','XwnReadback651Post','XwnTrace649','xbox_ram','xwn_hd_apply','xwn_hd_smb_write','hd_delay','hd_r32','hd_r8','hd_w8']
assert all(n in symbols for n in required)
out=K/'compiled-wrapper001.json';assert not out.exists()
report=dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),passed=False,physical_access=False,image_sha256=digest,results=[],scope='Exact wrapper/capture/LED code; apply result and hardware callbacks are modeled. No physical readback or timing proof.')
def save():out.write_text(json.dumps(report,indent=2)+'\n')
save()
# error22: each phase; each mismatch class; status patterns; handshake outcomes;
# IF enabled skips indexed access, plus unsupported gate and setup outcomes.
cases=[dict(result=-1,stage=255,error=22,phase=p,match=0,status='constant',handshake=0,iflag=0,gate=0) for p in range(1,7)]
for match,status,hs,iflag in [(1,'constant',0,0),(2,'constant',1,0),(3,'varied',0x10,0),(0,'ff',0x11,0),(0,'invalid',0xffffffff,0),(0,'constant',0,1)]:
 cases.append(dict(result=-1,stage=255,error=22,phase=3,match=match,status=status,handshake=hs,iflag=iflag,gate=0))
for result,stage,error in [(1,5,0),(0,0,0),(-1,255,21),(-1,255,11),(-1,255,23)]:
 cases.append(dict(result=result,stage=stage,error=error,phase=0,match=0,status='invalid',handshake=0,iflag=0,gate=int(result==0)))
for match in (1,2,3):
 cases.append(dict(result=1,stage=5,error=0,phase=0,match=match,status='invalid',handshake=0,iflag=0,gate=0))
try:
 for case in cases:
  detailed=case['error']==22
  for fail in range(5):
   uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x02600000,0x100000);uc.mem_write(0x02600000,blob)
   uc.mem_map(0x027f0000,0x10000);esp=0x027fe000;end=0x026ff000;mode=0x026f0000
   cable=1 if case['gate'] else 3
   uc.mem_write(esp,struct.pack('<5I',end,mode,0,cable,8));uc.mem_write(symbols['xbox_ram'],struct.pack('<I',64))
   uc.reg_write(x.UC_X86_REG_ESP,esp);uc.reg_write(x.UC_X86_REG_EFLAGS,2|(0x200 if case['iflag'] else 0))
   for reg in (x.UC_X86_REG_EBX,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI,x.UC_X86_REG_EBP):uc.reg_write(reg,0x12345678)
   d=dict(setup=0,index=0x56,reads=[0,0],writes=[0,0],events=[],delays=0,halt=False)
   def words(a,n):return struct.unpack('<'+'I'*n,uc.mem_read(a,4*n))
   def ret(value):
    sp=uc.reg_read(x.UC_X86_REG_ESP);dest=words(sp,1)[0]
    uc.reg_write(x.UC_X86_REG_EAX,value&0xffffffff);uc.reg_write(x.UC_X86_REG_ESP,sp+4);uc.reg_write(x.UC_X86_REG_EIP,dest)
   def hook(uc,a,size,unused):
    sp=uc.reg_read(x.UC_X86_REG_ESP)
    if a==symbols['xwn_hd_apply']:
     assert d['setup']==0 and d['index']==0x56
     d['setup']=1;d['index']=0x28
     io,request,state=words(sp+4,3);assert words(request,8)==(3,67108864,57671680,9437184,316160,0,cable,8)
     mutated=int(case['result']!=0)
     uc.mem_write(state,struct.pack('<9I',case['stage'],case['error'],mutated,19,19,1,2,0,0))
     phase=case['phase'];trace=[phase,max(phase-1,0),phase]+[0]*60
     if phase:
      wanted=((phase-1)%2)*8;byte=255 if case['status']=='ff' else (wanted^8)|0xa0
      row=[wanted,byte,byte,0 if case['status']=='invalid' else 100000,12 if case['status']=='varied' else 0,0,0,0,4200000,4200000]
      trace[3+(phase-1)*10:13+(phase-1)*10]=row
     uc.mem_write(symbols['XwnTrace649'],struct.pack('<63I',*trace));ret(case['result'])
    elif a==symbols['hd_r32']:
     context,offset=words(sp+4,2);assert context==0
     d['reads'][d['setup']]+=1
     assert offset in list(p['MM'])+[0x680508,0x600804,0x6806a0]
     value=p['MM'].get(offset,0x12345678)
     if offset==0x6806a0:value=case['handshake'] if d['setup'] else 0
     if d['setup'] and case['match']&2 and offset==0x680800:value^=1
     ret(value)
    elif a==symbols['hd_r8']:
     context,offset=words(sp+4,2);assert context==0
     d['reads'][d['setup']]+=1
     assert offset in (0x6013d4,0x6013d5)
     value=d['index'] if offset==0x6013d4 else p['CR'][d['index']]
     if offset==0x6013d5 and d['setup'] and case['match']&1 and d['index']==0:value^=1
     ret(value)
    elif a==symbols['hd_w8']:
     context,offset,value=words(sp+4,3);assert context==0 and offset==0x6013d4
     d['writes'][d['setup']]+=1;d['index']=value;ret(0)
    elif a==symbols['xwn_hd_smb_write']:
     io,addr,reg,value=words(sp+4,4)
     assert d['setup'] and d['index']==0x28
     d['events'].append((addr,reg,value));ret(int(reg!=2 and len(d['events'])==fail))
    elif a==symbols['hd_delay']:
     context,us=words(sp+4,2);assert us==1000000
     d['delays']+=1;assert d['delays']<=22;ret(0)
    elif bytes(uc.mem_read(a,1))==b'\xf4':d['halt']=True;uc.emu_stop()
   uc.hook_add(u.UC_HOOK_CODE,hook)
   uc.emu_start(symbols['XwnHdTry720'],end,count=200000)
   known=(case['result']==1 and case['stage']==5 and case['error']==0) or (case['result']==-1 and case['stage']==255 and case['error']==22)
   comparison=4 if case['iflag'] or case['gate'] or not known else case['match']
   mask=[5,80,85,245,165][comparison]
   writes=[(16,8,0),(16,7,1),(16,8,mask),(16,7,0)]
   expected=writes[:fail or len(writes)]
   if case['result']<=0:expected += [(16,2,1)]
   assert d['events']==expected,(case,fail,d['events'],expected)
   assert d['delays']==[22,0,0,2,22][fail]
   assert words(symbols['XwnDiag651Status'],1)[0]==fail
   assert d['halt']==(case['result']<=0)
   if not case['gate']:
    count=18 if case['iflag'] else 43;wc=0 if case['iflag'] else 24
    assert d['reads']==[count,count] and d['writes']==[wc,wc]
    for name,index in [('XwnReadback651Pre',0x56),('XwnReadback651Post',0x28)]:
     v=words(symbols[name],47);assert v[0]==1 and v[1]==(not case['iflag'])
     assert (v[4]&0x200)==(v[5]&0x200)==(0x200 if case['iflag'] else 0)
     if not case['iflag']:assert v[2:4]==(index,index)
   else:assert d['reads']==[0,0] and d['writes']==[0,0]
   if case['result']>0:
    assert uc.reg_read(x.UC_X86_REG_EIP)==end and uc.reg_read(x.UC_X86_REG_ESP)==esp+4
    assert words(mode+16,4)==(720,480,0,0)
    assert all(uc.reg_read(reg)==0x12345678 for reg in (x.UC_X86_REG_EBX,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI,x.UC_X86_REG_EBP))
   report['results'].append(dict(**case,failed_write=fail,reads=d['reads'],selector_writes=d['writes'],delay_calls=d['delays'],reset_path=d['halt']))
  save()
 report.update(passed=True,cases=len(report['results']))
except BaseException as e:report['failure']=repr(e);raise
finally:save()
print('PASS',len(report['results']),'exact wrapper/capture/LED cases')
