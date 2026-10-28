"""Author750 from closed748 source only; no prior runtime reopened."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;O=K.parent/'crtc-total748'
names=['main.c','layout.c','layout.h','probe.c','probe.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','audit_collection.py']
assert not (K/'probe.c').exists()
for n in names:(K/n).write_text((O/n).read_text().replace('748','750').replace('crtc_total_control','crtc_blank_start_control'),newline='\n')
def edit(n,changes):
 p=K/n;s=p.read_text()
 for a,b in changes:assert a in s,(n,a);s=s.replace(a,b)
 p.write_text(s,newline='\n')
edit('probe.h',[('};',' uint32_t c2_before,c2_target,c2_attempted,c2_after,c2_restored,c2_cleanup_mask,c0_after_c2,c4_after_c2,c5_after_c2;\n};')])
edit('probe.c',[
 ('Distinct CR00 total checkpoint','Distinct CR02 blank-start checkpoint'),
 ('qualified CR04/CR05 writes.','qualified CR04/CR05/CR00 writes.'),
 (' o->c0_after=o->c0_restored=o->c4_after_c0=o->c5_after_c0=0xffffffff;',' o->c0_after=o->c0_restored=o->c4_after_c0=o->c5_after_c0=0xffffffff;\n o->c2_after=o->c2_restored=o->c0_after_c2=o->c4_after_c2=o->c5_after_c2=0xffffffff;'),
 ('o->c0_before=cr(0);','o->c0_before=cr(0);o->c2_before=cr(2);'),
 ('o->c0_before!=0xc8)admitted=0;','o->c0_before!=0xc8 || o->c2_before!=0x9f)admitted=0;'),
 (' o->forward_status=0x750;\nrestore:', ''' /* Next original horizontal blank-start byte: (720/8)-1 == 89. */
 o->c2_target=(720u/8u)-1u;o->c2_attempted=1;cw(2,(uint8_t)o->c2_target);o->forward_status=0x75010;
 o->c2_after=cr(2);o->c0_after_c2=cr(0);o->c4_after_c2=cr(4);o->c5_after_c2=cr(5);
 if(o->c2_after!=o->c2_target || o->c0_after_c2!=o->c0_target || o->c4_after_c2!=93 || o->c5_after_c2!=o->c5_target)goto restore;
 o->forward_status=0x750;
restore:'''),
 (' if(o->c0_attempted)cw(0,',' if(o->c2_attempted)cw(2,(uint8_t)o->c2_before);\n if(o->c0_attempted)cw(0,'),
 ('o->c0_restored=cr(0);','o->c0_restored=cr(0);o->c2_restored=cr(2);\n if(o->c2_restored!=o->c2_before)o->c2_cleanup_mask=1;'),
 ('&& !o->c0_cleanup_mask){','&& !o->c0_cleanup_mask && !o->c2_cleanup_mask){'),
 (' if(o->c0_cleanup_mask)o->code=0x750f;',' if(o->c0_cleanup_mask)o->code=0x750f;\n if(o->c2_cleanup_mask)o->code=0x75011;')])
edit('main.c',[('words[124]','words[133]'),('i<124','i<133'),('result.c0_cleanup_mask){','result.c0_cleanup_mask || result.c2_cleanup_mask){'),('result.code==0x750e)','result.code==0x750e || result.code==0x75010)')])
edit('Makefile',[('Kernel\\ CR00','Kernel\\ CR02')])
edit('physical.py',[('CR04, CR05 and CR00 bytes','CR04, CR05, CR00 and CR02 bytes'),('CR00 checkpoint after qualified horizontal prefix and CR04/CR05','CR02 checkpoint after qualified horizontal prefix and CR04/CR05/CR00')])
edit('audit_collection.py',[('len(v)==124','len(v)==133'),('0x750e]','0x750e,0x75010]')])
(K/'lineage001.json').write_text(json.dumps({'source_only_reuse':True,'closed_runtime_reused':False,'files':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'delta':'CR02 after CR00, full-byte and CR00/04/05 interaction checks; newest-first own-value recovery; separate CR02 cleanup mask'},indent=2)+'\n',newline='\n')
print('Prepared750 sources')
