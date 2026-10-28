"""Source-only extension of closed773, admitted by physical readonly775."""
from pathlib import Path
import hashlib,json,re
K=Path(__file__).resolve().parent;O=K.parent/'vertical-total773'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):return re.sub(r'(?<![0-9])773(?![0-9])','776',re.sub(r'0x773(?=[0-9a-f]*\b)','0x776',s)).replace('vertical-total773','vertical-crtc776')
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','clock_model.py','audit_logic.py','prefix_schema.py','physical.py']
for n in names:
 assert not (K/n).exists()
 (K/n).write_text(ns((O/n).read_text()),encoding='utf-8',newline='\n')
(K/'.gitattributes').write_text('* -text\n')
fields=['vc_before','vc_target','vc_attempted','vc_after','vc_restored','vc_cleanup_mask']
neighbors=[('vc_disp',0x680800,479),('vc_total',0x680804,524),('vc_syncstart',0x68080c,724),('vc_syncend',0x680810,729),('vc_validstart',0x680814,0),('vc_validend',0x680818,719),('vc_c13',0x13,104),('vc_c19',0x19,48)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
capture=lambda a:('cr('+hex(a)+')' if a<256 else 'R32('+hex(a)+')')
block=' /* Next pinned source-order word: NVVCRTC only; readonly775 baseline. */\n o->forward_status=0x77626;o->vc_before=R32(0x680808);\n'
block+=' '+''.join('o->'+n+'_before='+capture(a)+';' for n,a,_ in neighbors)+'\n'
block+=' if(o->vc_before!=719 || '+' || '.join('o->'+n+'_before!='+str(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->vc_target=479u;o->vc_attempted=1;R32(0x680808)=o->vc_target;\n o->vc_after=R32(0x680808);'
block+=''.join('o->'+n+'_after='+capture(a)+';' for n,a,_ in neighbors)+'\n'
block+=' if(o->vc_after!=o->vc_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->vc_attempted){R32(0x680808)=o->vc_before;o->vc_restored=R32(0x680808);'
undo+=''.join('o->'+n+'_restored='+capture(a)+';' for n,a,_ in neighbors)
undo+='if(o->vc_restored!=o->vc_before)o->vc_cleanup_mask|=1;'
undo+=''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->vc_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();anchor=' o->forward_status=0x776;\nrestore:';assert s.count(anchor)==1
s=s.replace(anchor,block+anchor).replace(' if(o->vt_attempted){',undo+' if(o->vt_attempted){')
s=s.replace(' && !o->vt_cleanup_mask){',' && !o->vt_cleanup_mask && !o->vc_cleanup_mask){')
s=s.replace(' if(o->vt_cleanup_mask)o->code=0x77625;',' if(o->vt_cleanup_mask)o->code=0x77625;\n if(o->vc_cleanup_mask)o->code=0x77627;')
pos=s.index(' o->vt_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_text(s,newline='\n')
p=K/'probe.h';p.write_text(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};'),newline='\n')
p=K/'main.c';s=p.read_text().replace('words[280]','words[310]').replace('i<280','i<310').replace('vertical_total_control','vertical_crtc_control').replace('result.vt_cleanup_mask){','result.vt_cleanup_mask || result.vc_cleanup_mask){').replace('result.code==0x77624)','result.code==0x77624 || result.code==0x77626)');p.write_text(s,newline='\n')
p=K/'Makefile';p.write_text(p.read_text().replace('NVVTOTAL','NVVCRTC'),newline='\n')
p=K/'physical.py';p.write_text(p.read_text().replace('vertical_total_control','vertical_crtc_control').replace('two_vertical_words','three_vertical_words').replace('no other vertical,','then NVVCRTC719 to479 with recovery and eight-neighbor checks; no other vertical,'),newline='\n')
s=ns((O/'audit_collection002.py').read_text()).replace('dashboard002','dashboard001').replace('audit002','audit001').replace('vertical_total_control','vertical_crtc_control')
(K/'audit_collection.py').write_text(s,newline='\n')
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'parent':'closed773 sources; readonly775 measured baseline; no runtime reuse','files':{n:sha(O/n) for n in names},'auditor':sha(O/'audit_collection002.py')},indent=2)+'\n')
print('Prepared776 source-only delta; no hardware access')
