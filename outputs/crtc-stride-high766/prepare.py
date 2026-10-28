"""Source-only 766: next CR19 pitch high bits; CR13 remains read-only."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-reenable764'
def ns(s):return re.sub(r'(?<![0-9])764(?![0-9])','766',re.sub(r'0x764(?=[0-9a-f]*\b)','0x766',s))
names=['main.c','layout.c','layout.h','probe.c','probe.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','audit_collection.py','clock_model.py']
assert not (K/'main.c').exists()
for n in names:(K/n).write_text(ns((O/n).read_text()),newline='\n')
fields=['c19b_before','c19b_target','c19b_attempted','c19b_after','c19b_restored','c19b_cleanup_mask','c13_before_c19b','c13_after_c19b','c17_after_c19b','c0_after_c19b','c1_after_c19b','c2_after_c19b','c3_after_c19b','c4_after_c19b','c5_after_c19b','c13_restored_c19b']
p=K/'probe.h';p.write_text(p.read_text().replace('\n};','\n uint32_t '+','.join(fields)+';\n};'),newline='\n')
p=K/'probe.c';s=p.read_text()
s=s.replace(' for(unsigned i=0;i<7;++i)o->h_checked',' o->c19b_after=o->c19b_restored=o->c13_after_c19b=o->c17_after_c19b=o->c0_after_c19b=o->c1_after_c19b=o->c2_after_c19b=o->c3_after_c19b=o->c4_after_c19b=o->c5_after_c19b=o->c13_restored_c19b=0xffffffff;\n for(unsigned i=0;i<7;++i)o->h_checked')
block=''' /* Next original stride high bits: pixelDepth is four bytes, m=360. */
 o->forward_status=0x7661e;o->c19b_before=cr(0x19);o->c13_before_c19b=cr(0x13);
 if(o->c19b_before!=o->crtc_checked[2] || o->c13_before_c19b!=0x80)goto restore;
 o->c19b_target=(o->c19b_before&0x1f)|((((720u/8u)*4u)>>3)&0xe0);
 o->c19b_attempted=1;cw(0x19,(uint8_t)o->c19b_target);
 o->c19b_after=cr(0x19);o->c13_after_c19b=cr(0x13);o->c17_after_c19b=cr(0x17);
 o->c0_after_c19b=cr(0);o->c1_after_c19b=cr(1);o->c2_after_c19b=cr(2);o->c3_after_c19b=cr(3);o->c4_after_c19b=cr(4);o->c5_after_c19b=cr(5);
 if(o->c19b_after!=o->c19b_target || o->c13_after_c19b!=o->c13_before_c19b || o->c17_after_c19b!=o->c17b_target || o->c0_after_c19b!=o->c0_target || o->c1_after_c19b!=o->c1_target || o->c2_after_c19b!=o->c2b_target || o->c3_after_c19b!=o->c3_target || o->c4_after_c19b!=93 || o->c5_after_c19b!=o->c5b_target)goto restore;
'''
s=s.replace(' o->forward_status=0x766;\nrestore:',block+' o->forward_status=0x766;\nrestore:')
s=s.replace(' if(o->c17b_attempted){',' if(o->c19b_attempted){cw(0x19,(uint8_t)o->c19b_before);o->c19b_restored=cr(0x19);o->c13_restored_c19b=cr(0x13);if(o->c19b_restored!=o->c19b_before)o->c19b_cleanup_mask|=1;if(o->c13_restored_c19b!=o->c13_before_c19b)o->c19b_cleanup_mask|=2;}\n if(o->c17b_attempted){')
s=s.replace(' && !o->c17b_cleanup_mask){',' && !o->c17b_cleanup_mask && !o->c19b_cleanup_mask){')
s=s.replace(' if(o->forward_status!=0x7661 && !o->selectors_restored)',' if(o->c19b_cleanup_mask)o->code=0x7661f;\n if(o->forward_status!=0x7661 && !o->selectors_restored)')
p.write_text(s,newline='\n')
p=K/'main.c';s=p.read_text().replace('crtc_reenable_control','crtc_stride_high_control').replace('words[200]','words[216]').replace('i<200','i<216').replace('result.c17b_cleanup_mask){','result.c17b_cleanup_mask || result.c19b_cleanup_mask){').replace('result.code==0x7661c)','result.code==0x7661c || result.code==0x7661e)');p.write_text(s,newline='\n')
p=K/'audit_collection.py';s=p.read_text().replace('crtc_reenable_control','crtc_stride_high_control').replace('len(v)==200','len(v)==216').replace('0x7661c]','0x7661c,0x7661e]');p.write_text(s,newline='\n')
p=K/'physical.py';s=p.read_text().replace('CR17 bit7 forward enable checkpoint','CR19 upper-stride checkpoint').replace('then CR17 bit7 forward enable with own','then CR17 bit7 forward enable then CR19 upper stride bits with own');p.write_text(s,newline='\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent764':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'delta':'CR19 fresh capture guarded by prior10, upper stride target30, CR13 read-only80 guard and forward/recovery preservation; seven other neighbors; newest-first own recovery10 then inherited51;216words864bytes. No CR13 write or later vertical/encoder/PLL work.'},indent=2)+'\n',newline='\n')
