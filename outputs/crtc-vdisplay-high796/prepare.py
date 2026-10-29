"""Fresh CR07 display-end overflow control; source-only closed794 derivation."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vblank-end794'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):return s.replace('794','796').replace('crtc-vblank-end796','crtc-vdisplay-high796')
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','clock_model.py']
for n in names:
 assert not (K/n).exists();(K/n).write_bytes(ns((O/n).read_text()).encode())
(K/'audit_collection.py').write_bytes(ns((O/'audit_collection002.py').read_text()).replace('audit002.json','audit001.json').replace('dashboard002.json','dashboard001.json').encode())
(K/'.gitattributes').write_bytes(b'* -text\n');(K/'.gitignore').write_bytes(b'model001.json\n__pycache__/\n')
fields=['cd7_before','cd7_target','cd7_attempted','cd7_after','cd7_restored','cd7_cleanup_mask']
neighbors=[('cd7_c6',6,12),('cd7_c9',9,96),('cd7_c10',16,233),('cd7_c12',18,207),('cd7_c15',21,207),('cd7_c16',22,140),('cd7_c18',24,255),('cd7_c25',37,16)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
block=' /* CRTC_VDISPEND overflow bits: yres480 minus1, preserve unrelated CR07 bits. */\n o->forward_status=0x7963a;o->cd7_before=cr(7);\n'
block+=' '+''.join('o->'+n+'_before=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->cd7_before!=0x74 || '+' || '.join('o->'+n+'_before!='+hex(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->cd7_target=(o->cd7_before&0xbdu)|(((480u-1u)>>3)&0x40u)|(((480u-1u)>>7)&0x02u);o->cd7_attempted=1;cw(7,o->cd7_target);\n o->cd7_after=cr(7);'
block+=''.join('o->'+n+'_after=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->cd7_after!=o->cd7_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->cd7_attempted){cw(7,o->cd7_before);o->cd7_restored=cr(7);'+''.join('o->'+n+'_restored=cr('+hex(a)+');' for n,a,_ in neighbors)
undo+='if(o->cd7_restored!=o->cd7_before)o->cd7_cleanup_mask|=1;'+''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->cd7_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();a=' o->forward_status=0x796;\nrestore:';assert s.count(a)==1
s=s.replace(a,block+a).replace(' if(o->ct16_attempted){',undo+' if(o->ct16_attempted){').replace(' && !o->ct16_cleanup_mask){',' && !o->ct16_cleanup_mask && !o->cd7_cleanup_mask){').replace(' if(o->ct16_cleanup_mask)o->code=0x79639;',' if(o->ct16_cleanup_mask)o->code=0x79639;\n if(o->cd7_cleanup_mask)o->code=0x7963b;')
pos=s.index(' o->ct16_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_bytes(s.encode())
p=K/'probe.h';p.write_bytes(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};').encode())
p=K/'main.c';s=p.read_text().replace('words[580]','words[610]').replace('i<580','i<610').replace('crtc_vblank_end_control','crtc_vdisplay_high_control').replace('result.ct16_cleanup_mask){','result.ct16_cleanup_mask || result.cd7_cleanup_mask){').replace('result.code==0x79638)','result.code==0x79638 || result.code==0x7963a)');p.write_bytes(s.encode())
p=K/'Makefile';p.write_bytes(p.read_text().replace('CR16 VBLANK END','CR07 VDISPLAY HIGH').encode())
p=K/'physical.py';s=p.read_text().replace('CR16 vertical-blank-end checkpoint','CR07 display-end overflow checkpoint').replace('then CR16 blank-end ED to8C preserving bit7, own reverse recovery before CR06; no later vertical,','then CR16 blank-end ED to8C, then CR07 display-end74 to36; own reverse recovery CR07 then CR16 then CR06; no later vertical,').replace('kernel-context CR16 blank-end ED to8C after CR06=0C; own reverse recovery CR16 then CR06, second CR07, CR10 and earlier CR07','kernel-context CR07 display-end overflow74 to36 after CR16=8C; own reverse recovery thirdCR07 then CR16, CR06, secondCR07, CR10 and earlierCR07');p.write_bytes(s.encode())
p=K/'audit_collection.py';p.write_bytes(p.read_text().replace('crtc_vblank_end_control','crtc_vdisplay_high_control').replace('len(v)==580','len(v)==610').replace('0x79638]','0x79638,0x7963a]').encode())
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent':'closed794 sources; native795 closed evidence retained','files':{n:sha(O/n) for n in names}},indent=2)+'\n')
print('Prepared796 sources; no build or hardware access')
