"""Adapt qualified812 compiled-code harness; new four-control oracle is separate."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-linecompare-low812'
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x812(?=[0-9a-f]{0,2}$)','0x814',p) if i%2 else p.replace('812','814') for i,p in enumerate(parts))
s=ns((O/'model005.py').read_text())
s=s.replace("out=K/'model005.json'","out=K/'prefix002.json'").replace('0x201cd0','0x201e54').replace('0x5330','0x51ac')
s=s.replace('count=40000','count=60000').replace('deadline=time.monotonic()+180','deadline=time.monotonic()+240')
s=s.replace('sq=1;gr=0','cr.update({0x1a:0,0x28:0x83,0x2d:0})\n sq=1;gr=0')
s=s.replace(" state={'cl18writes'", " state={'mc_phase':None,'mc_ret':None,'mc_step':-1,'mc_trace':[],'cl18writes'")
s=s.replace('  steps[0]+=1','''  if pc==state['mc_ret']:state['mc_phase']=None;state['mc_ret']=None
  if pc in [symbols['_controls_forward814'],symbols['_controls_restore814']]:
   state['mc_phase']='forward' if pc==symbols['_controls_forward814'] else 'undo'
   state['mc_ret']=struct.unpack('<I',uc.mem_read(uc.reg_read(x.UC_X86_REG_ESP),4))[0]
   state['mc_step']=-1
  steps[0]+=1''')
hook='''   if state['mc_phase']:
    regs_mc=[26,37,40,45,19,25,23,24,7,9];assert idx in regs_mc
    j=regs_mc.index(idx);phase=state['mc_phase'];i=state['mc_step']
    assert state['sq']==0x21 and ports==[5]
    if kind==u.UC_MEM_WRITE:
     assert j<4
     if phase=='forward':
      assert j==i+1 and word(834)==j+1;value_expected=[4,16,131,0][j]
     else:
      assert j==(word(834)-1 if i==-1 else i-1);value_expected=word(820+j)
     assert value==value_expected;state['mc_step']=j;i=j
     state['mc_trace'].append([phase,i,'write',idx,value])
     if fault==f'mc-{phase}-drop-{i}':return
     cr[idx]=value
     if fault==f'mc-{phase}-wrong-{i}':cr[idx]^=1
     if phase=='forward' and fault.startswith(f'mc-couple-{i}-'):cr[regs_mc[int(fault.rsplit('-',1)[1])]]^=1
     return
    val=cr[idx]
    label='before' if phase=='forward' and i==-1 else phase
    if fault==f'mc-{label}-read-{i}-{j}':val^=1
    state['mc_trace'].append([label,i,'read',idx,val]);uc.mem_write(addr,bytes([val]));return
'''
a='   assert width==1;idx=sels[0x6013d4];assert idx in cr\n';assert s.count(a)==1;s=s.replace(a,a+hook)
# Earlier recovery assertions accept the new failure stages. No fault is masked.
s=re.sub(r'(word\(1\) in \[[^\]\n]+)\]',lambda m:m.group(1)+',0x81450,0x81451,0x81452,0x81453]',s)
s=s.replace('  if val==4:\n','  if val==4:\n   assert word(915)==0\n')
boundary=''' mc=list(struct.unpack('<97I',c.mem_read(0x201000+820*4,388)))
 if mc[14]:
  assert mc[:15]==[0,16,131,0,104,48,227,255,62,64,4,16,131,0,4],(name,mc[:15])
  for i in range(4):
   assert mc[15+10*i:25+10*i]==[mc[10+j] if j<=i else mc[j] for j in range(10)]
   assert mc[55+10*i:65+10*i]==[mc[10+j] if j<i else mc[j] for j in range(10)]
  assert mc[95:]==[0,0]
  assert [t[:4] for t in state['mc_trace'] if t[2]=='write']==[['forward',i,'write',r] for i,r in enumerate([26,37,40,45])]+[['undo',i,'write',[26,37,40,45][i]] for i in [3,2,1,0]]
 else:assert mc==[0]*15+[0xffffffff]*80+[0,0],(name,mc)
'''
anchor=" extra=list(struct.unpack('<30I'";assert s.count(anchor)==1;s=s.replace(anchor,boundary+anchor)
s=s.replace("'raw_result':v+extra,","'raw_result':v+extra+mc,")
(K/'prefix002.py').write_text(s)
# Narrow new-control fault tests use the same actual COFF access contract.
head=s[:s.index(boundary)].replace("out=K/'prefix002.json'","out=K/'tail002.json'")
tail=''' v=list(struct.unpack('<917I',c.mem_read(0x201000,3668)))
 assert bytes(c.mem_read(0x200000,4096))==b'G'*4096
 assert bytes(c.mem_read(0x201e54,0x51ac))==b'G'*0x51ac
 assert bytes(c.mem_read(0x208008,0xff8))==b'G'*0xff8 and sels==original
 assert v[8]==v[10] and v[11:14]==[cpu0,cpu3,cpu4]
 mc=v[820:];trace=state['mc_trace'];regs_mc=[26,37,40,45,19,25,23,24,7,9]
 if cpu0!=0x80010031 or cpu4&0x20:
  assert mc==[0]*15+[0xffffffff]*80+[0,0] and not trace
 else:
  # Independently replay the observed accesses against the protocol, deriving
  # forward and recovery masks from observed values rather than status colors.
  obs=[t[4] for t in trace[:10]];assert [t[2] for t in trace[:10]]==['read']*10
  assert mc[:10]==obs
  fm=sum(1<<j for j,(a,b) in enumerate(zip(obs,[0,16,131,0,104,48,227,255,62,64])) if a!=b)
  pos=10;attempts=0;stage=0x81450
  while not fm and attempts<4:
   i=attempts;stage=0x81450+i
   assert trace[pos]==['forward',i,'write',regs_mc[i],[4,16,131,0][i]];pos+=1;attempts+=1
   readings=trace[pos:pos+10];pos+=10
   assert [t[:4] for t in readings]==[['forward',i,'read',r] for r in regs_mc]
   vals=[t[4] for t in readings];assert mc[15+10*i:25+10*i]==vals
   expected=[([4,16,131,0][j] if j<=i else obs[j]) for j in range(10)]
   fm=sum(1<<j for j,(a,b) in enumerate(zip(vals,expected)) if a!=b)
  assert mc[14]==attempts and mc[96]==fm
  assert v[1]==(stage if fm else 0x814)
  um=0
  for i in reversed(range(attempts)):
   assert trace[pos]==['undo',i,'write',regs_mc[i],obs[i]];pos+=1
   readings=trace[pos:pos+10];pos+=10
   assert [t[:4] for t in readings]==[['undo',i,'read',r] for r in regs_mc]
   vals=[t[4] for t in readings];assert mc[55+10*i:65+10*i]==vals
   expected=[([4,16,131,0][j] if j<i else obs[j]) for j in range(10)]
   um|=sum(1<<j for j,(a,b) in enumerate(zip(vals,expected)) if a!=b)
  assert pos==len(trace) and mc[95]==um
  assert mc[15+10*attempts:55]==[0xffffffff]*(40-10*attempts)
  assert mc[55+10*attempts:95]==[0xffffffff]*(40-10*attempts)
  assert (4 in ports)==(um==0 and all(v[n]==0 for n in [100,108,121,129,138,148,158,169,181,193,205,221,237,261,285,315,345,375,405,435,465,495,525,555,585,615,645,675,705,735,765,795]))
  if um:assert v[0]==0x81454
  if not fault:assert v[:2]==[0x814,0x814] and not um and attempts==4
 R['cases'].append(dict(name=name,raw_result=v,ports=ports,control_trace=trace))
try:
 for flags in [0x246,0x46]:run('clean-'+hex(flags),flags=flags)
 run('cpu-unpaged',cpu0=0x10031);run('cpu-pae',cpu4=0x630)
 for j in range(10):run(f'mc-before-read--1-{j}',fault=f'mc-before-read--1-{j}')
 for phase in ['forward','undo']:
  for i in range(4):
   for j in range(10):run(f'mc-{phase}-read-{i}-{j}',fault=f'mc-{phase}-read-{i}-{j}')
   for f in ['drop','wrong']:run(f'mc-{phase}-{f}-{i}',fault=f'mc-{phase}-{f}-{i}')
 for i in range(4):
  for j in range(10):
   if j!=i:run(f'mc-couple-{i}-{j}',fault=f'mc-couple-{i}-{j}')
 R['passed']=True;R['case_count']=len(R['cases'])
except BaseException as e:R['failure']=repr(e);raise
finally:
 R['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(R,separators=(',',':'))+'\\n')
print('PASS814 compiled four-control fault cases:',len(R['cases']))
'''
(K/'tail002.py').write_text(head+tail)
(K/'model-lineage002.json').write_text(json.dumps({'parent':'CLOSED812 source-only','sha256':hashlib.sha256((O/'model005.py').read_bytes()).hexdigest(),'physical_access':False},indent=2)+'\n')
print('814 models generated, not yet run')
