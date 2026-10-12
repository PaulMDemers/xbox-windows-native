"""Independent log admission; CPU framebuffer results distinct from TV observation."""
import re,json
from pathlib import Path
expected=json.loads((Path(__file__).resolve().parent/'expected.json').read_text())
def decode(data):
 lines=[x.strip() for x in data.decode('ascii').splitlines() if x.strip()]
 assert re.fullmatch(r'XWN_HD292 version=1 kernel=\d+\.\d+\.\d+\.\d+',lines[0])
 def fields(line,names):
  values=re.findall(r'(\w+)=([0-9a-f]+)',line)
  assert [a for a,b in values]==names,(line,names)
  return dict(values)
 settings=[x for x in lines if x.startswith('SETTINGS ')];assert len(settings)==1
 value=int(fields(settings[0],['value'])['value'],16);assert value&255==4 and value&0xe0000==0xe0000
 modes=[x for x in lines if x.startswith('MODE ')];assert len(modes)==3
 sets=[x for x in lines if x.startswith('SET ')];assert len(sets)==3
 rows=[]
 for i,(line,e) in enumerate(zip(modes,expected)):
  x=fields(line,['stage','width','height','bytes','allocation','physical','scanout','hvalid','vvalid','mismatches','crc','tick'])
  for name in ['stage','width','height','bytes']:assert int(x[name])==e[name]
  assert x['crc']==e['crc'] and int(x['mismatches'])==0
  size=int(x['allocation']);pa=int(x['physical'],16)
  assert int(x['bytes'])<=size<=int(x['bytes'])+4095 and 0<pa and pa+size<=64*1024**2
  assert int(x['scanout'],16)==pa
  ss=fields(sets[i],['stage','width','height','tick'])
  for name in ['stage','width','height']:assert int(ss[name])==e[name]
  fps=[f for f in lines if f.startswith('FP stage='+str(i+1)+' ')];assert len(fps)==16
  fp=[]
  for j,f in enumerate(fps):
   ff=fields(f,['stage','index','value']);assert int(ff['index'])==j;fp.append(int(ff['value'],16))
  x['fp']=fp;rows.append(x)
 completion=[x for x in lines if x.startswith('COMPLETE ')];assert len(completion)==1 and lines[-1]==completion[0]
 c=fields(completion[0],['error','log_ok','mode_changes']);assert c==dict(error='0',log_ok='1',mode_changes='3')
 assert len(lines)==57 # header + settings + 3*(set+mode+16FP) + complete
 return dict(passed=True,settings=value,rows=rows,exact_expected_crc_bytes=sum(e['bytes'] for e in expected),physical_tv_observation='Not inferred from logs',windows_hd_qualified=False)
