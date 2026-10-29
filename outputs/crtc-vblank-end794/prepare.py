"""Fresh kernel CR16 extension from closed792 sources only; no hardware access."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vtotal-low792'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):return s.replace('792','794').replace('crtc-vtotal-low794','crtc-vblank-end794')
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','clock_model.py','audit_collection.py']
for n in names:
 assert not (K/n).exists();(K/n).write_text(ns((O/n).read_text()),newline='\n')
(K/'.gitignore').write_text('model001.json\n__pycache__/\n')
fields=['ct16_before','ct16_target','ct16_attempted','ct16_after','ct16_restored','ct16_cleanup_mask']
neighbors=[('ct16_c6',6,12),('ct16_c7',7,0x74),('ct16_c9',9,0x60),('ct16_c10',0x10,0xe9),('ct16_c12',0x12,0xcf),('ct16_c15',0x15,0xcf),('ct16_c18',0x18,0xff),('ct16_c25',0x25,0x10)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
block=' /* CRTC_VBLANKEND: preserve bit7 and replace low seven bits from total524. */\n o->forward_status=0x79438;o->ct16_before=cr(0x16);\n'
block+=' '+''.join('o->'+n+'_before=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->ct16_before!=0xed || '+' || '.join('o->'+n+'_before!='+hex(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->ct16_target=(o->ct16_before&0x80u)|(524u&0x7fu);o->ct16_attempted=1;cw(0x16,o->ct16_target);\n o->ct16_after=cr(0x16);'
block+=''.join('o->'+n+'_after=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->ct16_after!=o->ct16_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->ct16_attempted){cw(0x16,o->ct16_before);o->ct16_restored=cr(0x16);'
undo+=''.join('o->'+n+'_restored=cr('+hex(a)+');' for n,a,_ in neighbors)
undo+='if(o->ct16_restored!=o->ct16_before)o->ct16_cleanup_mask|=1;'
undo+=''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->ct16_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();anchor=' o->forward_status=0x794;\nrestore:';assert s.count(anchor)==1
s=s.replace(anchor,block+anchor).replace(' if(o->ct6_attempted){',undo+' if(o->ct6_attempted){')
s=s.replace(' && !o->ct6_cleanup_mask){',' && !o->ct6_cleanup_mask && !o->ct16_cleanup_mask){')
s=s.replace(' if(o->ct6_cleanup_mask)o->code=0x79437;',' if(o->ct6_cleanup_mask)o->code=0x79437;\n if(o->ct16_cleanup_mask)o->code=0x79439;')
pos=s.index(' o->ct6_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_text(s,newline='\n')
p=K/'probe.h';p.write_text(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};'),newline='\n')
p=K/'main.c';s=p.read_text().replace('words[550]','words[580]').replace('i<550','i<580').replace('crtc_vtotal_low_control','crtc_vblank_end_control').replace('result.ct6_cleanup_mask){','result.ct6_cleanup_mask || result.ct16_cleanup_mask){').replace('result.code==0x79436)','result.code==0x79436 || result.code==0x79438)');p.write_text(s,newline='\n')
p=K/'Makefile';p.write_text(p.read_text().replace('CR06 VTOTAL LOW','CR16 VBLANK END'),newline='\n')
p=K/'physical.py';s=p.read_text().replace('CR06 vertical-total low-byte checkpoint','CR16 vertical-blank-end checkpoint').replace('no CR16 or later vertical,','then CR16 blank-end ED to8C preserving bit7, own reverse recovery before CR06; no later vertical,').replace('kernel-context CR06 total low byte EC to0C after second CR07=74; own reverse recovery CR06 then second CR07, CR10 and earlier CR07','kernel-context CR16 blank-end ED to8C after CR06=0C; own reverse recovery CR16 then CR06, second CR07, CR10 and earlier CR07');p.write_text(s,newline='\n')
p=K/'audit_collection.py';p.write_text(p.read_text().replace('crtc_vtotal_low_control','crtc_vblank_end_control').replace('len(v)==550','len(v)==580').replace('0x79436]','0x79436,0x79438]'),newline='\n')
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent':'closed792 sources only; closed793 native evidence retained','files':{n:sha(O/n) for n in names}},indent=2)+'\n')
print('Prepared794 sources; no hardware access')
