"""Author748 from closed746 source only, never its runtime."""
from pathlib import Path
import json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-end746'
assert not (K/'probe.c').exists()
names=['main.c','layout.c','layout.h','probe.c','probe.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','audit_collection.py']
for n in names:(K/n).write_text((O/n).read_text().replace('746','748').replace('crtc_end_control','crtc_total_control'),newline='\n')
def edit(n,changes):
 p=K/n;s=p.read_text()
 for a,b in changes:assert a in s,(n,a);s=s.replace(a,b)
 p.write_text(s,newline='\n')
edit('probe.h',[('};',' uint32_t c0_before,c0_target,c0_attempted,c0_after,c0_restored,c0_cleanup_mask,c4_after_c0,c5_after_c0;\n};')])
edit('probe.c',[
 ('Distinct CR05 low-five-bit checkpoint after','Distinct CR00 total checkpoint after'),
 ('the preserving prefix, seven horizontal words, and qualified CR04 write.','the preserving prefix, seven horizontal words, and qualified CR04/CR05 writes.'),
 (' o->c5_after=o->c4_after=0xffffffff;', ' o->c5_after=o->c4_after=0xffffffff;\n o->c0_after=o->c0_restored=o->c4_after_c0=o->c5_after_c0=0xffffffff;'),
 (' o->c4_before=cr(4);o->c5_before=cr(5);',' o->c4_before=cr(4);o->c5_before=cr(5);o->c0_before=cr(0);'),
 ('o->c5_before!=0x31)admitted=0;', 'o->c5_before!=0x31 || o->c0_before!=0xc8)admitted=0;'),
 (' o->forward_status=0x748;\nrestore:',""" /* Next original CRTC total byte: (779/8)-5 == 92. */
 o->c0_target=(779u/8u)-5u;o->c0_attempted=1;cw(0,(uint8_t)o->c0_target);o->forward_status=0x748e;
 o->c0_after=cr(0);o->c4_after_c0=cr(4);o->c5_after_c0=cr(5);
 if(o->c0_after!=o->c0_target || o->c4_after_c0!=93 || o->c5_after_c0!=o->c5_target)goto restore;
 o->forward_status=0x748;
restore:"""),
 (' if(o->c5_attempted)cw(5,',' if(o->c0_attempted)cw(0,(uint8_t)o->c0_before);\n if(o->c5_attempted)cw(5,'),
 (' o->c4_restored=cr(4);o->c5_restored=cr(5);',' o->c4_restored=cr(4);o->c5_restored=cr(5);o->c0_restored=cr(0);\n if(o->c0_restored!=o->c0_before)o->c0_cleanup_mask=1;'),
 ('if(!o->h_cleanup_mask && !o->c4_cleanup_mask)', 'if(!o->h_cleanup_mask && !o->c4_cleanup_mask && !o->c0_cleanup_mask)'),
 (' if(o->c4_cleanup_mask)o->code=0x748c;',' if(o->c4_cleanup_mask)o->code=0x748c;\n if(o->c0_cleanup_mask)o->code=0x748f;')])
edit('main.c',[('words[116]','words[124]'),('i<116','i<124'),('result.h_cleanup_mask || result.c4_cleanup_mask','result.h_cleanup_mask || result.c4_cleanup_mask || result.c0_cleanup_mask'),('result.code==0x748d)','result.code==0x748d || result.code==0x748e)')])
edit('Makefile',[('Kernel\\ CR05','Kernel\\ CR00')])
edit('physical.py',[('CR04 and CR05 bytes','CR04, CR05 and CR00 bytes'),('CR05 checkpoint after qualified horizontal prefix and CR04','CR00 checkpoint after qualified horizontal prefix and CR04/CR05')])
edit('audit_collection.py',[('len(v)==116','len(v)==124'),('0x748d]','0x748d,0x748e]')])
(K/'lineage001.json').write_text(json.dumps({'source_only_reuse':True,'closed_runtime_reused':False,'files':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'delta':'CR00fullbyte afterCR04/CR05; neighbor checks; reverse ownvalue recovery; separateCR00cleanup'},indent=2)+'\n',newline='\n')
print('Prepared748 source only')
