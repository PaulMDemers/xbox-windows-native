"""Extend fresh728-derived COFF model with independent729 sample vectors."""
from pathlib import Path
K=Path(__file__).resolve().parent
f=K/'model.py';t=f.read_text()
t=t.replace("seq=1):", "seq=1,unlock_value=3,delay_at=4):",1)
t=t.replace("'write_reads':0", "'write_reads':0,'blank_reads':0,'gate_reads':0")
t=t.replace("state['seq']=value", "state['seq']=value\n    if value==1:\n     assert state['gate']==4 and state['gate_reads']==1\n     if behavior=='on-seq' and state['cr_attempt']:cr[0x1b]=0x85")
t=t.replace("cr[i]=value\n    else:", "cr[i]=unlock_value\n    else:",1)
t=t.replace("('sticky','on-output','late')", "('sticky','on-output','on-seq','blank-delay','late')")
t=t.replace("   if i==0x1b:\n", """   if i==0x1b:
    if state['gate']==5 and state['nmm']==2:
     if behavior=='blank-delay' and state['blank_reads']==delay_at:cr[i]=value=0x85
     state['blank_reads']+=1
    if state['gate']==4 and state['seq']==0x21:state['gate_reads']+=1
""")
t=t.replace("    if state['gate']==4:\n", "    if state['gate']==4 and state['seq']==1:\n")
t=t.replace("assert width==1 and value==[5,4][len(outs)];outs.append(value)", "assert width==1 and value==[5,4][len(outs)]\n   if value==4 and state['nmm']==2:assert state['blank_reads']==33\n   outs.append(value)")
t=t.replace('0x2010d8','0x2011f4').replace("0x5f28","0x5e0c").replace("'<54I',c.mem_read(0x201000,216)","'<125I',c.mem_read(0x201000,500)")
t=t.replace("if behavior=='on-output':pairs[3]=(3,5)", "if behavior in ('on-output','on-seq','blank-delay'):pairs[3]=(3,5)")
at=" if ncr:\n  reads="
extra=''' if nmm==2:
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
'''
assert at in t;t=t.replace(at,extra+at)
t=t.replace(" for f in (0x202,0x246,2):", " run('unlock57',unlock_value=0x57)\n run('on-seq',behavior='on-seq')\n for delay in (1,4,32):run('blank-delay-'+str(delay),behavior='blank-delay',delay_at=delay)\n for f in (0x202,0x246,2):")
f.write_text(t,newline='\n')
