"""Source-only adaptation of closed825 and689. No launch or runtime reuse."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;W=K.parents[1]
pins={}
def take(kit,name,dest=None):
 p=W/'outputs'/kit/name;raw=p.read_bytes();pins[str(p.relative_to(W))]=hashlib.sha256(raw).hexdigest()
 q=K/(dest or name);assert not q.exists();q.write_bytes(raw);return q
for n in ['encoder.c','xcal_bus.c','xcal_bus.h','xcal_table.h','delay_candidate.h','gpu_preserving.c','gpu_types.h']:
 take('native-visible825',n)
p=take('native-visible825','transaction825.c','transaction826.c')
t=p.read_text().replace('Fresh825 complete-mode diagnostic','Fresh826 reserved-framebuffer loader diagnostic')
t=t.replace('r->base<0x2000000||r->base>=r->ram','r->base!=0x03700000||r->base>=r->ram')
t=t.replace('r->allocation<3686400','r->allocation!=0x00900000')
t=t.replace('r->tv_path_confirmed!=1','r->tv_path_confirmed!=1||r->incoming_base<0x02000000||\n (r->incoming_base&4095)||r->incoming_base>0x04000000-3686400')
t=t.replace('r32(g,0x600800)!=r->base||r32(g,0x680838)!=1279','r32(g,0x600800)!=r->incoming_base||r32(g,0x680838)!=1279')
for a,b in [('allocation','reserved_bytes'),('checked_bytes','pattern_extent'),('contiguous','reservation_checked'),('alias_checked','identity_checked')]:t=t.replace('r->'+a,'r->'+b)
p.write_text(t)
p=take('native-visible825','transaction.h');t=p.read_text()
t=t.replace('ram,base,allocation,checked_bytes,contiguous,alias_checked','ram,base,reserved_bytes,pattern_extent,reservation_checked,identity_checked')
t=t.replace('timer_hz,tv_path_confirmed;','timer_hz,tv_path_confirmed,incoming_base;')
t=t.replace('Only the retained720p allocation is admitted. Never pass703\'s smaller buffer.','826 uses the fixed nine-MiB loader reservation, not an nxdk allocation.\n * pattern_extent describes required bytes, not a successful memory test.\n * incoming_base is independently read from PCRTC_START before any mode write.')
p.write_text(t)
p=take('xcal-visible689','build.py','build001.py');t=p.read_text().replace('689','826')
t=t.replace("names=['entry','native','config','xcal_bus','indicator']","names=['entry','transaction826','encoder','xcal_bus','gpu_preserving']")
p.write_text(t)
(K/'source-reuse001.json').write_text(json.dumps({'source_only':True,'closed_runtime_reused':False,'pins':pins},indent=2)+'\n')
