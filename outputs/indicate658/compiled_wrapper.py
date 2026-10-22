"""Execute exact linked i386 capture/bridge/encoder/reset instructions under Unicorn.
Display apply and NIC sender callbacks are models, not physical hardware proof.
"""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('C:/xwn658/build001')
sys.path[:0]=[str(W/'work/python-packages'),str(W/'outputs/timing-review650'),str(W/'outputs/udp655')]
import unicorn as u
from unicorn import x86_const as x
from decode import load_profiles
from receiver import decode
p=load_profiles()[3];cfg=json.loads(Path('C:/xwn658/config.json').read_text())
build=json.loads((K/'build001.json').read_text());assert build['status']=='compiled-unqualified'
blob=(B/'image-crom.bin').read_bytes();digest=hashlib.sha256(blob).hexdigest();assert digest==build['artifacts']['image-crom.bin']['sha256']
nm=subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-n','/mnt/c/xwn658/build001/image-crom.elf'],text=True,timeout=25)
symbols={a[2]:int(a[0],16) for line in nm.splitlines() if len(a:=line.split())==3}
out=K/'compiled-wrapper001.json';assert not out.exists()
report=dict(passed=False,physical_access=False,image_sha256=digest,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),cases=[],scope='Actual linked capture/bridge/encoder/classifier/reset; modeled display apply, MMIO, NIC callback and LED show function. LED core is separately sanitizer-tested; no physical timing/NIC proof.')
def save():out.write_text(json.dumps(report,indent=2)+'\n')
save()
base=[]
for result,stage,error in [(1,5,0),(0,0,0)]+[(-1,255,e) for e in [11,12,13,21,22,23,24]]:
 for iflag in [0,1]:base.append(dict(result=result,stage=stage,error=error,iflag=iflag))
