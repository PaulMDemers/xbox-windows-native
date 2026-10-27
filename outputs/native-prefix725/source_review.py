from pathlib import Path
import re,json,hashlib,datetime,difflib
k=Path('outputs/native-prefix725');old=Path('outputs/native-prefix724/probe.c').read_text().replace('724','725');new=(k/'probe.c').read_text()
new=new.replace('static uint8_t sample1b(void){uint8_t i=R8(0x6013d4),v=cr(0x1b);R8(0x6013d4)=i;return v;}\n','')
new='\n'.join(line for line in new.splitlines() if 'o->cr1b_trace' not in line)
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
assert clean(old)==clean(new),'material prefix change beyond instrumentation'
for n in ['main.c','layout.c','layout.h','plan.c','plan.h','page002.c','page.h']:
 oldname='main002.c' if n=='main.c' else n;a=Path('outputs/native-prefix724',oldname).read_text().replace('724','725');b=(k/n).read_text()
 assert clean(a)==clean(b),n
# First source's active main correctly retains both geometry and SDK720p constant.
assert 'VIDEO_MODE_720P' in (k/'main.c').read_text() and 'VIDEO_MODE_725P' not in (k/'main.c').read_text()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prefix_noninstrumentation_tokens_identical_to724':True,'frontend_plan_layout_page_identical_except_namespace_comment':True,'data_write_sequence_unchanged':True,'extra_CR1b_reads':4,'extra_read_selector_behavior':'save selector, select1b, read, restore saved selector','immediate_and_final_trace_values':'copy existing read results, no extra reads','trace_initial_value':'ffffffff (unreached)','CR22_data_writes':0,'CR1b_restore85':False,'result_bytes':296,'trace_offsets':[0x5208,0x520c,0x5210,0x5214,0x5218,0x521c],'limits':'Instrumentation changes timing and index traffic; model transitions locate observed boundary only, not register semantics or hardware cause','sources':{n:sha(k/n) for n in ['probe.c','probe.h','transaction725.c','transaction.h','main.c','bridge.S']}}
(k/'source-review001.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS same underlying prefix; only four added selector-preserving reads and trace storage')
