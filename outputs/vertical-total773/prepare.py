"""Source-only successor to closed771; no old runtime access."""
from pathlib import Path
import hashlib,json,re
K=Path(__file__).resolve().parent;O=K.parent/'vertical-display-end771'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):return re.sub(r'(?<![0-9])771(?![0-9])','773',re.sub(r'0x771(?=[0-9a-f]*\b)','0x773',s)).replace('vertical-display-end771','vertical-total773')
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','clock_model.py','audit_logic.py','prefix_schema.py','physical.py','audit_collection.py']
for n in names:
 assert not (K/n).exists()
 (K/n).write_text(ns((O/n).read_text()),encoding='utf-8',newline='\n')
(K/'.gitattributes').write_text('* -text\n')
fields=['vt_before','vt_target','vt_attempted','vt_after','vt_restored','vt_cleanup_mask']
neighbors=[('vt_disp',0x680800,479),('vt_syncstart',0x68080c,724),('vt_syncend',0x680810,729),('vt_validend',0x680818,719),('vt_c13',0x13,104),('vt_c19',0x19,48)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
capture=lambda n,a:('cr('+hex(a)+')' if a<256 else 'R32('+hex(a)+')')
block=' /* Next pinned source-order word: vertical total only. */\n o->forward_status=0x77324;o->vt_before=R32(0x680804);\n'
block+=' '+''.join('o->'+n+'_before='+capture(n,a)+';' for n,a,_ in neighbors)+'\n'
block+=' if(o->vt_before!=749 || '+' || '.join('o->'+n+'_before!='+str(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->vt_target=524u;o->vt_attempted=1;R32(0x680804)=o->vt_target;\n o->vt_after=R32(0x680804);'
block+=''.join('o->'+n+'_after='+capture(n,a)+';' for n,a,_ in neighbors)+'\n'
block+=' if(o->vt_after!=o->vt_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->vt_attempted){R32(0x680804)=o->vt_before;o->vt_restored=R32(0x680804);'
undo+=''.join('o->'+n+'_restored='+capture(n,a)+';' for n,a,_ in neighbors)
undo+='if(o->vt_restored!=o->vt_before)o->vt_cleanup_mask|=1;'
undo+=''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->vt_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();anchor=' o->forward_status=0x773;\nrestore:';assert s.count(anchor)==1
s=s.replace(anchor,block+anchor).replace(' if(o->v_attempted){',undo+' if(o->v_attempted){')
s=s.replace(' && !o->v_cleanup_mask){',' && !o->v_cleanup_mask && !o->vt_cleanup_mask){')
s=s.replace(' if(o->v_cleanup_mask)o->code=0x77323;',' if(o->v_cleanup_mask)o->code=0x77323;\n if(o->vt_cleanup_mask)o->code=0x77325;')
pos=s.index(' o->v_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_text(s,newline='\n')
p=K/'probe.h';p.write_text(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};'),newline='\n')
p=K/'main.c';s=p.read_text().replace('words[256]','words[280]').replace('i<256','i<280').replace('vertical_display_end_control','vertical_total_control').replace('result.v_cleanup_mask){','result.v_cleanup_mask || result.vt_cleanup_mask){').replace('result.code==0x77322)','result.code==0x77322 || result.code==0x77324)');p.write_text(s,newline='\n')
p=K/'Makefile';p.write_text(p.read_text().replace('NVVDISPEND','NVVTOTAL'),newline='\n')
for n in ['physical.py','audit_collection.py']:
 p=K/n;s=p.read_text().replace('review004.json','review001.json').replace('vertical_display_end_control','vertical_total_control').replace('len(v)==256','len(v)==280').replace('0x77322]','0x77322,0x77324]').replace('horizontal_prefix_one_vertical_word_diagnostic','horizontal_prefix_two_vertical_words_diagnostic').replace('no other vertical,','then NVVTOTAL 749 to 524 with own recovery and six-neighbor checks; no other vertical,');p.write_text(s,newline='\n')
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'parent':'closed771 source; no runtime reuse','files':{n:sha(O/n) for n in names}},indent=2)+'\n')
print('Prepared773 source-only delta; no hardware access')
