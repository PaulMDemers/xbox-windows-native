"""Author753 from closed750 source only; no runtime reused."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;O=K.parent/'crtc-blank-start750'
names=['main.c','layout.c','layout.h','probe.c','probe.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','audit_collection.py']
assert not (K/'probe.c').exists()
for n in names:(K/n).write_text((O/n).read_text().replace('750','753').replace('crtc_blank_start_control','crtc_blank_end_control'),newline='\n')
def edit(n,changes):
 p=K/n;s=p.read_text()
 for a,b in changes:assert a in s,(n,a);s=s.replace(a,b)
 p.write_text(s,newline='\n')
edit('probe.h',[('};',' uint32_t c3_before,c3_target,c3_attempted,c3_after,c3_restored,c3_cleanup_mask,c0_after_c3,c2_after_c3,c4_after_c3,c5_after_c3;\n};')])
edit('probe.c',[
 ('Distinct CR02 blank-start checkpoint','Distinct CR03 blank-end checkpoint'),
 ('qualified CR04/CR05/CR00 writes.','qualified CR04/CR05/CR00/CR02 writes.'),
 (' for(unsigned i=0;i<7;++i)o->h_checked', ' o->c3_after=o->c3_restored=o->c0_after_c3=o->c2_after_c3=o->c4_after_c3=o->c5_after_c3=0xffffffff;\n for(unsigned i=0;i<7;++i)o->h_checked'),
 ('o->c2_before=cr(2);','o->c2_before=cr(2);o->c3_before=cr(3);'),
 ('o->c2_before!=0x9f)admitted=0;','o->c2_before!=0x9f || o->c3_before!=0x8c)admitted=0;'),
 (' o->forward_status=0x753;\nrestore:',""" /* Next original horizontal blank-end byte; preserve own upper three bits. */
 o->c3_target=(o->c3_before&0xe0)|(((779u/8u)-1u)&0x1f);
 o->c3_attempted=1;cw(3,(uint8_t)o->c3_target);o->forward_status=0x75312;
 o->c3_after=cr(3);o->c0_after_c3=cr(0);o->c2_after_c3=cr(2);o->c4_after_c3=cr(4);o->c5_after_c3=cr(5);
 if(o->c3_after!=o->c3_target || o->c0_after_c3!=o->c0_target || o->c2_after_c3!=o->c2_target || o->c4_after_c3!=93 || o->c5_after_c3!=o->c5_target)goto restore;
 o->forward_status=0x753;
restore:"""),
 (' if(o->c2_attempted)cw(2,',' if(o->c3_attempted)cw(3,(uint8_t)o->c3_before);\n if(o->c2_attempted)cw(2,'),
 ('o->c2_restored=cr(2);','o->c2_restored=cr(2);o->c3_restored=cr(3);\n if(o->c3_restored!=o->c3_before)o->c3_cleanup_mask=1;'),
 ('&& !o->c2_cleanup_mask){','&& !o->c2_cleanup_mask && !o->c3_cleanup_mask){'),
 (' if(o->c2_cleanup_mask)o->code=0x75311;',' if(o->c2_cleanup_mask)o->code=0x75311;\n if(o->c3_cleanup_mask)o->code=0x75313;')])
edit('main.c',[('words[133]','words[143]'),('i<133','i<143'),('result.c2_cleanup_mask){','result.c2_cleanup_mask || result.c3_cleanup_mask){'),('result.code==0x75310)','result.code==0x75310 || result.code==0x75312)')])
edit('Makefile',[('Kernel\\ CR02','Kernel\\ CR03')])
edit('physical.py',[('CR04, CR05, CR00 and CR02 bytes','CR04, CR05, CR00, CR02 and CR03 bytes'),('CR02 checkpoint after qualified horizontal prefix and CR04/CR05/CR00','CR03 checkpoint after qualified horizontal prefix and CR04/CR05/CR00/CR02')])
edit('audit_collection.py',[('len(v)==133','len(v)==143'),('0x75310]','0x75310,0x75312]')])
(K/'lineage001.json').write_text(json.dumps({'source_only_reuse':True,'closed_runtime_reused':False,'files':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'delta':'CR03 after CR02; full byte and CR00/02/04/05 checks, own-value recovery'},indent=2)+'\n',newline='\n')
