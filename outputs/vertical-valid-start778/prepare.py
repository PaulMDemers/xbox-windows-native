"""Source-only778 extension: same-value NVVVALIDSTART after closed776/777."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'vertical-crtc776'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):return re.sub(r'(?<![0-9])776(?![0-9])','778',re.sub(r'0x776(?=[0-9a-f]*\b)','0x778',s)).replace('vertical-crtc776','vertical-valid-start778')
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','clock_model.py','audit_logic.py','prefix_schema.py','physical.py','audit_collection.py']
for n in names:
 assert not (K/n).exists();(K/n).write_text(ns((O/n).read_text()),newline='\n')
(K/'.gitattributes').write_text('* -text\n')
fields=['vs_before','vs_target','vs_attempted','vs_after','vs_restored','vs_cleanup_mask']
neighbors=[('vs_disp',0x680800,479),('vs_total',0x680804,524),('vs_crtc',0x680808,479),('vs_syncstart',0x68080c,724),('vs_syncend',0x680810,729),('vs_validend',0x680818,719),('vs_c13',0x13,104),('vs_c19',0x19,48)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
capture=lambda a:('cr('+hex(a)+')' if a<256 else 'R32('+hex(a)+')')
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
block=' /* Next pinned source-order word: NVVVALIDSTART same-value zero write. */\n o->forward_status=0x77828;o->vs_before=R32(0x680814);\n'
block+=' '+''.join('o->'+n+'_before='+capture(a)+';' for n,a,_ in neighbors)+'\n'
block+=' if(o->vs_before!=0 || '+' || '.join('o->'+n+'_before!='+str(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->vs_target=0u;o->vs_attempted=1;R32(0x680814)=o->vs_target;\n o->vs_after=R32(0x680814);'
block+=''.join('o->'+n+'_after='+capture(a)+';' for n,a,_ in neighbors)+'\n'
block+=' if(o->vs_after!=o->vs_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->vs_attempted){R32(0x680814)=o->vs_before;o->vs_restored=R32(0x680814);'
undo+=''.join('o->'+n+'_restored='+capture(a)+';' for n,a,_ in neighbors)
undo+='if(o->vs_restored!=o->vs_before)o->vs_cleanup_mask|=1;'
undo+=''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->vs_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();anchor=' o->forward_status=0x778;\nrestore:';assert s.count(anchor)==1
s=s.replace(anchor,block+anchor).replace(' if(o->vc_attempted){',undo+' if(o->vc_attempted){')
s=s.replace(' && !o->vc_cleanup_mask){',' && !o->vc_cleanup_mask && !o->vs_cleanup_mask){')
s=s.replace(' if(o->vc_cleanup_mask)o->code=0x77827;',' if(o->vc_cleanup_mask)o->code=0x77827;\n if(o->vs_cleanup_mask)o->code=0x77829;')
pos=s.index(' o->vc_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_text(s,newline='\n')
p=K/'probe.h';p.write_text(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};'),newline='\n')
p=K/'main.c';s=p.read_text().replace('words[310]','words[340]').replace('i<310','i<340').replace('vertical_crtc_control','vertical_valid_start_control').replace('result.vc_cleanup_mask){','result.vc_cleanup_mask || result.vs_cleanup_mask){').replace('result.code==0x77826)','result.code==0x77826 || result.code==0x77828)');p.write_text(s,newline='\n')
p=K/'Makefile';p.write_text(p.read_text().replace('NVVCRTC','NVVVALIDSTART'),newline='\n')
for n in ['physical.py','audit_collection.py']:
 p=K/n;s=p.read_text().replace('vertical_crtc_control','vertical_valid_start_control').replace('three_vertical_words','four_vertical_words').replace('len(v)==310','len(v)==340').replace('0x77826]','0x77826,0x77828]')
 s=s.replace('no other vertical,','then NVVVALIDSTART0 to0 with own recovery and eight-neighbor checks (dropped same-value writes indistinguishable); no later vertical,')
 p.write_text(s,newline='\n')
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent':'closed776 sources; closed777 native evidence retained','files':{n:sha(O/n) for n in names}},indent=2)+'\n')
print('Prepared778 source-only delta; no physical access')
