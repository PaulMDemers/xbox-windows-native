"""Create a fresh, bounded actual-COFF CR18 test from source-only809 machinery.
This is a narrow tail test, not full launch qualification or hardware proof.
"""
from pathlib import Path
import hashlib,re,json
K=Path(__file__).resolve().parent;W=K.parents[1]
parent=W/'outputs/crtc-linecompare-bit809/model006.py'
s=parent.read_text(encoding='utf-8')
s=s[:s.index(" v=list(struct.unpack('<790I'")]
s=s.replace('Actual809 COFF with horizontal transaction, pre-enable recovery and fault injection.',
 'Actual812 COFF narrow CR18 tail validation; full prefix regression still required.')
s=s.replace('C:/xwn809/build002','C:/xwn812/build002').replace('_probe809','_probe812')
s=re.sub(r'0x809(?=[0-9a-f]{0,2}\b)','0x812',s)
s=s.replace("out=K/'model006.json'","out=K/'model001.json'")
s=s.replace("state={'cl9writes':0", "state={'cl18writes':0,'cl18reads':[],'cl9writes':0")
s=s.replace('0x201c58','0x201cd0')
# Prior prefix hook phase recognizers must also recognize the new terminal stage.
s=re.sub(r'(\[[^\]\n]*,0x812)\]',r'\1,0x81248]',s)
s=s.replace('assert idx in [0x15,9,','assert idx in [0x18,0x15,9,')
hook='''    if idx==0x18:
     assert state['cl9writes']==1 and word(1) in [0x81248,0x812]
     state['cl18writes']+=1;n=state['cl18writes'];assert n<=2
     assert [word(790),word(791),word(792)]==[255,255,1] and value==255
     assert state['sq']==0x21 and ports==[5]
     writes.append(['cr',24,value])
     if fault==('cl18-drop-write' if n==1 else 'cl18-drop-undo') or (n==2 and fault=='cl18-wrong-write-drop-undo'):return
     cr[24]=value
     if fault==('cl18-wrong-write' if n==1 else 'cl18-wrong-undo') or (n==1 and fault=='cl18-wrong-write-drop-undo'):cr[24]^=1
     if n==1 and fault.startswith('cl18-coupling-'):
      j=int(fault.rsplit('-',1)[1]);assert 1<=j<=8;cr[[6,7,9,16,18,21,22,37][j-1]]^=1
     return
'''
needle="    if idx==9 and state['cl7writes']==1"
assert s.count(needle)==1;s=s.replace(needle,hook+needle)
readhook='''   if idx in [24,6,7,9,16,18,21,22,37] and state['cl9writes']==1 and word(1) in [0x81248,0x812]:
    j=[24,6,7,9,16,18,21,22,37].index(idx);phase=['before','after','undo'][state['cl18writes']]
    if fault=='cl18-'+phase+'-'+str(j):val^=1
    state['cl18reads'].append([phase,j,val])
'''
s=s.replace('   val=cr[idx]\n','   val=cr[idx]\n'+readhook)
s=s.replace('  if val==4:\n','  if val==4:\n   assert word(795)==0 and (not word(792) or word(794)==word(790))\n')
tail=''' v=list(struct.unpack('<820I',c.mem_read(0x201000,3280)))
 assert v[8]==v[10] and not v[9]&0x200 and v[8]&0x200==flags&0x200
 assert v[11:14]==[cpu0,cpu3,cpu4] and c.reg_read(x.UC_X86_REG_EFLAGS)&0x200==flags&0x200
 assert bytes(c.mem_read(0x200000,4096))==b'G'*4096
 assert bytes(c.mem_read(0x201cd0,0x5330))==b'G'*0x5330
 assert bytes(c.mem_read(0x208008,0xff8))==b'G'*0xff8 and sels==original
 cpu_bad=(cpu0&0x80000001)!=0x80000001 or cpu4&0x20
 if cpu_bad or baseline:
  assert v[0:2]==[0x8121 if cpu_bad else 0x8122]*2
  assert not writes and not ports and not v[792] and not state['cl18writes']
 else:
  before_fault=fault.startswith('cl18-before-')
  after_fault=fault.startswith('cl18-after-') or fault in ['cl18-wrong-write','cl18-wrong-write-drop-undo'] or fault.startswith('cl18-coupling-')
  cleanup_fault=fault.startswith(('cl18-undo-','cl18-coupling-')) or fault in ['cl18-wrong-undo','cl18-wrong-write-drop-undo']
  expected_mask=(1<<int(fault.rsplit('-',1)[1])) if fault.startswith(('cl18-undo-','cl18-coupling-')) else int(cleanup_fault)
  assert v[1]==(0x81248 if before_fault or after_fault else 0x812),(name,hex(v[1]))
  assert v[0]==(0x81249 if cleanup_fault else v[1]),(name,hex(v[0]))
  assert v[792]==int(not before_fault) and state['cl18writes']==2*v[792]
  assert v[795]==expected_mask,(name,v[795],expected_mask)
  assert (4 in ports)==(not cleanup_fault),(name,ports)
  assert ports==([5] if cleanup_fault else [5,4])
  expected=[255,12,62,64,233,223,223,140,16]
  indices=[790]+[796+3*j for j in range(8)]
  for j,n in enumerate(indices):
   assert v[n]==(expected[j]^int(fault=='cl18-before-'+str(j)))
  if before_fault:
   assert v[791]==0 and v[793:795]==[0xffffffff]*2
   assert all(v[n+1:n+3]==[0xffffffff]*2 for n in indices[1:])
  else:
   assert v[791]==255
   for j,n in enumerate([793]+[797+3*j for j in range(8)]):
    bad=fault=='cl18-after-'+str(j) or (j==0 and fault in ['cl18-wrong-write','cl18-wrong-write-drop-undo']) or fault=='cl18-coupling-'+str(j)
    assert v[n]==(expected[j]^int(bad)),(name,'after',j,v[n])
   for j,n in enumerate([794]+[798+3*j for j in range(8)]):
    bad=bool(expected_mask&(1<<j))
    assert v[n]==(expected[j]^int(bad)),(name,'undo',j,v[n])
  # These same-value writes cannot demonstrate effectiveness when dropped.
  if fault in ['cl18-drop-write','cl18-drop-undo']:assert v[0]==0x812
 R['cases'].append({'name':name,'code':hex(v[0]),'forward':hex(v[1]),'attempted':v[792],
  'cr18':[v[790],v[793],v[794]],'mask':v[795],'ports':ports,'tail_reads':state['cl18reads']})
try:
 for flags in [0x246,0x46]:run('clean-'+hex(flags),flags=flags)
 run('cpu-unpaged',cpu0=0x10031)
 run('cpu-pae',cpu4=0x630)
 for base in ['cr22','cr33','seq','cr11','mm','cr','cr1b']:run('baseline-'+base,baseline=base)
 for phase in ['before','after','undo']:
  for j in range(9):run('cl18-'+phase+'-'+str(j),fault='cl18-'+phase+'-'+str(j))
 for fault in ['cl18-drop-write','cl18-drop-undo','cl18-wrong-write','cl18-wrong-undo','cl18-wrong-write-drop-undo']:
  run(fault,fault=fault)
 for j in range(1,9):run('cl18-coupling-'+str(j),fault='cl18-coupling-'+str(j))
 R['passed']=True;R['case_count']=len(R['cases'])
except BaseException as e:R['failure']=repr(e);raise
finally:
 R['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 R['launch_qualified']=False
 out.write_text(json.dumps(R,separators=(',',':'))+'\\n')
print('PASS narrow812 actual COFF',len(R['cases']),'cases; full qualification outstanding')
'''
s+=tail
out=K/'model001.py';assert not out.exists();out.write_text(s,encoding='utf-8')
(K/'model-lineage001.json').write_text(json.dumps({'source_only_parent':str(parent.relative_to(W)),
 'parent_sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),
 'harness_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
 'scope':'Narrow CR18 compiled tail checks; inherited hardware model, new oracle; prefix regression and frontend qualification outstanding'},indent=2)+'\n')
