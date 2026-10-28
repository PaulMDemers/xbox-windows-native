"""Source-only764 CR17 bit7 enable after qualified later CR02; no runtime reuse."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-repeat-blank762'
def ns(s):return re.sub(r'(?<![0-9])762(?![0-9])','764',re.sub(r'0x762(?=[0-9a-f]*\b)','0x764',s))
names=['main.c','layout.c','layout.h','probe.c','probe.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','audit_collection.py','clock_model.py']
assert not (K/'main.c').exists()
for n in names:(K/n).write_text(ns((O/n).read_text()),newline='\n')
fields=' uint32_t c17b_before,c17b_target,c17b_attempted,c17b_after,c17b_restored,c17b_cleanup_mask,c0_after_c17b,c1_after_c17b,c2_after_c17b,c3_after_c17b,c4_after_c17b,c5_after_c17b;\n'
p=K/'probe.h';p.write_text(p.read_text().replace('\n};','\n'+fields+'};'),newline='\n')
p=K/'probe.c';s=p.read_text()
s=s.replace(' for(unsigned i=0;i<7;++i)o->h_checked',' o->c17b_after=o->c17b_restored=o->c0_after_c17b=o->c1_after_c17b=o->c2_after_c17b=o->c3_after_c17b=o->c4_after_c17b=o->c5_after_c17b=0xffffffff;\n for(unsigned i=0;i<7;++i)o->h_checked')
block=''' /* Original next CR17 RMW: set bit7, fresh own value under outer blank. */
 o->forward_status=0x7641c;o->c17b_before=cr(0x17);
 if(o->c17b_before!=o->c17_after_c2b)goto restore;
 o->c17b_target=(o->c17b_before&0x7f)|0x80;o->c17b_attempted=1;cw(0x17,(uint8_t)o->c17b_target);
 o->c17b_after=cr(0x17);o->c0_after_c17b=cr(0);o->c1_after_c17b=cr(1);o->c2_after_c17b=cr(2);o->c3_after_c17b=cr(3);o->c4_after_c17b=cr(4);o->c5_after_c17b=cr(5);
 if(o->c17b_after!=o->c17b_target || o->c0_after_c17b!=o->c0_target || o->c1_after_c17b!=o->c1_target || o->c2_after_c17b!=o->c2b_target || o->c3_after_c17b!=o->c3_target || o->c4_after_c17b!=93 || o->c5_after_c17b!=o->c5b_target)goto restore;
'''
s=s.replace(' o->forward_status=0x764;\nrestore:',block+' o->forward_status=0x764;\nrestore:')
s=s.replace(' if(o->c2b_attempted){',' if(o->c17b_attempted){cw(0x17,(uint8_t)o->c17b_before);o->c17b_restored=cr(0x17);if(o->c17b_restored!=o->c17b_before)o->c17b_cleanup_mask=1;}\n if(o->c2b_attempted){')
s=s.replace(' && !o->c2b_cleanup_mask){',' && !o->c2b_cleanup_mask && !o->c17b_cleanup_mask){')
s=s.replace(' if(o->forward_status!=0x7641 && !o->selectors_restored)',' if(o->c17b_cleanup_mask)o->code=0x7641d;\n if(o->forward_status!=0x7641 && !o->selectors_restored)')
p.write_text(s,newline='\n')
p=K/'main.c';s=p.read_text().replace('crtc_repeat_blank_control','crtc_reenable_control').replace('words[188]','words[200]').replace('i<188','i<200').replace('result.c2b_cleanup_mask){','result.c2b_cleanup_mask || result.c17b_cleanup_mask){').replace('result.code==0x7641a)','result.code==0x7641a || result.code==0x7641c)');assert 'frequency!=3375000' in s;p.write_text(s,newline='\n')
p=K/'audit_collection.py';s=p.read_text().replace('crtc_repeat_blank_control','crtc_reenable_control').replace('len(v)==188','len(v)==200').replace('0x7641a]','0x7641a,0x7641c]');p.write_text(s,newline='\n')
p=K/'physical.py';s=p.read_text().replace('later CR02 repeated blank-start checkpoint','CR17 bit7 forward enable checkpoint').replace('then later CR02 repeated blank-start with own','then later CR02 repeated blank-start then CR17 bit7 forward enable with own');p.write_text(s,newline='\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent762':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'delta':'CR17 fresh capture guarded by previous63, bit7 OR targete3, six neighbors and newest-first own recovery63;200words800bytes. Outer sequencer/gate blank retained. No later operations. Native counterpart must expand initialized result extent beyond5400 with fresh validation.'},indent=2)+'\n',newline='\n')
