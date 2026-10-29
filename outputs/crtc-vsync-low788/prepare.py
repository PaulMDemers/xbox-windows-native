"""Source-only CR10 extension; never opens a closed runtime or accesses hardware."""
from pathlib import Path
import json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vsync-high786'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):return s.replace('786','788').replace('crtc-vsync-high788','crtc-vsync-low788')
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','clock_model.py','audit_collection.py']
for n in names:
 assert not (K/n).exists();(K/n).write_text(ns((O/n).read_text()),newline='\n')
(K/'.gitattributes').write_text('* -text\n')
fields=['c10_before','c10_target','c10_attempted','c10_after','c10_restored','c10_cleanup_mask']
neighbors=[('c10_c6',6,0xec),('c10_c7',7,0x74),('c10_c9',9,0x60),('c10_c12',0x12,0xcf),('c10_c15',0x15,0xcf),('c10_c16',0x16,0xed),('c10_c18',0x18,0xff),('c10_c25',0x25,0x10)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
block=' /* Second CRTC_VSYNCSTART operation: CR10 low byte, after qualified CR07 bits. */\n o->forward_status=0x78832;o->c10_before=cr(0x10);\n'
block+=' '+''.join('o->'+n+'_before=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->c10_before!=0xd4 || '+' || '.join('o->'+n+'_before!='+hex(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->c10_target=489u&0xffu;o->c10_attempted=1;cw(0x10,o->c10_target);\n o->c10_after=cr(0x10);'
block+=''.join('o->'+n+'_after=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->c10_after!=o->c10_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->c10_attempted){cw(0x10,o->c10_before);o->c10_restored=cr(0x10);'
undo+=''.join('o->'+n+'_restored=cr('+hex(a)+');' for n,a,_ in neighbors)
undo+='if(o->c10_restored!=o->c10_before)o->c10_cleanup_mask|=1;'
undo+=''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->c10_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();anchor=' o->forward_status=0x788;\nrestore:';assert s.count(anchor)==1
s=s.replace(anchor,block+anchor).replace(' if(o->c7_attempted){',undo+' if(o->c7_attempted){')
s=s.replace(' && !o->c7_cleanup_mask){',' && !o->c7_cleanup_mask && !o->c10_cleanup_mask){')
s=s.replace(' if(o->c7_cleanup_mask)o->code=0x78831;',' if(o->c7_cleanup_mask)o->code=0x78831;\n if(o->c10_cleanup_mask)o->code=0x78833;')
pos=s.index(' o->c7_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_text(s,newline='\n')
p=K/'probe.h';p.write_text(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};'),newline='\n')
p=K/'main.c';s=p.read_text().replace('words[460]','words[490]').replace('i<460','i<490').replace('crtc_vsync_high_control','crtc_vsync_low_control').replace('result.c7_cleanup_mask){','result.c7_cleanup_mask || result.c10_cleanup_mask){').replace('result.code==0x78830)','result.code==0x78830 || result.code==0x78832)');p.write_text(s,newline='\n')
p=K/'Makefile';p.write_text(p.read_text().replace('CR07 VSYNC HIGH','CR10 VSYNC LOW'),newline='\n')
p=K/'physical.py';s=p.read_text().replace('vertical display-end checkpoint','CR10 vertical-sync low-byte checkpoint').replace('no CR10 or later vertical,','then CR10 sync-start low byte D4 to E9 with own saved-value recovery before CR07 recovery, including CR07=74 neighbor check; no later vertical,').replace('kernel-context NVVDISPEND checkpoint after qualified horizontal prefix and CR04/CR05/CR00/CR02 with own saved-value recovery','kernel-context CR10 sync-start low byte D4 to E9 after qualified CR07=74; own reverse recovery CR10 then CR07');p.write_text(s,newline='\n')
p=K/'audit_collection.py';p.write_text(p.read_text().replace('crtc_vsync_high_control','crtc_vsync_low_control').replace('len(v)==460','len(v)==490').replace('0x78830]','0x78830,0x78832]'),newline='\n')
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent':'closed786 source only; closed787 native evidence retained','files':{n:sha(O/n) for n in names}},indent=2)+'\n')
print('Prepared788 source only; no hardware access')
