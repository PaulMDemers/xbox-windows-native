"""Parser-only adversarial cases. Synthetic logs are never guest evidence."""
import json
from pathlib import Path
from sample_analysis import analyze
k=Path(__file__).resolve().parent
rows=['XWN_GDI_PROBE_VERSION 4 256 128','CAP_index_value 8 1024 0','CAP_index_value 10 576 0','IDENTITY_RESULT 1 0 0']
identity=[0x44525758,112,1024,576,4096,32,2359296,1]
rows += ['IDENTITY_index_value %d %d 0'%(i,v) for i,v in enumerate(identity)]
rows += ['COPY_stage_pass %d 1 0'%i for i in range(4)]
for kind in range(5):
    rows += ['TIMING_kind_count_ms %d 100 1500'%kind]
    for phase,label in enumerate(['BEFORE','AFTER']):
        rows += ['STATS_CALL_kind_phase_result %d %d 1'%(kind,phase),'STATS_LATENCY_kind_phase_ms %d %d 25'%(kind,phase)]
        a=[0]*32;a[:2]=[0x53525758,112];a[2]=kind*100+phase*100;a[16]=kind*100+phase*100;a[17]=kind*13107200+phase*13107200;a[20]=1
        rows += ['STATS_%s_kind_index_value %d %d %d'%(label,kind,i,v) for i,v in enumerate(a)]
rows+=['PASS 0 0 0'];good='\n'.join(rows)+'\n';assert analyze(good)['probe_passed']
bad={
 'missing_snapshot':good.replace('STATS_AFTER_kind_index_value 4 31 0\n',''),
 'mismatch':good.replace('STATS_AFTER_kind_index_value 0 19 0','STATS_AFTER_kind_index_value 0 19 1'),
 'saturated':good.replace('STATS_AFTER_kind_index_value 0 2 100','STATS_AFTER_kind_index_value 0 2 4294967295'),
 'negative_delta':good.replace('STATS_BEFORE_kind_index_value 0 2 0','STATS_BEFORE_kind_index_value 0 2 101'),
 'byte_underflow':good.replace('STATS_BEFORE_kind_index_value 0 18 0','STATS_BEFORE_kind_index_value 0 18 1'),
 'unsupported':good.replace('STATS_CALL_kind_phase_result 0 0 1','STATS_CALL_kind_phase_result 0 0 0'),
 'bad_version':good.replace('IDENTITY_index_value 1 112 0','IDENTITY_index_value 1 111 0'),
 'reserved':good.replace('STATS_AFTER_kind_index_value 0 21 0','STATS_AFTER_kind_index_value 0 21 1'),
 'duplicate':good.replace('STATS_AFTER_kind_index_value 4 31 0','STATS_AFTER_kind_index_value 4 30 0'),
 'missing_loop':good.replace('TIMING_kind_count_ms 2 100 1500\n',''),
 'truncated':good[:-11], 'garbage':good+'arbitrary input\n'}
for name,value in bad.items():assert not analyze(value)['probe_passed'],name
(k/'log-gate-tests.json').write_text(json.dumps(dict(passed=True,positive_synthetic_parser_case=True,rejected=list(bad),guest_evidence=False),indent=2)+'\n',encoding='utf-8')
print('Synthetic parser acceptance plus12 adversarial rejections passed')
