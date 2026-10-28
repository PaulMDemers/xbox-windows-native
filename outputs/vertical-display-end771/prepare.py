"""Source-only successor to closed769; never uses or launches its runtime."""
from pathlib import Path
import hashlib,json,re
K=Path(__file__).resolve().parent;O=K.parent/'crtc-stride-cold769'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):return re.sub(r'(?<![0-9])769(?![0-9])','771',re.sub(r'0x769(?=[0-9a-f]*\b)','0x771',s)).replace('crtc-stride-cold769','vertical-display-end771')
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','clock_model.py','audit_logic.py','prefix_schema.py','physical.py','audit_collection.py']
for n in names:
 assert not (K/n).exists()
 (K/n).write_text(ns((O/n).read_text()),encoding='utf-8',newline='\n')
(K/'.gitattributes').write_text('* -text\n')
fields=['v_before','v_target','v_attempted','v_after','v_restored','v_cleanup_mask']
neighbors=[('vtotal',0x680804,749),('vsyncstart',0x68080c,724),('vsyncend',0x680810,729),('vvalidend',0x680818,719),('c13_v',0x13,104),('c19_v',0x19,48)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
capture=lambda n,a:('cr('+hex(a)+')' if n.startswith('c') else 'R32('+hex(a)+')')
block=' /* Next pinned source-order word: vertical display end only. */\n o->forward_status=0x77122;o->v_before=R32(0x680800);\n'
block+=' '+''.join('o->'+n+'_before='+capture(n,a)+';' for n,a,_ in neighbors)+'\n'
block+=' if(o->v_before!=719 || '+' || '.join('o->'+n+'_before!='+str(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->v_target=480u-1u;o->v_attempted=1;R32(0x680800)=o->v_target;\n o->v_after=R32(0x680800);'
block+=''.join('o->'+n+'_after='+capture(n,a)+';' for n,a,_ in neighbors)+'\n'
block+=' if(o->v_after!=o->v_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->v_attempted){R32(0x680800)=o->v_before;o->v_restored=R32(0x680800);'
undo+=''.join('o->'+n+'_restored='+capture(n,a)+';' for n,a,_ in neighbors)
undo+='if(o->v_restored!=o->v_before)o->v_cleanup_mask|=1;'
undo+=''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->v_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();anchor=' o->forward_status=0x771;\nrestore:';assert s.count(anchor)==1
s=s.replace(anchor,block+anchor).replace(' if(o->c13_attempted){',undo+' if(o->c13_attempted){')
s=s.replace(' && !o->c13_cleanup_mask){',' && !o->c13_cleanup_mask && !o->v_cleanup_mask){')
s=s.replace(' if(o->c13_cleanup_mask)o->code=0x77121;',' if(o->c13_cleanup_mask)o->code=0x77121;\n if(o->v_cleanup_mask)o->code=0x77123;')
# Insert sentinel initialization immediately after prior result initialization.
anchor=' o->c13_after=';pos=s.index(anchor);end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_text(s,newline='\n')
p=K/'probe.h';p.write_text(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};'),newline='\n')
p=K/'main.c';s=p.read_text().replace('words[232]','words[256]').replace('i<232','i<256').replace('crtc_stride_low_control','vertical_display_end_control').replace('result.c13_cleanup_mask){','result.c13_cleanup_mask || result.v_cleanup_mask){').replace('result.code==0x77120)','result.code==0x77120 || result.code==0x77122)');p.write_text(s,newline='\n')
p=K/'Makefile';p.write_text(p.read_text().replace('CR03','NVVDISPEND'),newline='\n')
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'parent':'closed769 source; no runtime reuse','files':{n:sha(O/n) for n in names},'next_plan':sha(K.parent/'native-crtc-stridelow770/next-source-plan001.json')},indent=2)+'\n')
print('Prepared771 source-only delta; not built or staged')
