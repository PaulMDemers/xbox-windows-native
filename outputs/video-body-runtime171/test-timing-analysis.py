"""Meaningful negative calibration/ABI/overflow/coverage cases before runtime."""
import copy,hashlib,json
from pathlib import Path
from timing_analysis import timing
k=Path(__file__).resolve().parent;dest=k/'analysis-tests.json';assert not dest.exists()
def synthetic(mode):
 lines=['SOLID_stage_pass 0 1 0','SOLID_stage_pass 1 1 0']
 for kind in range(5):
  for phase in range(2):
   lines.append('PROFILE_CALL_kind_phase_result %d %d 1'%(kind,phase));a=[0]*32
   a[:7]=[0x544d5758,113,128,mode,1000000,0,128];a[9]=2
   for i in range(4):a[14+3*i]=100+kind*2+phase;a[15+3*i]=(1000+kind*2+phase)*mode
   a[26]=256+2*sum(a[14+3*i] for i in range(4))*mode
   label='PROFILE_'+('AFTER' if phase else 'BEFORE')+'_kind_index_value'
   lines.extend('%s %d %d %d'%(label,kind,index,v) for index,v in enumerate(a))
 return lines
positive=[timing('\n'.join(synthetic(mode)),mode)['passed'] for mode in [0,1]];assert all(positive)
cases=[]
for label,index,value in [('bad_magic',0,0),('bad_version',1,112),('wrong_size',2,124),('wrong_mode',3,0),('zero_frequency',4,0),('negative_frequency',5,0x80000000),('missing_calibration',6,127),('regression_range',7,3),('timer_error',11,1),('overflow',12,1),('reserved13',13,1),('bad_reads',26,0),('reserved31',31,1)]:
 lines=synthetic(1);needle='PROFILE_BEFORE_kind_index_value 0 %d '%index
 lines=[needle+str(value) if v.startswith(needle) else v for v in lines]
 assert not timing('\n'.join(lines),1)['passed'],label;cases.append(label)
for label,transform in [('missing_packet',lambda lines:[v for v in lines if v!='PROFILE_AFTER_kind_index_value 0 31 0']),('duplicate_packet',lambda lines:lines+['PROFILE_AFTER_kind_index_value 0 31 0']),('wrong_solid',lambda lines:[v.replace('SOLID_stage_pass 1 1 0','SOLID_stage_pass 1 0 0') for v in lines])]:
 assert not timing('\n'.join(transform(synthetic(1))),1)['passed'],label;cases.append(label)
dest.write_text(json.dumps(dict(passed=True,positive_modes=2,negative_cases=cases,pins={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['test-timing-analysis.py','timing_analysis.py']}),indent=2)+'\n');print('2 positive modes/16 corrupt-contract cases passed')
