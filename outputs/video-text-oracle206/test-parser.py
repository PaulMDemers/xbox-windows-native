"""Reject corrupted actual closed204 text and lifecycle evidence. Host-only mutations."""
import hashlib,json
from pathlib import Path
from text_analysis import analyze
from runner_analysis import analyze as lifecycle
k=Path(__file__).resolve().parent;dest=k/'parser-tests.json';assert not dest.exists()
art=k/'emu-control001/artifacts';raw=(art/'sample0/gdi-baseline.txt').read_bytes();log=raw.decode('ascii')
assert analyze(log,0)['passed'];checks=1
rows=log.splitlines()
def replace(label,case,index,new):
 matches=[i for i,v in enumerate(rows) if v.split()[:3]==[label,str(case),str(index)]];assert len(matches)==1
 result=list(rows);result[matches[0]]=label+' '+str(case)+' '+str(index)+' '+str(new);return '\n'.join(result)+'\n'
for label,case,index,value in [('TEXT_AFTER_case_index_value',0,0,0),('TEXT_AFTER_case_index_value',0,3,1),
 ('TEXT_AFTER_case_index_value',0,11,1),('TEXT_AFTER_case_index_value',0,20,3),('TEXT_AFTER_case_index_value',0,29,1),
 ('TEXT_AFTER_case_index_value',0,30,1),('TEXT_AFTER_case_index_value',0,27,0),('TEXT_AFTER_case_index_value',0,26,0)]:
 assert not analyze(replace(label,case,index,value),0)['passed'];checks+=1
for old,new in [('TEXT_CASE_case_pass 12 1 0','TEXT_CASE_case_pass 12 0 0'),
 ('TEXT_SCANOUT_case_result_mismatches 0 1 0','TEXT_SCANOUT_case_result_mismatches 0 1 1')]:
 assert old in log and not analyze(log.replace(old,new,1),0)['passed'];checks+=1
assert not analyze(log,1)['passed'];checks+=1
assert not analyze(log.replace('TEXT_AFTER_case_index_value 0 0 ', 'TEXT_AFTER_case_index_value 1 0 ',1),0)['passed'];checks+=1
assert not analyze(log.replace('TEXT_CASE_case_pass 12 1 0\r\n',''),0)['passed'];checks+=1
attempt=(art/'attempt.log').read_text(encoding='ascii');snaps=[(art/n).read_bytes() for n in ['setup-before.log','setup-after.log']];wizard=(art/'wizard201.log').read_bytes()
assert lifecycle(attempt,snaps,wizard,1)['idle_branch_passed'];checks+=1
for old,new in [('WIZARD_JOIN_RESULT 0','WIZARD_JOIN_RESULT 258'),('WIZARD_EXIT 0','WIZARD_EXIT 15'),
                ('INSTALL_BEFORE_SAMPLE 0','INSTALL_BEFORE_SAMPLE 258'),('INSTALL_FINAL_RESULT 0','INSTALL_FINAL_RESULT 258'),
                ('NORMAL_RESTART_REQUEST 0','NORMAL_RESTART_REQUEST 1')]:
 assert old in attempt and not lifecycle(attempt.replace(old,new,1),snaps,wizard,1)['idle_branch_passed'];checks+=1
assert not lifecycle(attempt,[snaps[0],snaps[1]+b'x'],wizard,1)['idle_branch_passed'];checks+=1
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=True,checks=checks,host_only=True,runtime_qualified=False,source_pins={p.name:sha(p) for p in [k/'text_analysis.py',k/'runner_analysis.py',k/'boundary_analysis.py',Path(__file__)]},
 input_pins={p.relative_to(k).as_posix():sha(p) for p in [art/'sample0/gdi-baseline.txt',art/'attempt.log',art/'wizard201.log',art/'setup-before.log',art/'setup-after.log']},
 limits='Mutations of closed actual emulator logs only; no synthesized runtime result or event waiver.')
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('Actual text/lifecycle evidence rejection checks:',checks)
