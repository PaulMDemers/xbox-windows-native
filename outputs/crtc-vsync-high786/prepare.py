"""Source-only extension of closed784. No runtime or console access."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;O=K.parent/'vertical-valid-end784'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):return s.replace('784','786').replace('vertical-valid-end786','crtc-vsync-high786')
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','clock_model.py']
for n in names:
 assert not (K/n).exists();(K/n).write_text(ns((O/n).read_text()),newline='\n')
(K/'audit_collection.py').write_text(ns((O/'audit_collection002.py').read_text()).replace('audit002.json','audit001.json').replace('dashboard002.json','dashboard001.json'),newline='\n')
(K/'.gitattributes').write_text('* -text\n')
fields=['c7_before','c7_target','c7_attempted','c7_after','c7_restored','c7_cleanup_mask']
neighbors=[('c7_c6',6,0xec),('c7_c9',9,0x60),('c7_c10',0x10,0xd4),('c7_c12',0x12,0xcf),('c7_c15',0x15,0xcf),('c7_c16',0x16,0xed),('c7_c18',0x18,0xff),('c7_c25',0x25,0x10)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
block=' /* First CRTC_VSYNCSTART operation: change only CR07 bits7/2; CR10 is untouched. */\n o->forward_status=0x78630;o->c7_before=cr(7);\n'
block+=' '+''.join('o->'+n+'_before=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->c7_before!=0xf0 || '+' || '.join('o->'+n+'_before!='+hex(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->c7_target=(o->c7_before&0x7bu)|((489u>>2)&0x80u)|((489u>>6)&4u);o->c7_attempted=1;cw(7,o->c7_target);\n o->c7_after=cr(7);'
block+=''.join('o->'+n+'_after=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->c7_after!=o->c7_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->c7_attempted){cw(7,o->c7_before);o->c7_restored=cr(7);'
undo+=''.join('o->'+n+'_restored=cr('+hex(a)+');' for n,a,_ in neighbors)
undo+='if(o->c7_restored!=o->c7_before)o->c7_cleanup_mask|=1;'
undo+=''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->c7_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();anchor=' o->forward_status=0x786;\nrestore:';assert s.count(anchor)==1
s=s.replace(anchor,block+anchor).replace(' if(o->ve_attempted){',undo+' if(o->ve_attempted){')
s=s.replace(' && !o->ve_cleanup_mask){',' && !o->ve_cleanup_mask && !o->c7_cleanup_mask){')
s=s.replace(' if(o->ve_cleanup_mask)o->code=0x7862f;',' if(o->ve_cleanup_mask)o->code=0x7862f;\n if(o->c7_cleanup_mask)o->code=0x78631;')
pos=s.index(' o->ve_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_text(s,newline='\n')
p=K/'probe.h';p.write_text(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};'),newline='\n')
p=K/'main.c';s=p.read_text().replace('words[430]','words[460]').replace('i<430','i<460').replace('vertical_valid_end_control','crtc_vsync_high_control').replace('result.ve_cleanup_mask){','result.ve_cleanup_mask || result.c7_cleanup_mask){').replace('result.code==0x7862e)','result.code==0x7862e || result.code==0x78630)');p.write_text(s,newline='\n')
p=K/'Makefile';p.write_text(p.read_text().replace('NVVVALIDEND','CR07 VSYNC HIGH'),newline='\n')
p=K/'physical.py';s=p.read_text().replace('no later vertical,','then CR07 sync overflow F0 to74 with own saved-value restoration and eight CRTC neighbor checks; no CR10 or later vertical,');p.write_text(s,newline='\n')
p=K/'audit_collection.py';p.write_text(p.read_text().replace('vertical_valid_end_control','crtc_vsync_high_control').replace('len(v)==430','len(v)==460').replace('0x7862e]','0x7862e,0x78630]'),newline='\n')
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent':'closed784 source only; closed785 native evidence retained','files':{n:sha(O/n) for n in names}},indent=2)+'\n')
print('Prepared786 source-only delta; no physical access')
