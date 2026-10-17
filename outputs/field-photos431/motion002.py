"""Relate actual unchanged-source movement to a hypothetical parity sampler."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'outputs/field-scanout428'))
from oracle import expected
out=K/'motion002.json';assert not out.exists()
source=W/'outputs/field-scanout428/probe.c'
s=source.read_text();assert 'y=32+((step*3)%64)' in s
assert 'if(phase==2)' in s
data=expected(2);examples=[];checks=0
for screen_parity in (0,1):
 previous=None
 for step in range(256):
  top=32+(step*3)%64
  # First source row selected by a fixed absolute-screen parity, not a claim
  # about which electrical field/TV algorithm is actually in use.
  row=(screen_parity-top)%2
  def pixel(x):
   at=(row*1024+x)*4;return int.from_bytes(data[at:at+3],'little')
  pair=(pixel(0),pixel(960))
  assert pair in ((0,0xff00ff),(0xffffff,0x00ff00))
  if previous is not None:assert pair!=previous
  previous=pair;checks+=1
  if step<4:examples.append(dict(screen_parity=screen_parity,step=step,top=top,source_row=row,one_line=pair[0],marker=pair[1]))
r=dict(passed=True,modeled_positions=checks,probe_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),source_phase=2,examples=examples,user_correction='when the test moves, the green column alternates between green and purple. the black/white columns flash',interpretation='Odd-row movement of unchanged source swaps visible parity colors under the modeled fixed-screen-parity sampler. Live user observation means camera-only sampling cannot fully explain the symptom.',limits=['No frame/field frequency measurement','Not proof of a fixed-parity sampler versus bob/interpolating/motion-adaptive processing','No identification of encoder, adapter or TV','No new hardware experiment or native code change'])
out.write_text(json.dumps(r,indent=2)+'\n');print('Modeled positions:',checks)
