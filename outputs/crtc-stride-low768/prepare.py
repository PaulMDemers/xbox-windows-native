"""Source-only CR13 low stride extension from closed766; no runtime reuse."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-stride-high766'
def ns(s):return re.sub(r'(?<![0-9])766(?![0-9])','768',re.sub(r'0x766(?=[0-9a-f]*\b)','0x768',s))
names=['main.c','layout.c','layout.h','probe.c','probe.h','Makefile','build.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','audit_collection.py','clock_model.py']
assert not (K/'main.c').exists()
for n in names:(K/n).write_text(ns((O/n).read_text()),newline='\n')
(K/'model.py').write_text(ns((O/'model002.py').read_text()).replace('model002.json','model001.json'),newline='\n')
fields=['c13_before','c13_target','c13_attempted','c13_after','c13_restored','c13_cleanup_mask','c19_before_c13','c19_after_c13','c17_after_c13','c0_after_c13','c1_after_c13','c2_after_c13','c3_after_c13','c4_after_c13','c5_after_c13','c19_restored_c13']
p=K/'probe.h';p.write_text(p.read_text().replace('\n};','\n uint32_t '+','.join(fields)+';\n};'),newline='\n')
p=K/'probe.c';s=p.read_text()
init=' o->c13_after=o->c13_restored=o->c19_after_c13=o->c17_after_c13=o->c0_after_c13=o->c1_after_c13=o->c2_after_c13=o->c3_after_c13=o->c4_after_c13=o->c5_after_c13=o->c19_restored_c13=0xffffffff;\n'
s=s.replace(' for(unsigned i=0;i<7;++i)o->h_checked',init+' for(unsigned i=0;i<7;++i)o->h_checked')
block=''' /* Next original stride low byte: pixelDepth is four bytes, m=360. */
 o->forward_status=0x76820;o->c13_before=cr(0x13);o->c19_before_c13=cr(0x19);
 if(o->c13_before!=o->c13_after_c19b || o->c19_before_c13!=o->c19b_after)goto restore;
 o->c13_target=((720u/8u)*4u)&0xff;
 o->c13_attempted=1;cw(0x13,(uint8_t)o->c13_target);
 o->c13_after=cr(0x13);o->c19_after_c13=cr(0x19);o->c17_after_c13=cr(0x17);
 o->c0_after_c13=cr(0);o->c1_after_c13=cr(1);o->c2_after_c13=cr(2);o->c3_after_c13=cr(3);o->c4_after_c13=cr(4);o->c5_after_c13=cr(5);
 if(o->c13_after!=o->c13_target || o->c19_after_c13!=o->c19_before_c13 || o->c17_after_c13!=o->c17b_target || o->c0_after_c13!=o->c0_target || o->c1_after_c13!=o->c1_target || o->c2_after_c13!=o->c2b_target || o->c3_after_c13!=o->c3_target || o->c4_after_c13!=93 || o->c5_after_c13!=o->c5b_target)goto restore;
'''
s=s.replace(' o->forward_status=0x768;\nrestore:',block+' o->forward_status=0x768;\nrestore:')
undo=' if(o->c13_attempted){cw(0x13,(uint8_t)o->c13_before);o->c13_restored=cr(0x13);o->c19_restored_c13=cr(0x19);if(o->c13_restored!=o->c13_before)o->c13_cleanup_mask|=1;if(o->c19_restored_c13!=o->c19_before_c13)o->c13_cleanup_mask|=2;}\n'
s=s.replace(' if(o->c19b_attempted){',undo+' if(o->c19b_attempted){')
s=s.replace(' && !o->c19b_cleanup_mask){',' && !o->c19b_cleanup_mask && !o->c13_cleanup_mask){')
s=s.replace(' if(o->forward_status!=0x7681 && !o->selectors_restored)',' if(o->c13_cleanup_mask)o->code=0x76821;\n if(o->forward_status!=0x7681 && !o->selectors_restored)')
p.write_text(s,newline='\n')
p=K/'main.c';s=p.read_text().replace('crtc_stride_high_control','crtc_stride_low_control').replace('words[216]','words[232]').replace('i<216','i<232').replace('result.c19b_cleanup_mask){','result.c19b_cleanup_mask || result.c13_cleanup_mask){').replace('result.code==0x7681e)','result.code==0x7681e || result.code==0x76820)');p.write_text(s,newline='\n')
p=K/'audit_collection.py';s=p.read_text().replace('crtc_stride_high_control','crtc_stride_low_control').replace('len(v)==216','len(v)==232').replace('0x7681e]','0x7681e,0x76820]');p.write_text(s,newline='\n')
p=K/'physical.py';s=p.read_text().replace('model002.json','model001.json').replace('CR19 upper-stride checkpoint','CR13 low-stride checkpoint').replace('then CR19 upper stride bits with own','then CR19 upper stride bits then CR13 low stride byte with own');p.write_text(s,newline='\n')
(K/'delta001.json').write_text(json.dumps({'fields':fields,'init':init,'block':block,'undo':undo},indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent766':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names+['model002.py']},'delta':'CR13 fresh capture checked against previous read, target68, CR19 preservation plus seven neighbors, newest-first own80 recovery before CR19 own10/inherited51.232words928bytes.'},indent=2)+'\n')
