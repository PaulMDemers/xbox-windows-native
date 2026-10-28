"""Source-only 773 frontend; fresh read-only probe before new vertical writes."""
from pathlib import Path
import json,hashlib,re
K=Path(__file__).resolve().parent;O=K.parent/'vertical-total773'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['main.c','layout.c','layout.h','Makefile','build.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','physical.py']
for n in names:
 s=(O/n).read_text().replace('773','775')
 if n=='main.c':
  s=s.replace('Kernel775 seven horizontal timing writes, recover before output-enable; no native handoff.','Kernel775 read-only vertical register snapshot; no native handoff.')
  s=s.replace('vertical_total_control','vertical_read_control').replace('words[280]','words[30]').replace('i<280','i<30')
  a=s.index('    /* Never draw or flush');z=s.index('    uint32_t *pixels=fb;',a)
  s=s[:a]+'    uint32_t color=recorded?0xff00ff:result.code==0x775?0x00ff00:0xff8000;\n'+s[z:]
 if n=='physical.py':
  s=s.replace('Kernel-context775 vertical display-end checkpoint','Kernel-context775 read-only vertical baseline')
  a=s.index("'purpose':");z=s.index(",'xbe_sha256'",a)
  s=s[:a]+"'purpose':'kernel-context three-pass read-only snapshot of seven vertical registers including NVVCRTC680808 and NVVVALIDSTART680814; no native handoff or custom timing writes; qualified SDK720p setup and automatic return after15seconds'"+s[z:]
  a=s.index("'observation':");z=s.index('}',a)
  s=s[:a]+"'observation':'authorized read-only vertical snapshot; one launch, automatic dashboard return intended; no custom timing writes or native handoff'"+s[z:]
 if n=='Makefile':s=s.replace('NVVTOTAL','vertical read-only snapshot')
 p=K/n;assert not p.exists();p.write_text(s,newline='\n')
(K/'.gitattributes').write_text('* -text\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtimes_reused':False,'parent773':{n:sha(O/n) for n in names},'purpose':'Read actual unreported680808 and680814 values before new write control'},indent=2)+'\n')
