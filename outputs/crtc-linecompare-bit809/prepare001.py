"""Derive809 from CLOSED807 sources only. No physical or closed runtime access."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-linecompare-high807'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x807(?=[0-9a-f]{0,2}$)','0x809',p) if i%2 else p.replace('807','809') for i,p in enumerate(parts)).replace('crtc-vblank-low809','crtc-linecompare-bit809')
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','clock_model003.py','frontend_model002.py','physical.py','model005.py','controller_review003.py','audit_collection002.py','dashboard.py','restore_receipts001.py']
for n in names:
 assert not (K/n).exists();(K/n).write_bytes(ns((O/n).read_text()).encode())
fields=['cl9_before','cl9_target','cl9_attempted','cl9_after','cl9_restored','cl9_cleanup_mask']
neighbors=[('cl9_c6',6,12),('cl9_c7',7,62),('cl9_c10',16,233),('cl9_c12',18,223),('cl9_c15',21,223),('cl9_c16',22,140),('cl9_c18',24,255),('cl9_c25',37,16)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
block=' /* CRTC_LINECOMP bit6, pinned704 m=0x3ff; same-value at this baseline. */\n o->forward_status=0x80946;o->cl9_before=cr(9);\n'
block+=' '+''.join('o->'+n+'_before=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->cl9_before!=0x40 || '+' || '.join('o->'+n+'_before!='+hex(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->cl9_target=(o->cl9_before&0xbfu)|((0x3ffu>>3)&0x40u);o->cl9_attempted=1;cw(9,o->cl9_target);\n o->cl9_after=cr(9);'
block+=''.join('o->'+n+'_after=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->cl9_after!=o->cl9_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->cl9_attempted){cw(9,o->cl9_before);o->cl9_restored=cr(9);'+''.join('o->'+n+'_restored=cr('+hex(a)+');' for n,a,_ in neighbors)
undo+='if(o->cl9_restored!=o->cl9_before)o->cl9_cleanup_mask|=1;'+''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->cl9_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text();a=' o->forward_status=0x809;\nrestore:';assert s.count(a)==1
s=s.replace(a,block+a).replace(' if(o->cl7_attempted){',undo+' if(o->cl7_attempted){').replace(' && !o->cl7_cleanup_mask){',' && !o->cl7_cleanup_mask && !o->cl9_cleanup_mask){').replace(' if(o->cl7_cleanup_mask)o->code=0x80945;',' if(o->cl7_cleanup_mask)o->code=0x80945;\n if(o->cl9_cleanup_mask)o->code=0x80947;')
pos=s.index(' o->cl7_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_bytes(s.encode())
p=K/'probe.h';p.write_bytes(p.read_text().replace('};',' uint32_t '+','.join(fields)+';\n};').encode())
p=K/'main.c';s=p.read_text().replace('words[760]','words[790]').replace('i<760','i<790').replace('crtc_linecompare_high_control','crtc_linecompare_bit_control').replace('result.cl7_cleanup_mask){','result.cl7_cleanup_mask || result.cl9_cleanup_mask){').replace('result.code==0x80944)','result.code==0x80944 || result.code==0x80946)');p.write_bytes(s.encode())
p=K/'Makefile';p.write_bytes(p.read_text().replace('CR07 LINECOMPARE HIGH','CR09 LINECOMPARE BIT').encode())
p=K/'physical.py';s=p.read_text().replace('CR15 vertical-blank-start low-byte checkpoint','CR07 line-compare bit4 checkpoint').replace('then CR15 CF toDF;','then CR15 CF toDF then CR07 line-compare3E to3E; same-value write/drop indistinguishable;').replace('own reverse recovery CR15 then CR07','own reverse recovery line-compareCR07 then CR15 then CR07').replace('kernel-context CR15 blank-start low byte CF toDF after CR07=3E','kernel-context CR07 line-compare bit4 same-value3E after CR15=DF');p.write_bytes(s.encode())
p=K/'audit_collection002.py';s=p.read_text().replace('crtc_linecompare_high_control','crtc_linecompare_bit_control').replace('len(v)==760','len(v)==790').replace('0x80944]','0x80944,0x80946]').replace('dashboard004.json','dashboard002.json');p.write_bytes(s.encode())
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n')
(K/'lineage001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'parent':'CLOSED807 sources only','files':{n:sha(O/n) for n in names},'hex_constants_preserved':True},indent=2)+'\n')
print('Prepared809 sources; no build or hardware access')
