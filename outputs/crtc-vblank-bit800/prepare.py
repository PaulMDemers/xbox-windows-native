"""Fresh CR09 vertical-blank bit5 control; closed798 SOURCE only."""
from pathlib import Path
import json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vdisplay-low798'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):return s.replace('798','800').replace('crtc-vdisplay-low800','crtc-vblank-bit800')
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','clock_model.py']
(K/'.gitattributes').write_bytes(b'* -text\n');(K/'.gitignore').write_bytes(b'model*.json\n!model-public*.json\n__pycache__/\n')
for n in names:
 assert not (K/n).exists();(K/n).write_bytes(ns((O/n).read_text()).encode())
for src,dst in [('physical002.py','physical.py'),('audit_collection003.py','audit_collection.py'),('model002.py','model.py')]:
 assert not (K/dst).exists();(K/dst).write_bytes(ns((O/src).read_text()).replace('model002.json','model001.json').replace('physical002.py','physical.py').replace('audit002.json','audit001.json').encode())
fields=['cb9_before','cb9_target','cb9_attempted','cb9_after','cb9_restored','cb9_cleanup_mask']
neighbors=[('cb9_c6',6,12),('cb9_c7',7,54),('cb9_c10',16,233),('cb9_c12',18,223),('cb9_c15',21,207),('cb9_c16',22,140),('cb9_c18',24,255),('cb9_c25',37,16)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
block=' /* CRTC_VBLANKSTART bit5, pinned704 yres480 minus1. */\n o->forward_status=0x8003e;o->cb9_before=cr(9);\n'
block+=' '+''.join('o->'+n+'_before=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->cb9_before!=0x60 || '+' || '.join('o->'+n+'_before!='+hex(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->cb9_target=(o->cb9_before&0xdfu)|(((480u-1u)>>4)&0x20u);o->cb9_attempted=1;cw(9,o->cb9_target);\n o->cb9_after=cr(9);'
block+=''.join('o->'+n+'_after=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->cb9_after!=o->cb9_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->cb9_attempted){cw(9,o->cb9_before);o->cb9_restored=cr(9);'+''.join('o->'+n+'_restored=cr('+hex(a)+');' for n,a,_ in neighbors)
undo+='if(o->cb9_restored!=o->cb9_before)o->cb9_cleanup_mask|=1;'+''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->cb9_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();a=' o->forward_status=0x800;\nrestore:';assert s.count(a)==1
s=s.replace(a,block+a).replace(' if(o->cd12_attempted){',undo+' if(o->cd12_attempted){').replace(' && !o->cd12_cleanup_mask){',' && !o->cd12_cleanup_mask && !o->cb9_cleanup_mask){').replace(' if(o->cd12_cleanup_mask)o->code=0x8003d;',' if(o->cd12_cleanup_mask)o->code=0x8003d;\n if(o->cb9_cleanup_mask)o->code=0x8003f;')
pos=s.index(' o->cd12_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_bytes(s.encode())
p=K/'probe.h';p.write_bytes(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};').encode())
p=K/'main.c';s=p.read_text().replace('words[640]','words[670]').replace('i<640','i<670').replace('crtc_vdisplay_low_control','crtc_vblank_bit_control').replace('result.cd12_cleanup_mask){','result.cd12_cleanup_mask || result.cb9_cleanup_mask){').replace('result.code==0x8003c)','result.code==0x8003c || result.code==0x8003e)');p.write_bytes(s.encode())
p=K/'Makefile';p.write_bytes(p.read_text().replace('CR12 VDISPLAY LOW','CR09 VBLANK BIT').encode())
p=K/'physical.py';s=p.read_text().replace('CR12 display-end low-byte checkpoint','CR09 vertical-blank-start bit5 checkpoint').replace('then CR12 CF toDF; own reverse recovery CR12','then CR12 CF toDF then CR09 60 to40; own reverse recovery CR09 then CR12').replace('kernel-context CR12 display-end CF toDF after thirdCR07=36; own reverse recovery CR12','kernel-context CR09 blank-start60 to40 after CR12=DF; own reverse recovery CR09 then CR12');p.write_bytes(s.encode())
p=K/'audit_collection.py';s=p.read_text().replace('crtc_vdisplay_low_control','crtc_vblank_bit_control').replace('len(v)==640','len(v)==670').replace('0x8003c]','0x8003c,0x8003e]');p.write_bytes(s.encode())
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent':'closed798 source with corrected model/controller/auditor; closed799 native evidence retained','files':{n:sha(O/n) for n in names+['model002.py','physical002.py','audit_collection003.py']}},indent=2)+'\n')
print('Prepared800 sources; no build or hardware access')
