"""Fresh source-only extension of closed788. No runtime or hardware access."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vsync-low788'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):return s.replace('788','790').replace('crtc-vsync-low790','crtc-vtotal-high790')
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','clock_model.py']
for n in names:
 assert not (K/n).exists();(K/n).write_text(ns((O/n).read_text()),newline='\n')
(K/'.gitattributes').write_text('* -text\n')
(K/'.gitignore').write_text('model001.json\n__pycache__/\n')
fields=['ct7_before','ct7_target','ct7_attempted','ct7_after','ct7_restored','ct7_cleanup_mask']
neighbors=[('ct7_c6',6,0xec),('ct7_c9',9,0x60),('ct7_c10',0x10,0xe9),('ct7_c12',0x12,0xcf),('ct7_c15',0x15,0xcf),('ct7_c16',0x16,0xed),('ct7_c18',0x18,0xff),('ct7_c25',0x25,0x10)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
block=' /* CRTC_VTOTAL overflow: second CR07 operation, after CR10. Same-value 74. */\n o->forward_status=0x79034;o->ct7_before=cr(7);\n'
block+=' '+''.join('o->'+n+'_before=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->ct7_before!=0x74 || '+' || '.join('o->'+n+'_before!='+hex(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->ct7_target=(o->ct7_before&0xdeu)|((524u>>4)&0x20u)|((524u>>8)&1u);o->ct7_attempted=1;cw(7,o->ct7_target);\n o->ct7_after=cr(7);'
block+=''.join('o->'+n+'_after=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->ct7_after!=o->ct7_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->ct7_attempted){cw(7,o->ct7_before);o->ct7_restored=cr(7);'
undo+=''.join('o->'+n+'_restored=cr('+hex(a)+');' for n,a,_ in neighbors)
undo+='if(o->ct7_restored!=o->ct7_before)o->ct7_cleanup_mask|=1;'
undo+=''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->ct7_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();anchor=' o->forward_status=0x790;\nrestore:';assert s.count(anchor)==1
s=s.replace(anchor,block+anchor).replace(' if(o->c10_attempted){',undo+' if(o->c10_attempted){')
s=s.replace(' && !o->c10_cleanup_mask){',' && !o->c10_cleanup_mask && !o->ct7_cleanup_mask){')
s=s.replace(' if(o->c10_cleanup_mask)o->code=0x79033;',' if(o->c10_cleanup_mask)o->code=0x79033;\n if(o->ct7_cleanup_mask)o->code=0x79035;')
pos=s.index(' o->c10_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_text(s,newline='\n')
p=K/'probe.h';p.write_text(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};'),newline='\n')
p=K/'main.c';s=p.read_text().replace('words[490]','words[520]').replace('i<490','i<520').replace('crtc_vsync_low_control','crtc_vtotal_high_control').replace('result.c10_cleanup_mask){','result.c10_cleanup_mask || result.ct7_cleanup_mask){').replace('result.code==0x79032)','result.code==0x79032 || result.code==0x79034)');p.write_text(s,newline='\n')
p=K/'Makefile';p.write_text(p.read_text().replace('CR10 VSYNC LOW','CR07 VTOTAL HIGH'),newline='\n')
p=K/'physical.py';s=p.read_text().replace('no later vertical,','then second CR07 vertical-total overflow 74 to74 with own reverse recovery before CR10; same-value write cannot prove a transition; no CR06/CR16 or later vertical,');p.write_text(s,newline='\n')
(K/'audit_collection.py').write_text(ns((O/'audit_collection002.py').read_text()).replace('audit002.json','audit001.json').replace('dashboard002.json','dashboard001.json').replace('crtc_vsync_low_control','crtc_vtotal_high_control').replace('len(v)==490','len(v)==520').replace('0x79032]','0x79032,0x79034]'),newline='\n')
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent':'closed788 source only; closed789 native evidence retained','files':{n:sha(O/n) for n in names}},indent=2)+'\n')
print('Prepared790 source only; no hardware access')
