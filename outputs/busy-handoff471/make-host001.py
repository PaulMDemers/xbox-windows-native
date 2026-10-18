"""Use actual471 wrapper/stub with the reviewed470 hardware interface model."""
import json
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'marker-capture468';S=K.parent/'marker-handoff466'
assert not (K/'test-wrapper.c').exists()
b=json.loads((K/'build001.json').read_text());t=(K.parent/'marker-busy470/test.c').read_text()
model=t[t.index('static int mode,stage'):t.index('static void trap(')]
expected=t[t.index('static const unsigned expected[51]'):t.index(';',t.index('static const unsigned expected[51]'))+1]
def ns(s):return s.replace('468','471').replace('0x383634','0x313734')
s=ns((P/'test-wrapper.c').read_text());a=s.index('static int mode,stage');z=s.index('static void trap(',a)
m=model.replace('r[8]',f'((uint32_t*){b["wrapper_symbols"]["before_marker_record"]})[8]')
m=m.replace('writes','port_writes').replace('reads','port_reads').replace('static void output(','static void output_port(')
s=s[:a]+m+s[z:]
s=s.replace('static int case_id,fmode,','static int new_success;\nstatic int case_id,fmode,')
s=s.replace('case_id<85','case_id<104').replace('mode=case_id>=74?8:', 'mode=case_id>=85?32+case_id-85:case_id>=74?8:')
s=s.replace('stage=1;','stage=1;\n        new_success=case_id>=85 && (mode<=37 || mode>=49);')
s=s.replace('&& case_id<55','&& (case_id<55 || new_success)')
(K/'test-wrapper.c').write_text(s)
(K/'host001.py').write_text((P/'host001.py').read_text().replace('xwn468','xwn471').replace('85','104'))
(K/'Host001.ps1').write_text((K/'Build001.ps1').read_text().replace('build001.py','host001.py'))
s=(S/'test-stub.c').read_text();a=s.index('static int mode,stage');z=s.index('static void trap(',a)
s=s[:a]+model.replace('r[8]','record[8]')+s[z:]
a=s.index('static const unsigned results[32]');z=s.index(';',a)+1
s=s[:a]+expected.replace('expected[51]','results[51]')+s[z:]
s=s.replace('mode<32','mode<51')
assert str(b['stub_symbols']['after_stack_record']) in s
(K/'test-stub.c').write_text(s);(K/'enter-stub.S').write_bytes((S/'enter-stub.S').read_bytes())
(K/'stub-host001.py').write_text((S/'stub-host001.py').read_text().replace('xwn466','xwn471').replace('26 actual post-stack','45 actual post-stack').replace('cases=26','cases=45'))
(K/'StubHost001.ps1').write_text((K/'Host001.ps1').read_text().replace('host001.py','stub-host001.py'))
(K/'decode.py').write_text(ns((P/'decode.py').read_text()))
(K/'refusal_decode.py').write_text(ns((P/'refusal_decode002.py').read_text()).replace('from failure_marker002 import','from failure_marker import'))
s=(P/'failure_marker002.py').read_text().replace('unchanged465','corrected470').replace('r[8]&~0x810','r[8]&~0x818')
(K/'failure_marker.py').write_text(s)
(K/'marker_decode.py').write_bytes((P/'marker_decode.py').read_bytes())
