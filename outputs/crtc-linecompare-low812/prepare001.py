"""Prepare fresh812 from pinned810 source only; no closed runtime access."""
from pathlib import Path
import re,json,hashlib,datetime
K=Path(__file__).resolve().parent;O=K.parent/'crtc-linecompare-cold810'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
assert read(O/'closed001.json')['passed']
assert read(K.parent/'native-linecompare-bit811/closed001.json')['passed']
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x810(?=[0-9a-f]{0,2}$)','0x812',p) if i%2 else re.sub(r'\b810\b|(?<=[A-Za-z_])810\b','812',p) for i,p in enumerate(parts))
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py']
for n in names:
 assert sha(O/n)==read(O/'sources001.json')[n]
 assert not (K/n).exists();(K/n).write_bytes(ns((O/n).read_text(encoding='utf-8')).encode())
fields=['cl18_before','cl18_target','cl18_attempted','cl18_after','cl18_restored','cl18_cleanup_mask']
neighbors=[('cl18_c6',6,12),('cl18_c7',7,62),('cl18_c9',9,64),('cl18_c10',16,233),('cl18_c12',18,223),('cl18_c15',21,223),('cl18_c16',22,140),('cl18_c25',37,16)]
for n,_,_ in neighbors:fields += [n+'_before',n+'_after',n+'_restored']
init=' '+''.join('o->'+f+'=0xffffffff;' for f in fields if f.endswith(('_after','_restored')))+'\n'
block=' /* CRTC_LINECOMP low byte, pinned704 m=0x3ff; baseline already FF. */\n o->forward_status=0x81248;o->cl18_before=cr(0x18);\n'
block+=' '+''.join('o->'+n+'_before=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->cl18_before!=0xff || '+' || '.join('o->'+n+'_before!='+hex(v) for n,_,v in neighbors)+')goto restore;\n'
block+=' o->cl18_target=0x3ffu&0xffu;o->cl18_attempted=1;cw(0x18,o->cl18_target);\n o->cl18_after=cr(0x18);'
block+=''.join('o->'+n+'_after=cr('+hex(a)+');' for n,a,_ in neighbors)+'\n'
block+=' if(o->cl18_after!=o->cl18_target || '+' || '.join('o->'+n+'_after!=o->'+n+'_before' for n,_,_ in neighbors)+')goto restore;\n'
undo=' if(o->cl18_attempted){cw(0x18,o->cl18_before);o->cl18_restored=cr(0x18);'+''.join('o->'+n+'_restored=cr('+hex(a)+');' for n,a,_ in neighbors)
undo+='if(o->cl18_restored!=o->cl18_before)o->cl18_cleanup_mask|=1;'+''.join('if(o->'+n+'_restored!=o->'+n+'_before)o->cl18_cleanup_mask|='+str(2<<i)+';' for i,(n,_,_) in enumerate(neighbors))+'}\n'
p=K/'probe.c';s=p.read_text(encoding='utf-8');a=' o->forward_status=0x812;\nrestore:';assert s.count(a)==1
s=s.replace(a,block+a).replace(' if(o->cl9_attempted){',undo+' if(o->cl9_attempted){').replace(' && !o->cl9_cleanup_mask){',' && !o->cl9_cleanup_mask && !o->cl18_cleanup_mask){').replace(' if(o->cl9_cleanup_mask)o->code=0x81247;',' if(o->cl9_cleanup_mask)o->code=0x81247;\n if(o->cl18_cleanup_mask)o->code=0x81249;')
pos=s.index(' o->cl9_after=0xffffffff;');end=s.index('\n',pos)+1;s=s[:end]+init+s[end:];p.write_bytes(s.encode())
p=K/'probe.h';p.write_bytes(p.read_text(encoding='utf-8').replace('};',' uint32_t '+','.join(fields)+';\n};').encode())
p=K/'main.c';s=p.read_text(encoding='utf-8').replace('words[790]','words[820]').replace('i<790','i<820').replace('crtc_linecompare_bit_control','crtc_linecompare_low_control').replace('result.cl9_cleanup_mask){','result.cl9_cleanup_mask || result.cl18_cleanup_mask){').replace('result.code==0x81246)','result.code==0x81246 || result.code==0x81248)');p.write_bytes(s.encode())
p=K/'Makefile';p.write_bytes(p.read_text(encoding='utf-8').replace('CR09 LINECOMPARE BIT','CR18 LINECOMPARE LOW').encode())
(K/'delta001.json').write_text(json.dumps(dict(fields=fields,init=init,block=block,undo=undo,neighbors=neighbors),indent=2)+'\n',encoding='utf-8')
(K/'lineage001.json').write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_only=True,closed_runtime_reused=False,parent='CLOSED810 sources only; native811 closed qualification gate',files={n:sha(O/n) for n in names},stage_authorized=False,launch_authorized=False),indent=2)+'\n',encoding='utf-8')
print('Prepared812 source only; no hardware controller or stage admission')
