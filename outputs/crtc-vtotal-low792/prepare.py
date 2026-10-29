"""Source-only CR06 extension of CLOSED790; never reuse a closed runtime."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vtotal-high790'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):return s.replace('790','792').replace('crtc-vtotal-high792','crtc-vtotal-low792')
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','clock_model.py','audit_collection.py']
for n in names:
 assert not (K/n).exists();(K/n).write_text(ns((O/n).read_text()),newline='\n')
(K/'.gitattributes').write_text('* -text\n')
(K/'.gitignore').write_text('model001.json\n__pycache__/\n')
fields=['ct6_before','ct6_target','ct6_attempted','ct6_after','ct6_restored','ct6_cleanup_mask']
neighbors=[('ct6_c7',7,0x74),('ct6_c9',9,0x60),('ct6_c10',0x10,0xe9),('ct6_c12',0x12,0xcf),('ct6_c15',0x15,0xcf),('ct6_c16',0x16,0xed),('ct6_c18',0x18,0xff),('ct6_c25',0x25,0x10)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
block=' /* CRTC_VTOTAL low byte after the second CR07 operation. */\n o->forward_status=0x79236;o->ct6_before=cr(6);\n'
block+=' '+''.join('o->'+n+'_before=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->ct6_before!=0xec || '+' || '.join('o->'+n+'_before!='+hex(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->ct6_target=(524u&0xffu);o->ct6_attempted=1;cw(6,o->ct6_target);\n o->ct6_after=cr(6);'
block+=''.join('o->'+n+'_after=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->ct6_after!=o->ct6_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->ct6_attempted){cw(6,o->ct6_before);o->ct6_restored=cr(6);'
undo+=''.join('o->'+n+'_restored=cr('+hex(a)+');' for n,a,_ in neighbors)
undo+='if(o->ct6_restored!=o->ct6_before)o->ct6_cleanup_mask|=1;'
undo+=''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->ct6_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();anchor=' o->forward_status=0x792;\nrestore:';assert s.count(anchor)==1
s=s.replace(anchor,block+anchor).replace(' if(o->ct7_attempted){',undo+' if(o->ct7_attempted){')
s=s.replace(' && !o->ct7_cleanup_mask){',' && !o->ct7_cleanup_mask && !o->ct6_cleanup_mask){')
s=s.replace(' if(o->ct7_cleanup_mask)o->code=0x79235;',' if(o->ct7_cleanup_mask)o->code=0x79235;\n if(o->ct6_cleanup_mask)o->code=0x79237;')
pos=s.index(' o->ct7_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_text(s,newline='\n')
p=K/'probe.h';p.write_text(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};'),newline='\n')
p=K/'main.c';s=p.read_text().replace('words[520]','words[550]').replace('i<520','i<550').replace('crtc_vtotal_high_control','crtc_vtotal_low_control').replace('result.ct7_cleanup_mask){','result.ct7_cleanup_mask || result.ct6_cleanup_mask){').replace('result.code==0x79234)','result.code==0x79234 || result.code==0x79236)');p.write_text(s,newline='\n')
p=K/'Makefile';p.write_text(p.read_text().replace('CR07 VTOTAL HIGH','CR06 VTOTAL LOW'),newline='\n')
p=K/'physical.py';s=p.read_text().replace('Kernel-context792 CR10 vertical-sync low-byte checkpoint','Kernel-context792 CR06 vertical-total low-byte checkpoint').replace('no CR06/CR16 or later vertical,','then CR06 vertical-total low byte EC to0C with own saved-value reverse recovery before second CR07; no CR16 or later vertical,').replace('kernel-context CR10 sync-start low byte D4 to E9 after qualified CR07=74; own reverse recovery CR10 then CR07','kernel-context CR06 total low byte EC to0C after second CR07=74; own reverse recovery CR06 then second CR07, CR10 and earlier CR07');p.write_text(s,newline='\n')
p=K/'audit_collection.py';p.write_text(p.read_text().replace('crtc_vtotal_high_control','crtc_vtotal_low_control').replace('len(v)==520','len(v)==550').replace('0x79234]','0x79234,0x79236]'),newline='\n')
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent':'closed790 source only; closed791 native evidence retained','files':{n:sha(O/n) for n in names}},indent=2)+'\n')
print('Prepared792 source only; no hardware access')
