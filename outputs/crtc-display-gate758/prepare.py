"""Fresh758 source-only CR17 clear/recovery control; closed756 sources only."""
from pathlib import Path
import re,json,hashlib
k=Path(__file__).resolve().parent;o=k.parent/'crtc-blank-bit756'
def ns(s):return re.sub(r'(?<![0-9])756(?![0-9])','758',re.sub(r'0x756(?=[0-9a-f]*\b)','0x758',s))
names=['main.c','layout.c','layout.h','probe.c','probe.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','audit_collection.py']
assert not (k/'main.c').exists()
for n in names:(k/n).write_text(ns((o/n).read_text()),newline='\n')
p=k/'probe.h';s=p.read_text().replace('\n};','\n uint32_t c17_before,c17_target,c17_attempted,c17_after,c17_restored,c17_cleanup_mask,c0_after_c17,c2_after_c17,c3_after_c17,c4_after_c17,c5_after_c17;\n};');p.write_text(s,newline='\n')
p=k/'probe.c';s=p.read_text().replace('Distinct second CR05 bit7 checkpoint','Distinct CR17 bit7 clear checkpoint')
s=s.replace(' for(unsigned i=0;i<7;++i)o->h_checked',' o->c17_after=o->c17_restored=o->c0_after_c17=o->c2_after_c17=o->c3_after_c17=o->c4_after_c17=o->c5_after_c17=0xffffffff;\n for(unsigned i=0;i<7;++i)o->h_checked')
block=''' /* Next original CR17 RMW: clear bit7 only, with fresh own-byte capture. */
 o->forward_status=0x75816;o->c17_before=cr(0x17);
 if(o->c17_before!=o->crtc_checked[1])goto restore;
 o->c17_target=o->c17_before&0x7f;o->c17_attempted=1;cw(0x17,(uint8_t)o->c17_target);
 o->c17_after=cr(0x17);o->c0_after_c17=cr(0);o->c2_after_c17=cr(2);o->c3_after_c17=cr(3);o->c4_after_c17=cr(4);o->c5_after_c17=cr(5);
 if(o->c17_after!=o->c17_target || o->c0_after_c17!=o->c0_target || o->c2_after_c17!=o->c2_target || o->c3_after_c17!=o->c3_target || o->c4_after_c17!=93 || o->c5_after_c17!=o->c5b_target)goto restore;
'''
s=s.replace(' o->forward_status=0x758;\nrestore:',block+' o->forward_status=0x758;\nrestore:')
s=s.replace(' if(o->c5b_attempted){',' if(o->c17_attempted){cw(0x17,(uint8_t)o->c17_before);o->c17_restored=cr(0x17);if(o->c17_restored!=o->c17_before)o->c17_cleanup_mask=1;}\n if(o->c5b_attempted){')
s=s.replace(' && !o->c5b_cleanup_mask){',' && !o->c5b_cleanup_mask && !o->c17_cleanup_mask){')
s=s.replace(' if(o->forward_status!=0x7581 && !o->selectors_restored)',' if(o->c17_cleanup_mask)o->code=0x75817;\n if(o->forward_status!=0x7581 && !o->selectors_restored)')
p.write_text(s,newline='\n')
p=k/'main.c';s=p.read_text().replace('crtc_blank_bit_control','crtc_display_gate_control').replace('words[153]','words[164]').replace('i<153','i<164').replace('result.c5b_cleanup_mask){','result.c5b_cleanup_mask || result.c17_cleanup_mask){').replace('result.code==0x75814)','result.code==0x75814 || result.code==0x75816)');assert 'frequency!=3375000' in s;p.write_text(s,newline='\n')
p=k/'physical.py';s=p.read_text().replace('second CR05 bit7 checkpoint','CR17 bit7 clear checkpoint').replace('then second CR05 bit7 write with','then second CR05 bit7 write and CR17 bit7 clear with');p.write_text(s,newline='\n')
p=k/'audit_collection.py';s=p.read_text().replace('crtc_blank_bit_control','crtc_display_gate_control').replace('len(v)==153','len(v)==164').replace('0x75814]','0x75814,0x75816]');p.write_text(s,newline='\n')
(k/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent756':{n:hashlib.sha256((o/n).read_bytes()).hexdigest() for n in names},'delta':'CR17 fresh read, clear bit7, check CR00/02/03/04/05; restore own CR17 first then prior reverse recovery;164words656bytes; clock3375000 unchanged'},indent=2)+'\n',newline='\n')
