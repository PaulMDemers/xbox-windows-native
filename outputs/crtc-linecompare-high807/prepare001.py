"""Derive807 from CLOSED805 sources only. No physical or closed runtime access."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-vblank-low805'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x805(?=[0-9a-f]{0,2}$)','0x807',p) if i%2 else p.replace('805','807') for i,p in enumerate(parts)).replace('crtc-vblank-low807','crtc-linecompare-high807')
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','clock_model003.py','frontend_model002.py','physical.py','model005.py','controller_review003.py','audit_collection002.py','dashboard.py','restore_receipts001.py']
for n in names:
 assert not (K/n).exists();(K/n).write_bytes(ns((O/n).read_text()).encode())
fields=['cl7_before','cl7_target','cl7_attempted','cl7_after','cl7_restored','cl7_cleanup_mask']
neighbors=[('cl7_c6',6,12),('cl7_c9',9,64),('cl7_c10',16,233),('cl7_c12',18,223),('cl7_c15',21,223),('cl7_c16',22,140),('cl7_c18',24,255),('cl7_c25',37,16)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
block=' /* CRTC_LINECOMP high bit, pinned704 m=0x3ff; same-value at this baseline. */\n o->forward_status=0x80744;o->cl7_before=cr(7);\n'
block+=' '+''.join('o->'+n+'_before=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->cl7_before!=0x3e || '+' || '.join('o->'+n+'_before!='+hex(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->cl7_target=(o->cl7_before&0xefu)|((0x3ffu>>4)&0x10u);o->cl7_attempted=1;cw(7,o->cl7_target);\n o->cl7_after=cr(7);'
block+=''.join('o->'+n+'_after=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->cl7_after!=o->cl7_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->cl7_attempted){cw(7,o->cl7_before);o->cl7_restored=cr(7);'+''.join('o->'+n+'_restored=cr('+hex(a)+');' for n,a,_ in neighbors)
undo+='if(o->cl7_restored!=o->cl7_before)o->cl7_cleanup_mask|=1;'+''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->cl7_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();a=' o->forward_status=0x807;\nrestore:';assert s.count(a)==1
s=s.replace(a,block+a).replace(' if(o->cb15_attempted){',undo+' if(o->cb15_attempted){').replace(' && !o->cb15_cleanup_mask){',' && !o->cb15_cleanup_mask && !o->cl7_cleanup_mask){').replace(' if(o->cb15_cleanup_mask)o->code=0x80743;',' if(o->cb15_cleanup_mask)o->code=0x80743;\n if(o->cl7_cleanup_mask)o->code=0x80745;')
pos=s.index(' o->cb15_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_bytes(s.encode())
p=K/'probe.h';p.write_bytes(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};').encode())
p=K/'main.c';s=p.read_text().replace('words[730]','words[760]').replace('i<730','i<760').replace('crtc_vblank_low_control','crtc_linecompare_high_control').replace('result.cb15_cleanup_mask){','result.cb15_cleanup_mask || result.cl7_cleanup_mask){').replace('result.code==0x80742)','result.code==0x80742 || result.code==0x80744)');p.write_bytes(s.encode())
p=K/'Makefile';p.write_bytes(p.read_text().replace('CR15 VBLANK LOW','CR07 LINECOMPARE HIGH').encode())
p=K/'physical.py';s=p.read_text().replace('CR15 vertical-blank-start low-byte checkpoint','CR07 line-compare bit4 checkpoint').replace('then CR15 CF toDF;','then CR15 CF toDF then CR07 line-compare3E to3E; same-value write/drop indistinguishable;').replace('own reverse recovery CR15 then CR07','own reverse recovery line-compareCR07 then CR15 then CR07').replace('kernel-context CR15 blank-start low byte CF toDF after CR07=3E','kernel-context CR07 line-compare bit4 same-value3E after CR15=DF');p.write_bytes(s.encode())
p=K/'audit_collection002.py';s=p.read_text().replace('crtc_vblank_low_control','crtc_linecompare_high_control').replace('len(v)==730','len(v)==760').replace('0x80742]','0x80742,0x80744]').replace('dashboard004.json','dashboard002.json');p.write_bytes(s.encode())
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent':'CLOSED805 sources only','files':{n:sha(O/n) for n in names},'hex_constants_preserved':True},indent=2)+'\n')
print('Prepared807 sources; no build or hardware access')
