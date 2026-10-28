"""Fresh762 later CR02 write, source-only760; no closed runtime reuse."""
from pathlib import Path
import re,json,hashlib
k=Path(__file__).resolve().parent;o=k.parent/'crtc-display-end760'
def ns(s):return re.sub(r'(?<![0-9])760(?![0-9])','762',re.sub(r'0x760(?=[0-9a-f]*\b)','0x762',s))
names=['main.c','layout.c','layout.h','probe.c','probe.h','Makefile','build.py','model002.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','audit_collection.py','clock_model.py']
assert not (k/'main.c').exists()
for n in names:(k/('model.py' if n=='model002.py' else n)).write_text(ns((o/n).read_text()).replace("'model002.json'","'model001.json'"),newline='\n')
fields=' uint32_t c2b_before,c2b_target,c2b_attempted,c2b_after,c2b_restored,c2b_cleanup_mask,c0_after_c2b,c1_after_c2b,c3_after_c2b,c4_after_c2b,c5_after_c2b,c17_after_c2b;\n'
p=k/'probe.h';p.write_text(p.read_text().replace('\n};','\n'+fields+'};'),newline='\n')
p=k/'probe.c';s=p.read_text()
s=s.replace(' for(unsigned i=0;i<7;++i)o->h_checked',' o->c2b_after=o->c2b_restored=o->c0_after_c2b=o->c1_after_c2b=o->c3_after_c2b=o->c4_after_c2b=o->c5_after_c2b=o->c17_after_c2b=0xffffffff;\n for(unsigned i=0;i<7;++i)o->h_checked')
block=''' /* Original later CR02 write: same target, distinct source-ordered access. */
 o->forward_status=0x7621a;o->c2b_before=cr(2);
 if(o->c2b_before!=o->c2_after_c1)goto restore;
 o->c2b_target=(720u/8u)-1u;o->c2b_attempted=1;cw(2,(uint8_t)o->c2b_target);
 o->c2b_after=cr(2);o->c0_after_c2b=cr(0);o->c1_after_c2b=cr(1);o->c3_after_c2b=cr(3);o->c4_after_c2b=cr(4);o->c5_after_c2b=cr(5);o->c17_after_c2b=cr(0x17);
 if(o->c2b_after!=o->c2b_target || o->c0_after_c2b!=o->c0_target || o->c1_after_c2b!=o->c1_target || o->c3_after_c2b!=o->c3_target || o->c4_after_c2b!=93 || o->c5_after_c2b!=o->c5b_target || o->c17_after_c2b!=o->c17_target)goto restore;
'''
s=s.replace(' o->forward_status=0x762;\nrestore:',block+' o->forward_status=0x762;\nrestore:')
s=s.replace(' if(o->c1_attempted){',' if(o->c2b_attempted){cw(2,(uint8_t)o->c2b_before);o->c2b_restored=cr(2);if(o->c2b_restored!=o->c2b_before)o->c2b_cleanup_mask=1;}\n if(o->c1_attempted){')
s=s.replace(' && !o->c1_cleanup_mask){',' && !o->c1_cleanup_mask && !o->c2b_cleanup_mask){')
s=s.replace(' if(o->forward_status!=0x7621 && !o->selectors_restored)',' if(o->c2b_cleanup_mask)o->code=0x7621b;\n if(o->forward_status!=0x7621 && !o->selectors_restored)')
p.write_text(s,newline='\n')
p=k/'main.c';s=p.read_text().replace('crtc_display_end_control','crtc_repeat_blank_control').replace('words[176]','words[188]').replace('i<176','i<188').replace('result.c1_cleanup_mask){','result.c1_cleanup_mask || result.c2b_cleanup_mask){').replace('result.code==0x76218)','result.code==0x76218 || result.code==0x7621a)');assert 'frequency!=3375000' in s;p.write_text(s,newline='\n')
p=k/'audit_collection.py';s=p.read_text().replace('crtc_display_end_control','crtc_repeat_blank_control').replace('len(v)==176','len(v)==188').replace('0x76218]','0x76218,0x7621a]');p.write_text(s,newline='\n')
p=k/'physical.py';s=p.read_text().replace('CR01 display-end checkpoint','later CR02 repeated blank-start checkpoint').replace('CR01 display-end with own','CR01 display-end then later CR02 repeated blank-start with own');p.write_text(s,newline='\n')
(k/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent760':{n:hashlib.sha256((o/n).read_bytes()).hexdigest() for n in names},'delta':'Later CR02 fresh capture/guard, target59, six neighbors, newest-first own recovery;188words752bytes. Same-value writes and undos can be dropped without readback distinction. CR17 enable excluded.'},indent=2)+'\n',newline='\n')
