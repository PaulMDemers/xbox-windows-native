"""Fresh802 source-only derivation; preserve long hexadecimal hardware constants."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vblank-bit800'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):
 constants=[]
 def save(m):constants.append(m[0]);return '@HEX'+str(len(constants)-1)+'@'
 s=re.sub(r'0x[0-9a-fA-F]{6,}',save,s)
 s=s.replace('800','802').replace('crtc-vblank-bit802','crtc-vblank-overflow802')
 return re.sub(r'@HEX(\d+)@',lambda m:constants[int(m[1])],s)
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','clock_model.py','physical.py','model.py']
(K/'.gitattributes').write_bytes(b'* -text\n');(K/'.gitignore').write_bytes(b'model[0-9][0-9][0-9].json\n__pycache__/\n')
for n in names:
 assert not (K/n).exists();(K/n).write_bytes(ns((O/n).read_text()).encode())
(K/'audit_collection.py').write_bytes(ns((O/'audit_collection002.py').read_text()).replace('dashboard003.json','dashboard002.json').encode())
fields=['cb7_before','cb7_target','cb7_attempted','cb7_after','cb7_restored','cb7_cleanup_mask']
neighbors=[('cb7_c6',6,12),('cb7_c9',9,64),('cb7_c10',16,233),('cb7_c12',18,223),('cb7_c15',21,207),('cb7_c16',22,140),('cb7_c18',24,255),('cb7_c25',37,16)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
block=' /* CRTC_VBLANKSTART bit3, pinned704 yres480 minus1. */\n o->forward_status=0x80240;o->cb7_before=cr(7);\n'
block+=' '+''.join('o->'+n+'_before=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->cb7_before!=0x36 || '+' || '.join('o->'+n+'_before!='+hex(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->cb7_target=(o->cb7_before&0xf7u)|(((480u-1u)>>5)&0x08u);o->cb7_attempted=1;cw(7,o->cb7_target);\n o->cb7_after=cr(7);'
block+=''.join('o->'+n+'_after=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->cb7_after!=o->cb7_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->cb7_attempted){cw(7,o->cb7_before);o->cb7_restored=cr(7);'+''.join('o->'+n+'_restored=cr('+hex(a)+');' for n,a,_ in neighbors)
undo+='if(o->cb7_restored!=o->cb7_before)o->cb7_cleanup_mask|=1;'+''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->cb7_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();a=' o->forward_status=0x802;\nrestore:';assert s.count(a)==1
s=s.replace(a,block+a).replace(' if(o->cb9_attempted){',undo+' if(o->cb9_attempted){').replace(' && !o->cb9_cleanup_mask){',' && !o->cb9_cleanup_mask && !o->cb7_cleanup_mask){').replace(' if(o->cb9_cleanup_mask)o->code=0x8023f;',' if(o->cb9_cleanup_mask)o->code=0x8023f;\n if(o->cb7_cleanup_mask)o->code=0x80241;')
pos=s.index(' o->cb9_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_bytes(s.encode())
p=K/'probe.h';p.write_bytes(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};').encode())
p=K/'main.c';s=p.read_text().replace('words[670]','words[700]').replace('i<670','i<700').replace('crtc_vblank_bit_control','crtc_vblank_overflow_control').replace('result.cb9_cleanup_mask){','result.cb9_cleanup_mask || result.cb7_cleanup_mask){').replace('result.code==0x8023e)','result.code==0x8023e || result.code==0x80240)');p.write_bytes(s.encode())
p=K/'Makefile';p.write_bytes(p.read_text().replace('CR09 VBLANK BIT','CR07 VBLANK OVERFLOW').encode())
p=K/'physical.py';s=p.read_text().replace('CR09 vertical-blank-start bit5 checkpoint','CR07 vertical-blank-start bit3 checkpoint').replace('then CR09 60 to40;','then CR09 60 to40 then CR07 36 to3E;').replace('own reverse recovery CR09 then CR12','own reverse recovery CR07 then CR09 then CR12');p.write_bytes(s.encode())
p=K/'audit_collection.py';s=p.read_text().replace('crtc_vblank_bit_control','crtc_vblank_overflow_control').replace('len(v)==670','len(v)==700').replace('0x8023e]','0x8023e,0x80240]');p.write_bytes(s.encode())
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent':'closed800 source; closed801 optical evidence','files':{n:sha(O/n) for n in names+['audit_collection002.py']},'hex_constants_preserved':True},indent=2)+'\n')
print('Prepared802 sources; no build or hardware access')
