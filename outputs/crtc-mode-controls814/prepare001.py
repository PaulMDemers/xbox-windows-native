"""Source-only kernel bundle after CLOSED812/813; no physical access."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-linecompare-low812'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
assert read(O/'closed001.json')['passed'] and read(K.parent/'native-linecompare-low813/closed001.json')['passed']
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x812(?=[0-9a-f]{0,2}$)','0x814',p) if i%2 else p.replace('812','814') for i,p in enumerate(parts))
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py']
for n in names:
 assert sha(O/n)==read(O/'sources001.json')[n]
 assert not (K/n).exists();(K/n).write_bytes(ns((O/n).read_text()).encode())
decl=' uint32_t mc_before[10],mc_target[4],mc_attempted,mc_after[40],mc_undo[40],mc_cleanup_mask,mc_forward_mask;\n'
helpers='''/* Pinned704 final four geometry controls, in source order. All writes
 * remain blanked, followed by own saved-value recovery in reverse order.
 * Strict720p-derived baseline admission; an unexpected value refuses writes.
 * CR25/28/2D are same-value controls on this admitted baseline. */
static const uint8_t mc_regs[10]={0x1a,0x25,0x28,0x2d,0x13,0x19,0x17,0x18,7,9};
static const uint8_t mc_baseline[10]={0,0x10,0x83,0,0x68,0x30,0xe3,0xff,0x3e,0x40};
__attribute__((noinline)) int controls_forward814(struct result814 *o)
{
 o->forward_status=0x81450;
 for(unsigned j=0;j<10;++j){o->mc_before[j]=cr(mc_regs[j]);if(o->mc_before[j]!=mc_baseline[j])o->mc_forward_mask|=1u<<j;}
 if(o->mc_forward_mask)return 0;
 o->mc_target[0]=4;o->mc_target[1]=0x10;o->mc_target[2]=0x83;o->mc_target[3]=o->mc_before[3]&0xe0;
 for(unsigned i=0;i<4;++i){
  o->forward_status=0x81450+i;o->mc_attempted=i+1;cw(mc_regs[i],(uint8_t)o->mc_target[i]);
  for(unsigned j=0;j<10;++j){
   uint32_t v=cr(mc_regs[j]);o->mc_after[10*i+j]=v;
   if(v!=(j<=i?o->mc_target[j]:o->mc_before[j]))o->mc_forward_mask|=1u<<j;
  }
  if(o->mc_forward_mask)return 0;
 }
 return 1;
}
__attribute__((noinline)) void controls_restore814(struct result814 *o)
{
 for(unsigned n=o->mc_attempted;n>0;--n){
  unsigned i=n-1;cw(mc_regs[i],(uint8_t)o->mc_before[i]);
  for(unsigned j=0;j<10;++j){
   uint32_t v=cr(mc_regs[j]);o->mc_undo[10*i+j]=v;
   if(v!=(j<i?o->mc_target[j]:o->mc_before[j]))o->mc_cleanup_mask|=1u<<j;
  }
 }
}
'''
init=' for(unsigned j=0;j<40;++j)o->mc_after[j]=o->mc_undo[j]=0xffffffff;\n'
p=K/'probe.c';s=p.read_text();anchor='void probe814(struct result814 *o)';assert s.count(anchor)==1;s=s.replace(anchor,helpers+anchor)
s=s.replace(' o->forward_status=0x814;\nrestore:', ' if(!controls_forward814(o))goto restore;\n o->forward_status=0x814;\nrestore:\n controls_restore814(o);')
s=s.replace(' for(unsigned i=0;i<7;++i)o->h_checked',init+' for(unsigned i=0;i<7;++i)o->h_checked')
s=s.replace(' && !o->cl18_cleanup_mask){',' && !o->cl18_cleanup_mask && !o->mc_cleanup_mask){')
s=s.replace(' if(o->cl18_cleanup_mask)o->code=0x81449;',' if(o->cl18_cleanup_mask)o->code=0x81449;\n if(o->mc_cleanup_mask)o->code=0x81454;')
p.write_bytes(s.encode())
p=K/'probe.h';p.write_bytes(p.read_text().replace('};',decl+'};').encode())
p=K/'main.c';s=p.read_text().replace('words[820]','words[917]').replace('i<820','i<917').replace('crtc_linecompare_low_control','crtc_mode_controls')
s=s.replace('result.cl18_cleanup_mask){','result.cl18_cleanup_mask || result.mc_cleanup_mask){')
s=s.replace('result.code==0x81448)','result.code==0x81448 || (result.code>=0x81450 && result.code<=0x81453))')
p.write_bytes(s.encode())
for n,t in [('.gitattributes','* -text\n'),('.gitignore','__pycache__/\n*.pyc\n*.xbe\n*.exe\n*.obj\n*.jpg\n*.png\nconnection.json\n')]:
 (K/n).write_text(t)
(K/'delta001.json').write_text(json.dumps(dict(decl=decl,helpers=helpers,init=init,result_words=917,source_only=True,parent={n:sha(O/n) for n in names},recipe_sha256=sha(K.parent/'xcal-transaction704/transaction003.c')),indent=2)+'\n')
print('Prepared814 four-control kernel bundle, no physical admission')
