"""Finish explicit layout/relocation adaptations before host construction."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;A=K.parent/'native-linecompare-low813'
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x813(?=[0-9a-f]{0,2}$)','0x817',p).replace('0x8130000d','0x8170000d') if i%2 else p.replace('813','817') for i,p in enumerate(parts))
hexmap={'0x67c0':'0x77c0','0x6800':'0x7800','0x74d0':'0x8654','0x7d00':'0x8f00','0x7d04':'0x8f04','0x8000':'0xa000'}
for n in ['relocate003.py','relocate004.py']:
 p=K/n;p.write_text(p.read_text().replace('len(rows)==43','len(rows)==53'))
for n in ['host_build009.py','page002.c','page_tool003.c','main004.c','page_review008.py','page_boundary009.py','link_review012.py']:
 p=K/n;s=p.read_text();s=re.sub(r'\b35\b','41',s)
 if n=='main004.c':s=s.replace('words[41]','words[35]')
 p.write_bytes(s.encode())
p=K/'optical_review005.py';s=p.read_text().replace('base - 4096, 40960','base - 4096, 49152').replace("b'G' * 40960","b'G' * 49152");p.write_bytes(s.encode())
s=ns((A/'integration001.py').read_text());s=re.sub(r'0x[0-9a-fA-F]+',lambda m:hexmap.get(m[0],m[0]),s)
s=s.replace('base-4096,40960','base-4096,49152').replace("b'G'*40960","b'G'*49152").replace('32768','40960').replace('op+3280','op+3668').replace('<820I','<917I').replace('admitted_stack_bytes\':768','admitted_stack_bytes\':4352')
s=s.replace("state={'cl18writes'","state={'mc_phase':None,'mc_ret':None,'mc_step':-1,'mc_trace':[],'cl18writes'")
s=s.replace("if cr_bad:cr[cr_bad[0]]=cr_bad[1]","cr[0x1a]=0x38\n if cr_bad:cr[cr_bad[0]]=cr_bad[1]")
# Exact relocated helper PCs are from this fresh linked native ELF.
s=s.replace("sy=b['bridge_symbols'];", "ps={a[2]:int(a[0],16) for l in Path('C:/xwn817/payload008/symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}\nsy=b['bridge_symbols'];")
point="  off=addr-GPU;assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200\n"
block='''  if off==0x6013d5 and state['mc_phase']:
   assert width==1;idx=sels[0x6013d4];regs_mc=[26,37,40,45,19,25,23,24,7,9];assert idx in regs_mc
   j=regs_mc.index(idx);phase=state['mc_phase'];i=state['mc_step']
   assert state['seq']==0x21 and state['gate']==5
   if kind==u.UC_MEM_WRITE:
    assert j<4
    if phase=='forward':assert j==i+1 and word(834)==j+1;expected=[60,16,131,224][j]
    else:assert j==(word(834)-1 if i==-1 else i-1);expected=word(820+j)
    assert value==expected;state['mc_step']=j;cr[idx]=value
    state['mc_trace'].append([phase,j,'write',idx,value]);return
   value=cr[idx];state['mc_trace'].append([phase,i,'read',idx,value]);uc.mem_write(addr,bytes([value]));return
'''
assert s.count(point)==1;s=s.replace(point,point+block)
point=" c.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,None,GPU,GPU+0x7fffff)"
block=''' def control_pc(uc,pc,size,_):
  if pc==state['mc_ret']:state['mc_phase']=None;state['mc_ret']=None
  entries=[base+2304+ps[n]-0x100000 for n in ['controls_forward817','controls_restore817']]
  if pc in entries:
   state['mc_phase']='forward' if pc==entries[0] else 'undo'
   state['mc_ret']=struct.unpack('<I',uc.mem_read(uc.reg_read(x.UC_X86_REG_ESP),4))[0];state['mc_step']=-1
 c.hook_add(u.UC_HOOK_CODE,control_pc)
'''
s=s.replace(point,block+point)
s=s.replace('assert full[796:]==','assert full[796:820]==')
point=' full_cw=cw[:];cw=[(i,x) for i,x in cw if i!=24]'
block=''' if full[834]:
  assert full[834]==4 and full[820:830]==[56,16,131,224,104,48,227,255,62,64]
  assert full[830:834]==[60,16,131,224] and full[915:917]==[0,0]
  assert [q for q in state['mc_trace'] if q[2]=='write']==[[p,i,'write',[26,37,40,45][i],([60,16,131,224] if p=='forward' else [56,16,131,224])[i]] for p,order in [('forward',range(4)),('undo',range(3,-1,-1))] for i in order]
  for i in range(4):
   assert full[835+10*i:845+10*i]==[full[830+j] if j<=i else full[820+j] for j in range(10)]
   assert full[875+10*i:885+10*i]==[full[830+j] if j<i else full[820+j] for j in range(10)]
'''
s=s.replace(point,block+point)
s=s.replace('words=[0x8170000d,0 if refusal else want,v[30],v[100],v[108],full[675],full[705],full[735],full[765],full[795],full[790],full[793],full[794]]','words=[0x8170000d,0 if refusal else want]+[full[j] for j in [30,100,108,675,735,795,915,916,820,835,905]]')
(K/'integration001.py').write_bytes(s.encode())
print('Fresh relocation counts: 53 total / 41 absolute; integration and40KiB bounds adapted')
