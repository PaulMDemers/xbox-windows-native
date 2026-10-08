"""Mutation checks against real frame0; never alter preserved capture files."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'candidate001';read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
trace=read(out/'trace.json');e=trace['cursor_events'][0];after=trace['events'][0]
raw=out/'artifacts'/e['raw'];ref=out/'artifacts'/e['reference_raw'];restored=out/'artifacts'/after['raw']
assert sha(raw)==e['sha256'] and sha(ref)==e['reference_sha256'] and sha(restored)==after['sha256']
reference=ref.read_bytes();frame=raw.read_bytes();plain=restored.read_bytes()
def expected(cursor=True,hotspot=7,wrong_mask=False):
 result=bytearray(reference)
 if cursor:
  for y in range(256):
   for x in range(384):
    dx=x-80+hotspot;dy=y-70+11
    if not (0<=dx<32 and 0<=dy<32):continue
    at=(y*384+x)*4;background=int.from_bytes(reference[at:at+3],'little')
    color=(background if dy>=16 else 0)^(0xffffff if (dx<16 if wrong_mask else dx>=16) else 0)
    result[at:at+3]=color.to_bytes(3,'little')
 return result
def mismatches(screen,want):
 return sum(screen[y*4096+x*4:y*4096+x*4+3]!=want[(y*384+x)*4:(y*384+x)*4+3] for y in range(256) for x in range(384))
want=expected();assert mismatches(frame,want)==0 and mismatches(plain,reference)==0
checks=[]
for name,data,oracle in [('missing cursor',frame,reference),('wrong hotspot',frame,expected(hotspot=8)),('wrong XOR polarity',frame,expected(wrong_mask=True)),('cursor ghost after move',frame,reference)]:
 n=mismatches(data,oracle);assert n>0;checks.append(dict(name=name,rejected=True,mismatches=n))
damaged=bytearray(frame);damaged[100*4096+250*4]^=1
n=mismatches(damaged,want);assert n==1;checks.append(dict(name='single noncursor RGB bit',rejected=True,mismatches=n))
dest=k/'oracle-tests.json';assert not dest.exists()
dest.write_text(json.dumps(dict(passed=True,baseline_visible_and_restored_match=True,checks=checks,
 pins={str(p.relative_to(k)):sha(p) for p in [raw,ref,restored,k/'test-oracle.py',out/'trace.json']}),indent=2)+'\n')
print('Five framebuffer oracle mutations rejected')
