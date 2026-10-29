"""Fresh805 source-only extension of CLOSED803; preserve hardware literals."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vblank-overflow803'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x803(?=[0-9a-f]{0,2}$)','0x805',p) if i%2 else p.replace('803','805') for i,p in enumerate(parts)).replace('crtc-vblank-overflow805','crtc-vblank-low805')
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','clock_model002.py','frontend_model002.py','physical.py','model003.py','controller_review002.py','audit_collection002.py','dashboard.py','restore_receipts001.py']
(K/'.gitattributes').write_bytes(b'* -text\n');(K/'.gitignore').write_bytes(b'model[0-9][0-9][0-9].json\n__pycache__/\n')
for n in names:
 data=ns((O/n).read_text()).encode()
 if (K/n).exists():assert (K/n).read_bytes()==data
 else:(K/n).write_bytes(data)
# Keep parent's active output names, but in a completely fresh805 namespace.
p=K/'build.py';p.write_bytes(p.read_text().replace('build001','build002').encode())
fields=['cb15_before','cb15_target','cb15_attempted','cb15_after','cb15_restored','cb15_cleanup_mask']
neighbors=[('cb15_c6',6,12),('cb15_c7',7,62),('cb15_c9',9,64),('cb15_c10',16,233),('cb15_c12',18,223),('cb15_c16',22,140),('cb15_c18',24,255),('cb15_c25',37,16)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
block=' /* CRTC_VBLANKSTART low byte, pinned704 yres480 minus1. */\n o->forward_status=0x80542;o->cb15_before=cr(0x15);\n'
block+=' '+''.join('o->'+n+'_before=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->cb15_before!=0xcf || '+' || '.join('o->'+n+'_before!='+hex(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->cb15_target=(480u-1u)&0xffu;o->cb15_attempted=1;cw(0x15,o->cb15_target);\n o->cb15_after=cr(0x15);'
block+=''.join('o->'+n+'_after=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->cb15_after!=o->cb15_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->cb15_attempted){cw(0x15,o->cb15_before);o->cb15_restored=cr(0x15);'+''.join('o->'+n+'_restored=cr('+hex(a)+');' for n,a,_ in neighbors)
undo+='if(o->cb15_restored!=o->cb15_before)o->cb15_cleanup_mask|=1;'+''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->cb15_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();a=' o->forward_status=0x805;\nrestore:';assert s.count(a)==1
s=s.replace(a,block+a).replace(' if(o->cb7_attempted){',undo+' if(o->cb7_attempted){').replace(' && !o->cb7_cleanup_mask){',' && !o->cb7_cleanup_mask && !o->cb15_cleanup_mask){').replace(' if(o->cb7_cleanup_mask)o->code=0x80541;',' if(o->cb7_cleanup_mask)o->code=0x80541;\n if(o->cb15_cleanup_mask)o->code=0x80543;')
pos=s.index(' o->cb7_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_bytes(s.encode())
p=K/'probe.h';p.write_bytes(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};').encode())
p=K/'main.c';s=p.read_text().replace('words[700]','words[730]').replace('i<700','i<730').replace('crtc_vblank_overflow_control','crtc_vblank_low_control').replace('result.cb7_cleanup_mask){','result.cb7_cleanup_mask || result.cb15_cleanup_mask){').replace('result.code==0x80540)','result.code==0x80540 || result.code==0x80542)');p.write_bytes(s.encode())
p=K/'Makefile';p.write_bytes(p.read_text().replace('CR07 VBLANK OVERFLOW','CR15 VBLANK LOW').encode())
p=K/'physical.py';s=p.read_text().replace('CR07 vertical-blank-start bit3 checkpoint','CR15 vertical-blank-start low-byte checkpoint').replace('then CR07 36 to3E;','then CR07 36 to3E then CR15 CF toDF;').replace('own reverse recovery CR07 then CR09','own reverse recovery CR15 then CR07 then CR09').replace('kernel-context CR07 blank-start overflow36 to3E after CR09=40','kernel-context CR15 blank-start low byte CF toDF after CR07=3E');p.write_bytes(s.encode())
p=K/'audit_collection002.py';s=p.read_text().replace('crtc_vblank_overflow_control','crtc_vblank_low_control').replace('len(v)==700','len(v)==730').replace('0x80540]','0x80540,0x80542]').replace('dashboard004.json','dashboard002.json');p.write_bytes(s.encode())
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent':'CLOSED803 corrected sources only','files':{n:sha(O/n) for n in names},'hex_constants_preserved':True},indent=2)+'\n')
print('Prepared805 sources; no build or hardware access')
