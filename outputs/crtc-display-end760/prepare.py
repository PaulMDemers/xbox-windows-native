"""Fresh760 source-only CR01 control; no closed runtime reused."""
from pathlib import Path
import re,json,hashlib
k=Path(__file__).resolve().parent;o=k.parent/'crtc-display-gate758'
def ns(s):return re.sub(r'(?<![0-9])758(?![0-9])','760',re.sub(r'0x758(?=[0-9a-f]*\b)','0x760',s))
names=['main.c','layout.c','layout.h','probe.c','probe.h','Makefile','build.py','model002.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','audit_collection.py','clock_model.py']
assert not (k/'main.c').exists()
for n in names:(k/('model.py' if n=='model002.py' else n)).write_text(ns((o/n).read_text()),newline='\n')
p=k/'probe.h';s=p.read_text().replace('\n};','\n uint32_t c1_before,c1_target,c1_attempted,c1_after,c1_restored,c1_cleanup_mask,c0_after_c1,c2_after_c1,c3_after_c1,c4_after_c1,c5_after_c1,c17_after_c1;\n};');p.write_text(s,newline='\n')
p=k/'probe.c';s=p.read_text()
s=s.replace(' for(unsigned i=0;i<7;++i)o->h_checked',' o->c1_after=o->c1_restored=o->c0_after_c1=o->c2_after_c1=o->c3_after_c1=o->c4_after_c1=o->c5_after_c1=o->c17_after_c1=0xffffffff;\n for(unsigned i=0;i<7;++i)o->h_checked')
block=''' /* Original next CR01 display-end byte, fresh own value for recovery. */
 o->forward_status=0x76018;o->c1_before=cr(1);o->c1_target=(720u/8u)-1u;
 o->c1_attempted=1;cw(1,(uint8_t)o->c1_target);
 o->c1_after=cr(1);o->c0_after_c1=cr(0);o->c2_after_c1=cr(2);o->c3_after_c1=cr(3);o->c4_after_c1=cr(4);o->c5_after_c1=cr(5);o->c17_after_c1=cr(0x17);
 if(o->c1_after!=o->c1_target || o->c0_after_c1!=o->c0_target || o->c2_after_c1!=o->c2_target || o->c3_after_c1!=o->c3_target || o->c4_after_c1!=93 || o->c5_after_c1!=o->c5b_target || o->c17_after_c1!=o->c17_target)goto restore;
'''
s=s.replace(' o->forward_status=0x760;\nrestore:',block+' o->forward_status=0x760;\nrestore:')
s=s.replace(' if(o->c17_attempted){',' if(o->c1_attempted){cw(1,(uint8_t)o->c1_before);o->c1_restored=cr(1);if(o->c1_restored!=o->c1_before)o->c1_cleanup_mask=1;}\n if(o->c17_attempted){')
s=s.replace(' && !o->c17_cleanup_mask){',' && !o->c17_cleanup_mask && !o->c1_cleanup_mask){')
s=s.replace(' if(o->forward_status!=0x7601 && !o->selectors_restored)',' if(o->c1_cleanup_mask)o->code=0x76019;\n if(o->forward_status!=0x7601 && !o->selectors_restored)')
p.write_text(s,newline='\n')
p=k/'main.c';s=p.read_text().replace('crtc_display_gate_control','crtc_display_end_control').replace('words[164]','words[176]').replace('i<164','i<176').replace('result.c17_cleanup_mask){','result.c17_cleanup_mask || result.c1_cleanup_mask){').replace('result.code==0x76016)','result.code==0x76016 || result.code==0x76018)');assert 'frequency!=3375000' in s;p.write_text(s,newline='\n')
p=k/'audit_collection.py';s=p.read_text().replace('crtc_display_gate_control','crtc_display_end_control').replace('len(v)==164','len(v)==176').replace('0x76016]','0x76016,0x76018]');p.write_text(s,newline='\n')
p=k/'physical.py';s=p.read_text().replace('CR17 bit7 clear checkpoint','CR01 display-end checkpoint').replace('CR17 bit7 clear with own','CR17 bit7 clear then CR01 display-end with own');p.write_text(s,newline='\n')
(k/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent758':{n:hashlib.sha256((o/n).read_bytes()).hexdigest() for n in names},'delta':'Fresh CR01 capture, target59, six neighbor checks, newest-first own-byte recovery;176words704bytes. CR17 enable and later CR02 operation excluded.'},indent=2)+'\n',newline='\n')
