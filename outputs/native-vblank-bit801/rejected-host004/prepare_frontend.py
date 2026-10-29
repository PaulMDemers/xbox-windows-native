"""Source-only 799 bridge derivation; new report layout and compact 801 payload."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'native-vdisplay-low799'
ns=lambda s:re.sub(r'(?<![0-9])799(?![0-9])','801',re.sub(r'0x799(?=[0-9a-f]*\b)','0x801',s))
mapping={'23424':'23040','23423':'23039','23425':'23041','0x5b80':'0x5a00',
 '0x6b80':'0x6a00','0x6b84':'0x6a04','0x6bbc':'0x6a3c','0x6bc0':'0x6a40',
 '0x75c0':'0x74b8','0x7600':'0x7500','0x7e00':'0x7d00','0x7e04':'0x7d04',
 '0x208b80':'0x208a00','0xa40':'0xab8','2560':'2680','512':'768'}
remap=lambda s:re.sub(r'(?<![0-9a-zA-Z])(?:'+'|'.join(map(re.escape,mapping))+r')(?![0-9a-zA-Z])',lambda m:mapping[m[0]],s)
old=','.join(hex(i) for i in [0x8d4]+[0x6bc0+4*j for j in [30,100,108,495,525,555,585,615,610,613,614]])
new=[0,0x8d4]+[0x6a40+4*j for j in [30,100,108,525,555,585,615,645,640,643,644]]
names=['main004.c','layout004.c','layout.h','plan.c','plan.h','plan_test002.py','page002.c','page.h','page_tool003.c',
 'bridge002.S','fixture.S','link.ld','Makefile','payload_build007.py','host_build006.py','relocate003.py','relocate004.py',
 'cpu003.py','integration010.py','optical_oracle.py','optical_review003.py','build010.py','page_review006.py',
 'page_boundary007.py','plan_review003.py','linked_review005.py','physical007.py','link_review010.py']
for n in names:
 s=ns((O/n).read_text()).replace('native-vdisplay-low801','native-vblank-bit801')
 if n in ['bridge002.S','optical_review003.py']:
  assert old in s;s=s.replace(old,'OFFSET_PLACEHOLDER')
 s=remap(s).replace('OFFSET_PLACEHOLDER',','.join(hex(i) for i in new[1:]))
 if n=='payload_build007.py':s=s.replace("'probe.c'","'probe-compact.c'")
 if n=='integration010.py':s=s.replace("'<640I'","'<670I'")
 if n in ['relocate003.py','relocate004.py']:s=s.replace('len(rows)==18','len(rows)==19')
 if n=='host_build006.py':s=s.replace('len(absolute)==13','len(absolute)==14').replace('payload_reloc[13]','payload_reloc[14]')
 if n=='physical007.py':s=s.replace('CR12 display-end low byte','CR09 vertical-blank-start bit5').replace('CR12 CF/DF/CF, eight neighbors and own recovery before thirdCR07','CR09 60/40/60, eight neighbors and own recovery before CR12')
 p=K/n;assert not p.exists();p.write_bytes(s.encode())
(K/'frontend-lineage001.json').write_text(json.dumps(dict(source_only=True,closed_runtime_reuse=False,
 sources={n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},mapping=mapping,
 optical_offsets=new,allocation_bytes=32768,payload=[4096,0x6a00],request=[0x6a00,0x6a3c],
 result=[0x6a40,0x74b8],guard=[0x74b8,0x7500],IDT=[0x7500,0x7d00],stack=[0x7d00,0x8000],
 scope='Candidate only; new actual stack, guard, relocation and CPU qualification required'),indent=2)+'\n')
print('Prepared801 frontend; no build/stage/launch')
