"""Extend only allocation metadata and bridge integration for fresh813."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;A=K.parent/'native-linecompare-bit811'
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x811(?=[0-9a-f]{0,2}$)','0x813',p).replace('0x8110000d','0x8130000d') if i%2 else p.replace('811','813') for i,p in enumerate(parts)).replace('native-linecompare-bit813','native-linecompare-low813')
replacements={
 'host_build009.py':[('len(absolute)==34','len(absolute)==35'),('payload_reloc[34]','payload_reloc[35]')],
 'page002.c':[('count!=34','count!=35')],
 'main004.c':[('payload_reloc,34,','payload_reloc,35,')],
 'page_tool003.c':[],
 'relocate003.py':[('len(rows)==42','len(rows)==43')],
 'relocate004.py':[('len(rows)==42','len(rows)==43')],
 'page_review008.py':[('24256,relptr,34,','24256,relptr,35,'),('range(34)','range(35)')],
 'page_boundary009.py':[('24256,relptr,34,','24256,relptr,35,'),('range(34)','range(35)')],
 'link_review012.py':[("'absolute_relocations':34","'absolute_relocations':35")],
}
for n,pairs in replacements.items():
 p=K/n;s=p.read_text()
 if n=='page_tool003.c':s=re.sub(r'\b34\b','35',s)
 for a,b in pairs:s=s.replace(a,b)
 p.write_bytes(s.encode())
s=ns((A/'integration014.py').read_text())
s=s.replace('0x7458','0x74d0').replace('<790I','<820I').replace('op+3160','op+3280')
s=s.replace("out=K/'integration012.json'","out=K/'integration001.json'")
s=s.replace("state={'cl9writes'","state={'cl18writes':0,'cl9writes'")
a="    if i==9 and state['cl7writes']==1"
assert s.count(a)==1
s=s.replace(a,"""    if i==24:
     state['cl18writes']+=1
     assert state['cl18writes']<=2 and value==255
     assert word(790)==255 and word(791)==255 and word(792)==1
     assert state['cl9writes']==1 and word(1) in (0x81348,0x813)
     assert state['seq']==0x21 and state['gate']==5 and not hrestore
     cr[i]=value
    elif i==9 and state['cl7writes']==1""")
s=s.replace('    assert word(765)==0','    assert word(795)==0 and (not word(792) or word(794)==word(790))\n    assert word(765)==0')
a=" final=bytes(c.mem_read(base,32768));v=list(struct.unpack_from('<820I',final,0x6800))"
assert s.count(a)==1
s=s.replace(a,a+"""
 full=v[:];v=v[:790]
 assert full[795]==0
 if state['cl18writes']:
  assert state['cl18writes']==2 and full[790:796]==[255,255,1,255,255,0]
  assert full[796:]==[n for x in [12,62,64,233,223,223,140,16] for n in [x,x,x]]
  assert [(i,x) for i,x in cw if i==24]==[(24,255),(24,255)]
 else:assert full[792]==0
 full_cw=cw[:];cw=[(i,x) for i,x in cw if i!=24]
""")
s=s.replace("'raw_result':v,","'raw_result':full,").replace("'CRTC_writes':cw,","'CRTC_writes':full_cw,")
s=s.replace('v[645],v[675],v[705],v[735],v[765],v[760],v[763],v[764]','full[675],full[705],full[735],full[765],full[795],full[790],full[793],full[794]')
# Full 1,014 prefix instruction cases plus 51 CR18 fault cases execute separately.
# Here exercise relocated bridge/stack/report ownership and wrapper admission.
selection=""" if not (name.startswith(('prefix-','pci-','timer-','null-','baseline-','first-mismatch-')) or name in ['IF-refusal','PAE-refusal','wrapper-baseline','CR1b05-preservation-mismatch','cl9-undo-0','cl9-undo-8','cl7-undo-0','horizontal-cleanup-0','horizontal-cleanup-6','c13-wrong-write','c13-wrong-undo','selector']):return
"""
at=s.index(' assert time.monotonic()<deadline',s.index('def run('));s=s[:at]+selection+s[at:]
(K/'integration001.py').write_bytes(s.encode())
print('813 metadata35 absolute/43 total relocations; bounded representative bridge integration derived')
