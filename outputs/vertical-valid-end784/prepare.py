"""Source-only extension of closed782; does not access a runtime or console."""
from pathlib import Path
import json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'vertical-sync-end782'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):return s.replace('782','784').replace('vertical-sync-end784','vertical-valid-end784')
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','audit_collection.py']
for n in names:
 assert not (K/n).exists();(K/n).write_text(ns((O/n).read_text()),newline='\n')
(K/'.gitattributes').write_text('* -text\n')
fields=['ve_before','ve_target','ve_attempted','ve_after','ve_restored','ve_cleanup_mask']
neighbors=[('ve_disp',0x680800,479),('ve_total',0x680804,524),('ve_crtc',0x680808,479),('ve_validstart',0x680814,0),('ve_syncstart',0x68080c,489),('ve_syncend',0x680810,492),('ve_c13',0x13,104),('ve_c19',0x19,48)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
capture=lambda a:('cr('+hex(a)+')' if a<256 else 'R32('+hex(a)+')')
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
block=' /* Next pinned source-order word: NVVVALIDEND, yres480-1=479. */\n o->forward_status=0x7842e;o->ve_before=R32(0x680818);\n'
block+=' '+''.join('o->'+n+'_before='+capture(a)+';' for n,a,_ in neighbors)+'\n'
block+=' if(o->ve_before!=719 || '+' || '.join('o->'+n+'_before!='+str(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->ve_target=479u;o->ve_attempted=1;R32(0x680818)=o->ve_target;\n o->ve_after=R32(0x680818);'
block+=''.join('o->'+n+'_after='+capture(a)+';' for n,a,_ in neighbors)+'\n'
block+=' if(o->ve_after!=o->ve_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->ve_attempted){R32(0x680818)=o->ve_before;o->ve_restored=R32(0x680818);'
undo+=''.join('o->'+n+'_restored='+capture(a)+';' for n,a,_ in neighbors)
undo+='if(o->ve_restored!=o->ve_before)o->ve_cleanup_mask|=1;'
undo+=''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->ve_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();anchor=' o->forward_status=0x784;\nrestore:';assert s.count(anchor)==1
s=s.replace(anchor,block+anchor).replace(' if(o->se_attempted){',undo+' if(o->se_attempted){')
s=s.replace(' && !o->se_cleanup_mask){',' && !o->se_cleanup_mask && !o->ve_cleanup_mask){')
s=s.replace(' if(o->se_cleanup_mask)o->code=0x7842d;',' if(o->se_cleanup_mask)o->code=0x7842d;\n if(o->ve_cleanup_mask)o->code=0x7842f;')
pos=s.index(' o->se_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_text(s,newline='\n')
p=K/'probe.h';p.write_text(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};'),newline='\n')
p=K/'main.c';s=p.read_text().replace('words[400]','words[430]').replace('i<400','i<430').replace('vertical_sync_end_control','vertical_valid_end_control').replace('result.se_cleanup_mask){','result.se_cleanup_mask || result.ve_cleanup_mask){').replace('result.code==0x7842c)','result.code==0x7842c || result.code==0x7842e)');p.write_text(s,newline='\n')
p=K/'Makefile';p.write_text(p.read_text().replace('NVVSYNCEND','NVVVALIDEND'),newline='\n')
p=K/'physical.py';s=p.read_text().replace('no later vertical,','then NVVVALIDEND719 to479 with own saved-value restoration and eight-neighbor checks; no later vertical,');p.write_text(s,newline='\n')
p=K/'audit_collection.py';p.write_text(p.read_text().replace('vertical_sync_end_control','vertical_valid_end_control').replace('len(v)==400','len(v)==430').replace('0x7842c]','0x7842c,0x7842e]').replace('six_vertical_words','seven_vertical_words'),newline='\n')
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent':'closed782 source only; closed783 native evidence retained','files':{n:sha(O/n) for n in names}},indent=2)+'\n')
print('Prepared784 source-only delta; no physical access')
