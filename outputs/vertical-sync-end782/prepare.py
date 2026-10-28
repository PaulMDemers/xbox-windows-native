"""Source-only extension of closed780; does not access a runtime or console."""
from pathlib import Path
import json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'vertical-sync-start780'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):return s.replace('780','782').replace('vertical-sync-start782','vertical-sync-end782')
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','audit_collection.py']
for n in names:
 assert not (K/n).exists();(K/n).write_text(ns((O/n).read_text()),newline='\n')
(K/'.gitattributes').write_text('* -text\n')
fields=['se_before','se_target','se_attempted','se_after','se_restored','se_cleanup_mask']
neighbors=[('se_disp',0x680800,479),('se_total',0x680804,524),('se_crtc',0x680808,479),('se_validstart',0x680814,0),('se_syncstart',0x68080c,489),('se_validend',0x680818,719),('se_c13',0x13,104),('se_c19',0x19,48)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
capture=lambda a:('cr('+hex(a)+')' if a<256 else 'R32('+hex(a)+')')
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
block=' /* Next pinned source-order word: NVVSYNCEND, nvvstart489+3=492. */\n o->forward_status=0x7822c;o->se_before=R32(0x680810);\n'
block+=' '+''.join('o->'+n+'_before='+capture(a)+';' for n,a,_ in neighbors)+'\n'
block+=' if(o->se_before!=729 || '+' || '.join('o->'+n+'_before!='+str(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->se_target=492u;o->se_attempted=1;R32(0x680810)=o->se_target;\n o->se_after=R32(0x680810);'
block+=''.join('o->'+n+'_after='+capture(a)+';' for n,a,_ in neighbors)+'\n'
block+=' if(o->se_after!=o->se_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->se_attempted){R32(0x680810)=o->se_before;o->se_restored=R32(0x680810);'
undo+=''.join('o->'+n+'_restored='+capture(a)+';' for n,a,_ in neighbors)
undo+='if(o->se_restored!=o->se_before)o->se_cleanup_mask|=1;'
undo+=''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->se_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();anchor=' o->forward_status=0x782;\nrestore:';assert s.count(anchor)==1
s=s.replace(anchor,block+anchor).replace(' if(o->sy_attempted){',undo+' if(o->sy_attempted){')
s=s.replace(' && !o->sy_cleanup_mask){',' && !o->sy_cleanup_mask && !o->se_cleanup_mask){')
s=s.replace(' if(o->sy_cleanup_mask)o->code=0x7822b;',' if(o->sy_cleanup_mask)o->code=0x7822b;\n if(o->se_cleanup_mask)o->code=0x7822d;')
pos=s.index(' o->sy_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_text(s,newline='\n')
p=K/'probe.h';p.write_text(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};'),newline='\n')
p=K/'main.c';s=p.read_text().replace('words[370]','words[400]').replace('i<370','i<400').replace('vertical_sync_start_control','vertical_sync_end_control').replace('result.sy_cleanup_mask){','result.sy_cleanup_mask || result.se_cleanup_mask){').replace('result.code==0x7822a)','result.code==0x7822a || result.code==0x7822c)');p.write_text(s,newline='\n')
p=K/'Makefile';p.write_text(p.read_text().replace('NVVSYNCSTART','NVVSYNCEND'),newline='\n')
p=K/'physical.py';s=p.read_text().replace('no later vertical,','then NVVSYNCEND729 to492 with own saved-value restoration and eight-neighbor checks; no later vertical,');p.write_text(s,newline='\n')
p=K/'audit_collection.py';p.write_text(p.read_text().replace('vertical_sync_start_control','vertical_sync_end_control').replace('len(v)==370','len(v)==400').replace('0x7822a]','0x7822a,0x7822c]').replace('five_vertical_words','six_vertical_words'),newline='\n')
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent':'closed780 source only; closed781 native evidence retained','files':{n:sha(O/n) for n in names}},indent=2)+'\n')
print('Prepared782 source-only delta; no physical access')