cases=[dict(**c,send=send,reset='ok') for c in base for send in ['ok','txfail','unsafe','admission']]
cases += [dict(result=-1,stage=255,error=22,iflag=0,send='ok',reset=reset) for reset in ['busy','completion','status-error','frozen','backward','wrap']]
cases += [dict(result=-1,stage=255,error=22,iflag=0,send='ok',reset='ok',signal_failure=i) for i in range(1,6)]
try:
 for case in cases:
  uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x02600000,0x100000);uc.mem_write(0x02600000,blob)
  uc.mem_map(0x027f0000,0x10000);esp=0x027fe000;end=0x026ff000;mode=0x026f0000
  cable=1 if case['result']==0 else 3
  uc.mem_write(esp,struct.pack('<5I',end,mode,0,cable,8));uc.mem_write(symbols['xbox_ram'],struct.pack('<I',64))
  uc.reg_write(x.UC_X86_REG_ESP,esp);uc.reg_write(x.UC_X86_REG_EFLAGS,2|(0x200 if case['iflag'] else 0))
  # Eeprom is an opaque fixture. Only six MAC bytes may be forwarded to sender.
  uc.mem_write(symbols['eeprom']+0x40,b'\x02\x12\x34\x56\x78\x9a')
  d=dict(signals=[],setup=0,index=0x56,reads=[0,0],writes=[0,0],ports=[],halt=False,sends=0,ticks=0,tick=0xfffffff0 if case['reset']=='wrap' else 100,busy=0,completion=0)
  def words(a,n):return struct.unpack('<'+'I'*n,uc.mem_read(a,4*n))
  def ret(value):
   sp=uc.reg_read(x.UC_X86_REG_ESP);dest=words(sp,1)[0];uc.reg_write(x.UC_X86_REG_EAX,value&0xffffffff);uc.reg_write(x.UC_X86_REG_ESP,sp+4);uc.reg_write(x.UC_X86_REG_EIP,dest)
  def hook(uc,a,size,unused):
   sp=uc.reg_read(x.UC_X86_REG_ESP)
   if a==symbols['xwn_hd_apply']:
    assert not d['setup'];d['setup']=1;d['index']=0x28
    io,request,state=words(sp+4,3);d['request']=list(words(request,8));d['state_address']=state
    statewords=[case['stage'],case['error'],int(case['result']!=0),19,18,123,456,0x11112222,0x33334444]
    uc.mem_write(state,struct.pack('<9I',*statewords));d['state']=statewords
    # Deliberately raw/unusual values: exporter must preserve, not classify.
    d['trace']=[6,4,5]+[0x10000000+i for i in range(60)]
    uc.mem_write(symbols['XwnTrace649'],struct.pack('<63I',*d['trace']));ret(case['result'])
   elif a==symbols['hd_r32']:
    context,offset=words(sp+4,2);assert context==0;d['reads'][d['setup']]+=1
    assert offset in list(p['MM'])+[0x680508,0x600804,0x6806a0];ret(p['MM'].get(offset,0x12345678))
   elif a==symbols['hd_r8']:
    context,offset=words(sp+4,2);assert context==0;d['reads'][d['setup']]+=1
    assert offset in [0x6013d4,0x6013d5];ret(d['index'] if offset==0x6013d4 else p['CR'][d['index']])
   elif a==symbols['hd_w8']:
    context,offset,value=words(sp+4,3);assert context==0 and offset==0x6013d4;d['writes'][d['setup']]+=1;d['index']=value;ret(0)
   elif a==symbols['show658']:
    io,code,ms,status=words(sp+4,4)
    assert code<=7 and ms==(4000 if not d['signals'] else 10000)
    assert d['setup'] and not d['ports']
    if not d['signals']:
     assert not d['sends'];d['entry_packet']=bytes(uc.mem_read(symbols['Packet657'],772))
     initial=decode(d['entry_packet'],bytes.fromhex(cfg['attempt']),bytes.fromhex(cfg['build_id']))
     assert initial['result']==case['result'] and initial['state']==d['state']
    else:assert d['sends']==1
    d['signals'].append((code,ms));ret(3 if len(d['signals'])==case.get('signal_failure') else 0)
   elif a==symbols['NativeSend656']:
    assert d['setup'] and not d['ports'] and not d['sends'] and d['signals']==[(1,4000)];d['sends']=1
    ptr,n,mac,ip,port=words(sp+4,5);assert n==772 and port==cfg['port']
    assert bytes(uc.mem_read(mac,6))==b'\x02\x12\x34\x56\x78\x9a'
    assert list(uc.mem_read(ip,4))==list(map(int,cfg['expected_peer'].split('.')))
    d['packet']=bytes(uc.mem_read(ptr,n));assert d['packet']==d['entry_packet'];v=decode(d['packet'],bytes.fromhex(cfg['attempt']),bytes.fromhex(cfg['build_id']))
    assert v['result']==case['result'] and v['post_kind']==(2 if case['result']<0 else 1)
    for key in ['request','state','trace']:assert v[key]==d[key],key
    for key,sym in [('pre','XwnReadback651Pre'),('post','XwnReadback651Post')]:assert v[key]==list(words(symbols[sym],47))
    assert v['error']==case['error'] # no substitution of fallback error30
    if case['result']==0:assert not any(v['pre']) and not any(v['post'])
    else:
     assert v['pre'][0]==v['post'][0]==1 and v['pre'][1]==v['post'][1]==(not case['iflag'])
     assert d['index']==0x28
    # Simulate network side effects changing producer RAM; frozen record survives.
    uc.mem_write(d['state_address'],b'\xee'*36)
    uc.mem_write(symbols['NativeResult656'],struct.pack('<14I',int(case['send']!='admission'),0,4 if case['send']=='unsafe' else 0,1,3,3,int(case['send'] in ['ok','txfail']),0,0,0,0,0,0,5 if case['send']=='txfail' else 6 if case['send']=='unsafe' else 0))
    uc.mem_write(symbols['NativeAdmissionError656'],struct.pack('<I',3 if case['send']=='admission' else 0))
    ret(0 if case['send']=='ok' else 3)
   elif a in [symbols.get('hd_delay'),symbols.get('xwn_hd_smb_write')]:raise AssertionError('legacy reset/delay path executed')
   elif bytes(uc.mem_read(a,1))==b'\xf4':d['halt']=True;uc.emu_stop()
  def inp(uc,port,size,user):
   assert d['sends'] and case['send']!='unsafe'
   if port==0x8008:
    assert size==4;d['ticks']+=1
    if case['reset']=='backward':d['tick']-=1
    elif case['reset']!='frozen':d['tick']+=40
    return d['tick']&0xffffffff
   assert port==0xc000
   if size==2:
    d['busy']+=1
    if case['reset']=='busy' or (case['reset'] in ['frozen','backward','wrap'] and d['busy']==1):return 0x800
    return 0
   assert size==1;d['completion']+=1
   return 0 if case['reset']=='completion' else 0x26 if case['reset']=='status-error' else 0x10
  def output(uc,port,size,value,user):
   assert d['sends'] and case['send']!='unsafe';d['ports'].append([port,size,value])
  uc.hook_add(u.UC_HOOK_CODE,hook);uc.hook_add(u.UC_HOOK_INSN,inp,None,1,0,x.UC_X86_INS_IN);uc.hook_add(u.UC_HOOK_INSN,output,None,1,0,x.UC_X86_INS_OUT)
  uc.emu_start(symbols['XwnHdTry720'],end,count=6000000)
  assert d['halt'] and d['sends']==1 and words(symbols['ExportPhase657'],1)==(5,)
  assert bytes(uc.mem_read(symbols['Packet657'],772))==d['packet']
  expected=[] if case['send']=='unsafe' or case['reset'] in ['busy','frozen','backward'] else [[0xc004,1,0x20],[0xc008,1,2],[0xc006,2,1],[0xc000,2,0],[0xc002,1,0x1a]]
  assert d['ports']==expected,(case,d['ports'])
  re={'busy':2,'completion':4,'status-error':3,'frozen':1,'backward':1}.get(case['reset'],0)
  assert words(symbols['ResetError657'],1)[0]==re
  assert d['ticks']<=200001 and d['completion']<=1000
  slots={'ok':[0,0,0,0],'admission':[2,0,3,0],'txfail':[3,0,3,5],'unsafe':[5,0,4,6]}[case['send']]
  assert list(words(symbols['Slots658'],4))==slots
  assert d['signals']==[(1,4000)]+[(n,10000) for n in slots]
  assert words(symbols['SignalError658'],1)[0]==(3 if case.get('signal_failure') else 0)
  report['cases'].append(dict(**case,signals=d['signals'],timer_reads=d['ticks'],reset_error=re,reset_writes=len(d['ports']),halted=True))
  save()
 report['passed']=True
except BaseException as e:report['failure']=repr(e);raise
finally:save()
print('PASS',len(report['cases']),'compiled capture/export/reset cases')
