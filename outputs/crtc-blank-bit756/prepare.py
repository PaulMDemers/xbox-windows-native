"""Fresh756 source-only CR05 bit7 extension; token-aware names, never runtime reuse."""
from pathlib import Path
import re,json,hashlib
k=Path(__file__).resolve().parent;o=k.parent/'crtc-blank-end754'
def ns(s):
 return re.sub(r'(?<![0-9])754(?![0-9])','756',re.sub(r'0x754(?=[0-9a-f]*\b)','0x756',s))
names=['main.c','layout.c','layout.h','probe.c','probe.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','clock_model.py','audit_logic.py','prefix_schema.py','physical.py','audit_collection.py']
assert not (k/'main.c').exists()
for n in names:(k/n).write_text(ns((o/n).read_text()),newline='\n')
p=k/'probe.h';s=p.read_text().replace('\n};','\n uint32_t c5b_before,c5b_target,c5b_attempted,c5b_after,c5b_restored,c5b_cleanup_mask,c0_after_c5b,c2_after_c5b,c3_after_c5b,c4_after_c5b;\n};');p.write_text(s,newline='\n')
p=k/'probe.c';s=p.read_text().replace('Distinct CR03 blank-end checkpoint','Distinct second CR05 bit7 checkpoint')
s=s.replace(' for(unsigned i=0;i<7;++i)o->h_checked', ' o->c5b_after=o->c5b_restored=o->c0_after_c5b=o->c2_after_c5b=o->c3_after_c5b=o->c4_after_c5b=0xffffffff;\n for(unsigned i=0;i<7;++i)o->h_checked')
new=''' /* Original second CR05 write: replace only horizontal blank-end bit7. */
 o->c5b_before=o->c5_after_c3;
 o->c5b_target=(o->c5b_before&0x7f)|((((779u/8u)-1u)&0x20)<<2);
 o->c5b_attempted=1;cw(5,(uint8_t)o->c5b_target);o->forward_status=0x75614;
 o->c5b_after=cr(5);o->c0_after_c5b=cr(0);o->c2_after_c5b=cr(2);o->c3_after_c5b=cr(3);o->c4_after_c5b=cr(4);
 if(o->c5b_after!=o->c5b_target || o->c0_after_c5b!=o->c0_target || o->c2_after_c5b!=o->c2_target || o->c3_after_c5b!=o->c3_target || o->c4_after_c5b!=93)goto restore;
'''
s=s.replace(' o->forward_status=0x756;\nrestore:',new+' o->forward_status=0x756;\nrestore:')
s=s.replace(' if(o->c3_attempted)cw(3,',' if(o->c5b_attempted){cw(5,(uint8_t)o->c5b_before);o->c5b_restored=cr(5);if(o->c5b_restored!=o->c5b_before)o->c5b_cleanup_mask=1;}\n if(o->c3_attempted)cw(3,')
s=s.replace(' && !o->c3_cleanup_mask){',' && !o->c3_cleanup_mask && !o->c5b_cleanup_mask){')
s=s.replace(' if(o->forward_status!=0x7561 && !o->selectors_restored)', ' if(o->c5b_cleanup_mask)o->code=0x75615;\n if(o->forward_status!=0x7561 && !o->selectors_restored)')
p.write_text(s,newline='\n')
p=k/'main.c';s=p.read_text().replace('crtc_blank_end_control','crtc_blank_bit_control').replace('words[143]','words[153]').replace('i<143','i<153').replace('result.c3_cleanup_mask){','result.c3_cleanup_mask || result.c5b_cleanup_mask){').replace('result.code==0x75612)','result.code==0x75612 || result.code==0x75614)');assert 'frequency!=3375000' in s;p.write_text(s,newline='\n')
p=k/'physical.py';s=p.read_text().replace('CR03 checkpoint after','second CR05 bit7 checkpoint after').replace('CR02 and CR03 bytes with','CR02 and CR03 bytes, then second CR05 bit7 write with');p.write_text(s,newline='\n')
p=k/'audit_collection.py';s=p.read_text().replace('crtc_blank_end_control','crtc_blank_bit_control').replace('len(v)==143','len(v)==153').replace('0x75612]','0x75612,0x75614]');p.write_text(s,newline='\n')
(k/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent754':{n:hashlib.sha256((o/n).read_bytes()).hexdigest() for n in names},'delta':'second CR05 bit7 RMW after CR03, distinct intermediate restoration then full-byte restoration,153 words; clock3375000 unchanged'},indent=2)+'\n',newline='\n')
