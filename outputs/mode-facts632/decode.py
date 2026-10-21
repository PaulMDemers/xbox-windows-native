"""Strict register-fact log and independent observed-subset comparison."""
import json,re
from pathlib import Path
K=Path(__file__).resolve().parent
def decode(data):
 f=json.loads((K.parent/'hd-profile310/profile-facts.json').read_text())
 lines=data.decode('ascii').splitlines()
 assert len(lines)==79 and lines[0]=='XWN_FACTS632 version=1 kernel=1.0.4034.1 error=0 reads=17'
 assert lines[-1]=='COMPLETE error=0 log_ok=1'
 at=1;groups={}
 for group,indices,key in [('CR',f['crtc_indices'],'index'),('MM',f['mmio_offsets'],'offset'),('EN',f['encoder_indices'],'index')]:
  values={}
  for i in indices:
   width=8 if group=='MM' else 2
   m=re.fullmatch(group+' '+key+r'=([0-9a-f]{'+str(width)+r'}) value=([0-9a-f]{'+str(width)+r'})',lines[at]);at+=1
   assert m and int(m[1],16)==i;values[i]=int(m[2],16)
  groups[group]=values
 actual=json.loads((K.parent/'mode-switch631/physical-collection002.json').read_text())['decoded']['stages'][0]
 comparisons=[];differences=[]
 for key,value in actual['crtc'].items():
  i=int(key);mask={0x19:0xe0,0x2d:1}.get(i,255)
  assert groups['CR'][i]&mask==value&mask,(i,groups['CR'][i],value)
  comparisons.append(('CR',i,mask,value))
  if groups['CR'][i]!=value:differences.append(dict(index=i,programmed=groups['CR'][i],readback=value,mask=mask,other_bits='unknown'))
 for i,v in enumerate(actual['fp']):
  off=0x680800+4*i
  if off in groups['MM']:assert groups['MM'][off]==v;comparisons.append(('MM',off,0xffffffff,v))
  else:assert i in (7,15)
 assert groups['MM'][0x680600]==actual['mmio'][str(0x680600)]
 comparisons.append(('MM',0x680600,0xffffffff,actual['mmio'][str(0x680600)]))
 old=json.loads((K.parent/'hd-matrix309/source-review001.json').read_text())['independent_matrix'][2]
 assert [groups['EN'][i] for i in f['encoder_indices'] if i!=0x6c]==old
 assert groups['EN'][0x6c]==0x46 # programmed value, not unknown hardware readback0
 assert 8*(((groups['CR'][0x19]&0xe0)<<3)|groups['CR'][0x13])==2880
 return dict(passed=True,mode_code='88080801',width=720,height=480,stride=2880,visible_bytes=1382400,groups=groups,hardware_compared_fields=len(comparisons),programmed_readback_differences=differences,unobserved_crtc_fields=12,unobserved_mode_mmio_fields=13,encoder_programming_matches_historical_facts=True,full_kernel_identity_recreated=False,native_windows_qualified=False)
