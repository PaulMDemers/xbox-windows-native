"""Decode read-only trace observations; never contact or modify a console."""
import argparse,json,struct,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('trace',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
b=a.trace.read_bytes();assert len(b)==4096 and b[:16]==b'XWN-VID-TRACE01\n'
count=struct.unpack_from('<I',b,16)[0];assert 1<=count<=254
records=[struct.unpack_from('<4I',b,32+i*16) for i in range(count)]
groups=[]
for event,x,y,z in records:
 if event==0x20:groups.append({'virtual':x,'physical':y,'length':z,'pages':{},'msrs':{}})
 elif event in range(0x21,0x26):
  assert groups;g=groups[-1]
  if event==0x21:g.update(cr0=x,cr3=y,cr4=z)
  elif event==0x22:g.update(cpuid1_eax=x,features_edx=y,ram_offset=z)
  elif event==0x23:g['pages'][str(x)]={'virtual':y,'pde':z}
  elif event==0x24:g['pages'][str(x)].update(pte=y,large_page=bool(z))
  elif event==0x25:g['msrs'][hex(x)]=y|(z<<32)
assert groups, 'No mapping observation records'
types={0:'UC',1:'WC',4:'WT',5:'WP',6:'WB',7:'UC-'}
for g in groups:
 for tag,v in g['pages'].items():
  entry=v['pde'] if v['large_page'] else v['pte'];v['present']=bool(entry&1)
  if not v['present']:continue
  v['physical']=(entry&0xffc00000)+(v['virtual']&0x3fffff) if v['large_page'] else (entry&0xfffff000)+(v['virtual']&4095)
  pat_bit=12 if v['large_page'] else 7
  v['pat_index']=((entry>>pat_bit)&1)*4+((entry>>4)&1)*2+((entry>>3)&1)
  pat=g['msrs'].get('0x277')
  v['pat_type']=types.get((pat>>(8*v['pat_index']))&255,'reserved') if pat is not None else 'not captured'
  # Strong UC cannot be promoted by MTRRs. Do not guess other combinations.
  v['effective_type']='UC' if v['pat_type']=='UC' or g['cr0']&(1<<30) else 'requires MTRR/PAT combination review'
 g['known_aliases_only']=True
r={'scope':__doc__,'trace_sha256':hashlib.sha256(b).hexdigest(),'records':count,'mapping_observations':groups,
 'limits':'Current address space and known loader alias endpoints only, not an exhaustive alias scan. Raw MTRRs retained; non-UC effective types require separate review. No cache state changed.'}
a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
