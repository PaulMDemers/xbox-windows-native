"""Fresh CR12 display-end low-byte control, source-only closed796 derivation."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vdisplay-high796'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):return s.replace('796','798').replace('crtc-vdisplay-high798','crtc-vdisplay-low798')
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','clock_model.py','audit_collection.py']
for n in names:
 assert not (K/n).exists();(K/n).write_bytes(ns((O/n).read_text()).encode())
(K/'model.py').write_bytes(ns((O/'model002.py').read_text()).replace('model002.json','model001.json').encode())
(K/'.gitattributes').write_bytes(b'* -text\n');(K/'.gitignore').write_bytes(b'model*.json\n!model-public*.json\n__pycache__/\n')
fields=['cd12_before','cd12_target','cd12_attempted','cd12_after','cd12_restored','cd12_cleanup_mask']
neighbors=[('cd12_c6',6,12),('cd12_c7',7,54),('cd12_c9',9,96),('cd12_c10',16,233),('cd12_c15',21,207),('cd12_c16',22,140),('cd12_c18',24,255),('cd12_c25',37,16)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
block=' /* CRTC_VDISPEND low byte, pinned704 yres480 minus1. */\n o->forward_status=0x7983c;o->cd12_before=cr(0x12);\n'
block+=' '+''.join('o->'+n+'_before=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->cd12_before!=0xcf || '+' || '.join('o->'+n+'_before!='+hex(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->cd12_target=(480u-1u)&0xffu;o->cd12_attempted=1;cw(0x12,o->cd12_target);\n o->cd12_after=cr(0x12);'
block+=''.join('o->'+n+'_after=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->cd12_after!=o->cd12_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->cd12_attempted){cw(0x12,o->cd12_before);o->cd12_restored=cr(0x12);'+''.join('o->'+n+'_restored=cr('+hex(a)+');' for n,a,_ in neighbors)
undo+='if(o->cd12_restored!=o->cd12_before)o->cd12_cleanup_mask|=1;'+''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->cd12_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();a=' o->forward_status=0x798;\nrestore:';assert s.count(a)==1
s=s.replace(a,block+a).replace(' if(o->cd7_attempted){',undo+' if(o->cd7_attempted){').replace(' && !o->cd7_cleanup_mask){',' && !o->cd7_cleanup_mask && !o->cd12_cleanup_mask){').replace(' if(o->cd7_cleanup_mask)o->code=0x7983b;',' if(o->cd7_cleanup_mask)o->code=0x7983b;\n if(o->cd12_cleanup_mask)o->code=0x7983d;')
pos=s.index(' o->cd7_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_bytes(s.encode())
p=K/'probe.h';p.write_bytes(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};').encode())
p=K/'main.c';s=p.read_text().replace('words[610]','words[640]').replace('i<610','i<640').replace('crtc_vdisplay_high_control','crtc_vdisplay_low_control').replace('result.cd7_cleanup_mask){','result.cd7_cleanup_mask || result.cd12_cleanup_mask){').replace('result.code==0x7983a)','result.code==0x7983a || result.code==0x7983c)');p.write_bytes(s.encode())
p=K/'Makefile';p.write_bytes(p.read_text().replace('CR07 VDISPLAY HIGH','CR12 VDISPLAY LOW').encode())
p=K/'physical.py';s=p.read_text().replace('model002.json','model001.json').replace('CR07 display-end overflow checkpoint','CR12 display-end low-byte checkpoint').replace('then CR07 display-end74 to36; own reverse recovery CR07 then CR16 then CR06','then CR07 display-end74 to36 then CR12 CF toDF; own reverse recovery CR12 then CR07 then CR16 then CR06').replace('kernel-context CR07 display-end overflow74 to36 after CR16=8C; own reverse recovery thirdCR07','kernel-context CR12 display-end CF toDF after thirdCR07=36; own reverse recovery CR12 then thirdCR07');p.write_bytes(s.encode())
p=K/'audit_collection.py';p.write_bytes(p.read_text().replace('crtc_vdisplay_high_control','crtc_vdisplay_low_control').replace('len(v)==610','len(v)==640').replace('0x7983a]','0x7983a,0x7983c]').encode())
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent':'closed796 sources and active model002; native797 closed evidence retained','files':{n:sha(O/n) for n in names+['model002.py']}},indent=2)+'\n')
print('Prepared798 sources; no build or hardware access')
