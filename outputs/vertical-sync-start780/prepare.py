"""Source-only extension of closed778; no runtime or hardware access."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'vertical-valid-start778'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):return s.replace('778','780').replace('vertical-valid-start780','vertical-sync-start780')
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','clock_model.py','audit_logic.py','prefix_schema.py','physical.py']
for n in names:
 assert not (K/n).exists();(K/n).write_text(ns((O/n).read_text()),newline='\n')
(K/'.gitattributes').write_text('* -text\n')
fields=['sy_before','sy_target','sy_attempted','sy_after','sy_restored','sy_cleanup_mask']
neighbors=[('sy_disp',0x680800,479),('sy_total',0x680804,524),('sy_crtc',0x680808,479),('sy_validstart',0x680814,0),('sy_syncend',0x680810,729),('sy_validend',0x680818,719),('sy_c13',0x13,104),('sy_c19',0x19,48)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
capture=lambda a:('cr('+hex(a)+')' if a<256 else 'R32('+hex(a)+')')
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
block=' /* Next pinned source-order word: NVVSYNCSTART, target489 from GPU_PARAMETER. */\n o->forward_status=0x7802a;o->sy_before=R32(0x68080c);\n'
block+=' '+''.join('o->'+n+'_before='+capture(a)+';' for n,a,_ in neighbors)+'\n'
block+=' if(o->sy_before!=724 || '+' || '.join('o->'+n+'_before!='+str(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->sy_target=489u;o->sy_attempted=1;R32(0x68080c)=o->sy_target;\n o->sy_after=R32(0x68080c);'
block+=''.join('o->'+n+'_after='+capture(a)+';' for n,a,_ in neighbors)+'\n'
block+=' if(o->sy_after!=o->sy_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->sy_attempted){R32(0x68080c)=o->sy_before;o->sy_restored=R32(0x68080c);'
undo+=''.join('o->'+n+'_restored='+capture(a)+';' for n,a,_ in neighbors)
undo+='if(o->sy_restored!=o->sy_before)o->sy_cleanup_mask|=1;'
undo+=''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->sy_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();anchor=' o->forward_status=0x780;\nrestore:';assert s.count(anchor)==1
s=s.replace(anchor,block+anchor).replace(' if(o->vs_attempted){',undo+' if(o->vs_attempted){')
s=s.replace(' && !o->vs_cleanup_mask){',' && !o->vs_cleanup_mask && !o->sy_cleanup_mask){')
s=s.replace(' if(o->vs_cleanup_mask)o->code=0x78029;',' if(o->vs_cleanup_mask)o->code=0x78029;\n if(o->sy_cleanup_mask)o->code=0x7802b;')
pos=s.index(' o->vs_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_text(s,newline='\n')
p=K/'probe.h';p.write_text(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};'),newline='\n')
p=K/'main.c';s=p.read_text().replace('words[340]','words[370]').replace('i<340','i<370').replace('vertical_valid_start_control','vertical_sync_start_control').replace('result.vs_cleanup_mask){','result.vs_cleanup_mask || result.sy_cleanup_mask){').replace('result.code==0x78028)','result.code==0x78028 || result.code==0x7802a)');p.write_text(s,newline='\n')
p=K/'Makefile';p.write_text(p.read_text().replace('NVVVALIDSTART','NVVSYNCSTART'),newline='\n')
p=K/'physical.py';s=p.read_text().replace('no later vertical,','then NVVSYNCSTART724 to489 with own saved-value restoration and eight-neighbor checks; no later vertical,');p.write_text(s,newline='\n')
(K/'audit_collection.py').write_text(ns((O/'audit_collection002.py').read_text()).replace('audit002.json','audit001.json').replace('dashboard002.json','dashboard001.json').replace('vertical_valid_start_control','vertical_sync_start_control').replace('len(v)==340','len(v)==370').replace('0x78028]','0x78028,0x7802a]').replace('four_vertical_words','five_vertical_words'),newline='\n')
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent':'closed778 source only; closed779 native evidence retained','files':{n:sha(O/n) for n in names},'audit_source_sha256':sha(O/'audit_collection002.py')},indent=2)+'\n')
print('Prepared780 source-only delta; no physical access')
