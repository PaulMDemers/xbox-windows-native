"""Derive a fresh combined native mode candidate from pinned closed sources only."""
from pathlib import Path
import json,hashlib,re
K=Path(__file__).resolve().parent;W=K.parents[1];A=K.parent/'native-mode-controls817';B=K.parent/'xcal-transaction704'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((A/'closed001.json').read_text())['passed']
pins={}
def source(d,n):
    p=d/n;pins[str(p.relative_to(W))]=sha(p);return p.read_text()
def put(n,s):
    with (K/n).open('x',encoding='utf-8',newline='\n') as f:f.write(s)
put('.gitattributes','* -text\n');put('.gitignore','__pycache__/\n')
for n in ['transaction.h','encoder.c','xcal_bus.c','xcal_bus.h','xcal_table.h','delay_candidate.h','gpu_types.h']:
    put(n,source(B,n))
s=source(B,'gpu_legacy.c');s=s.replace('b = 0x04;','b = NvGetCrtc(pbRegs, 0x1a) | 0x04;').replace('b = 0x00;','b = NvGetCrtc(pbRegs, 0x1a) & ~0x04;')
put('gpu_preserving.c',s)
s=source(B,'transaction003.c')
s=s.replace('HOST-ONLY transaction candidate; no XBE or physical admission.','Fresh818 complete-mode diagnostic; physical admission requires fresh host checks.')
s=s.replace('{0x19,0x10},{0x1b,5},{0x22,255},{0x33,0x11}','{0x19,0x10}')
s=s.replace('{0x1a,255,4}','{0x1a,255,0x3c}')
s=s.replace('static int check_setup(volatile uint8_t *g,int after_geometry)\n{','static int check_setup(volatile uint8_t *g,int after_geometry)\n{\n if(cr(g,0x1b)!=0x85 || cr(g,0x22)!=0xfe || cr(g,0x33)!=0x11)return 0;')
s=s.replace('if(!context(g)||r32(g,0x600800)!=r->base', 'if(cr(g,0x1a)!=0x38||cr(g,0x1b)!=0x85||cr(g,0x22)!=0xfe||cr(g,0x33)!=0x11||!context(g)||r32(g,0x600800)!=r->base')
put('transaction818.c',s)
for n in ['layout.h','layout004.c','plan.h','plan.c','page.h','page002.c','page_tool003.c','main004.c','Makefile','fixture.S','link.ld','optical_oracle.py','plan_test004.py','cpu006.py']:
    put(n,source(A,n).replace('817','818'))
s=source(A,'bridge003.S').replace('817','818')
start=s.index(' /*818: call returned.');end=s.index('10:sfence',start)
s=s[:start]+''' /* The transaction owns the new720x480 framebuffer on success. Never draw
  * a1280-pitch report over it. On failure the transaction reblanks; hold without
  * retry, kernel call, encoder restoration from firmware, or Windows handoff. */
 jmp 10f
'''+s[end:]
put('bridge003.S',s)
s=source(A,'payload_build008.py').replace('817','818')
s=s.replace("['transaction818.c','transaction.h','probe-pairs-native.c','probe.h']","['transaction818.c','transaction.h','encoder.c','xcal_bus.c','xcal_bus.h','xcal_table.h','delay_candidate.h','gpu_preserving.c','gpu_types.h']")
s=s.replace("str(K/'probe-pairs-native.c')","str(K/'encoder.c'),str(K/'xcal_bus.c'),str(K/'gpu_preserving.c')")
put('payload_build008.py',s)
put('relocate003.py',source(A,'relocate004.py').replace('assert rows and len(rows)==53','assert rows and len(rows)<256'))
s=source(A,'host_build009.py').replace('817','818').replace('assert len(absolute)==41','assert len(absolute)==ABSOLUTE_COUNT').replace("'static const struct reloc705 payload_reloc[41]={'","'static const struct reloc705 payload_reloc[ABSOLUTE_COUNT]={'")
put('host_build_template.py',s)
s=source(B,'cpu004.py').replace('xwn704/build003','xwn818/payload008').replace("K/'build003.json'","K/'payload008.json'").replace("K/'cpu004.json'","K/'model001.json'")
s=s.replace('0x19:0x10,0x1b:5,0x22:255,0x33:0x11','0x19:0x10').replace('0x1a:(255,4)','0x1a:(255,0x3c)')
s=s.replace('cr[9]&=0x7f;', 'cr[0x1a]=0x38;cr[0x1b]=0x85;cr[0x22]=0xfe;cr[0x33]=0x11;cr[9]&=0x7f;')
s=s.replace("assert key[1]!=0x11,'CR11 writes prohibited'", "assert key[1] not in (0x11,0x1b,0x22,0x33),'preserved register write prohibited'")
s=s.replace('deadline=time.monotonic()+240','deadline=time.monotonic()+600')
s=s.replace("run('blank-write-dropped'", "for i,v in [(0x1a,0),(0x1b,5),(0x22,255),(0x33,0)]:run('preserving-baseline-'+hex(i),pre=('cr',i,v),expected=5)\n run('blank-write-dropped'")
put('model001.py',s)
put('derivation001.json',json.dumps(dict(source_only=True,closed_runtime_reused=False,pins=pins,deltas=['Skip CR1b/CR22/CR33 writes; require measured and qualified85/FE/11 instead','CR1A bit2 preserving RMW38->3C; require full-byte3C','Fresh40KiB817 bridge/layout; no1280-pitch postcall overlay','Full bounded704 encoder/VGA/output sequence; host-only until fresh qualification'],physical_admission=False),indent=2)+'\n')
put('NEXT.md','#818 host preparation only\n\nFresh combined visible-mode candidate. No XBE/stage/launch yet. Build and test\nfull transaction, relocation, page/CPU handoff, compiled ownership, exact source\nand staged bytes. Physical success requires watched720x480 authored pattern;\na blank failure holds without retry. No Windows driver or desktop claim.\n')
print('818 fresh candidate prepared; no hardware access')
