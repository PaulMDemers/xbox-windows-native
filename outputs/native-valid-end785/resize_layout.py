"""Fresh785 layout: preserve32KiB allocation, move owned IDT above result.
No hardware access. Failed14080-byte payload build remains immutable.
"""
from pathlib import Path
import json,hashlib
K=Path(__file__).resolve().parent
edits={}
for n in ['main.c','page002.c','page_tool003.c','page_review003.py','bridge.S']:
 p=K/n;old=p.read_bytes();s=old.decode().replace('14080','15360')
 if n=='page002.c':s=s.replace('base+0x4800','base+0x5800').replace('at=0x4800+8*i','at=0x5800+8*i')
 if n=='bridge.S':s=s.replace('0xa5a5a5a5,0x5ffc(%ebp)','0xa5a5a5a5,0x6000(%ebp)')
 p.write_text(s,newline='\n');edits[n]={'before':hashlib.sha256(old).hexdigest(),'after':hashlib.sha256(p.read_bytes()).hexdigest()}
p=K/'payload_build004.py';s=p.read_text().replace('payload004','payload005').replace('14080','15360')
(K/'payload_build005.py').write_text(s,newline='\n')
for n in ['model.py','host_build005.py','audit_collection005.py','review_prepare002.py']:
 p=K/n;p.write_text(p.read_text().replace('payload004','payload005'),newline='\n')
p=K/'cpu002.py';s=p.read_text().replace('4096+0x4800','4096+0x5000').replace('[0x1000:0x4800]','[0x1000:0x5000]');p.write_text(s,newline='\n')
(K/'layout-change001.json').write_text(json.dumps({'allocation_bytes':32768,'old_payload_reserve':14080,'failed_raw_size':14744,'new_payload_reserve':15360,'regions':{'bridge_and_descriptors':[0,4096],'payload':[4096,19456],'payload_guard':[19456,20480],'request':[20480,20540],'request_result_guard':[20540,20736],'result':[20736,22456],'result_guard':[22456,22528],'IDT':[22528,24576],'stack':[24576,32768]},'stack_low_guard_word':24576,'IDTR_limit':2047,'no_allocation_address_policy_change':True,'no_probe_source_change':True,'required_fresh_checks':['all256IDTentries and descriptor pointer','zero result and guard extents','payload relocation and exact binary','CPUtransition/fault handler on four mappings and negative cases','direct/fullpath/optical cases'],'edits':edits},indent=2)+'\n')
print('Fresh785 layout prepared; hardware remains untouched')
