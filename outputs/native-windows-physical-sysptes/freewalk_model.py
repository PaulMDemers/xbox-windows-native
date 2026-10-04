import struct,json,hashlib
from pathlib import Path

def model(before):
 data=bytearray.fromhex(before['pfn_hex']);directory=before['directory'];wg=before['walk_globals']
 head=list(before['free_head']);assert head==[0,1,0xffffffff,0xffffffff],head
 assert wg['0x81bf8']==0 and wg['0x8119c']==31 and wg['0x811b8']==0xffbdf000 and wg['0x811bc']==0xffbdf100
 u=lambda o:struct.unpack_from('<I',data,o)[0]
 def w(o,v):struct.pack_into('<I',data,o,v&0xffffffff)
 inserted=[];new_inuse=[];preserved=[];events=[]
 for typ,base,pages in reversed(before['descriptors']):
  if typ in (6,22,23):pages=max(0,min(pages,0x3c00-base))
  assert typ!=3,'Unmodeled bad-page descriptor'
  for pfn in range(base,base+pages):
   assert pfn<0x3c00
   o=pfn*24
   if typ in (2,4,5,8):
    if u(o+12)>>16:preserved.append(pfn);continue
    assert not u(o+12)&0x2000
    w(o+4,pfn<<2)
    prev=head[3]
    if prev==0xffffffff:head[2]=pfn
    else:w(prev*24,pfn)
    head[3]=pfn;head[0]+=1
    w(o,0xffffffff);w(o+8,prev);w(o+12,(u(o+12)&~0x700)|0x100)
    co=90*4096+256+(pfn&31)*8
    if u(co)==0xffffffff:w(co,pfn)
    else:w(u(co+4)-0xffb85000+16,pfn)
    w(co+4,0xffb85000+o);w(o+16,0xffffffff)
    inserted.append(pfn)
    if len(inserted) in (2,19):events.append(0x81dc0 if len(inserted)==2 else 0x812a0)
    if len(inserted)==wg['0x727d8']:events.append(0x81c20)
   elif not u(o+12)>>16:
    va=0x80000000+pfn*4096
    w(o+4,0xc0000000+(va>>12)*4);w(o+8,u(o+8)+1)
    w(o+12,((u(o+12)&0xffff)|0x10000)&0xfffffe8f|0x600)
    w(o+20,directory[va>>22]>>12);new_inuse.append(pfn)
   else:preserved.append(pfn)
 return data,{'free_head':head,'available':len(inserted),'new_inuse':len(new_inuse),'preserved':len(preserved),'expected_event_rvas':[hex(v) for v in events],'free_pfns':inserted}

def capture(read,k,descriptors):
 from mapped_pfn_model import snapshot
 state=snapshot(read,k);state['pfn_hex']=state.pop('pfn').hex();state['descriptors']=descriptors
 offsets=[0x727bc,0x727cc,0x811b8,0x811bc,0x8119c,0x81bf8,0x727d8,0x81b48]
 state['walk_globals']={hex(o):struct.unpack('<I',read(k+o,4))[0] for o in offsets}
 state['free_head']=list(struct.unpack('<4I',read(state['walk_globals']['0x727bc'],16)))
 state['events']={hex(o):read(k+o,16).hex() for o in [0x81dc0,0x812a0,0x81c20]}
 return state

def verify(before,after,sysptes=False):
 expected,info=model(before);actual=bytes.fromhex(after['pfn_hex'])
 if sysptes:
  from sysptes_model import FLAGS
  for pfn,flags in FLAGS.items():
   old=struct.unpack_from('<I',expected,pfn*24+12)[0];struct.pack_into('<I',expected,pfn*24+12,old|flags)
 assert actual==expected,[(hex(i),hex(x),hex(y)) for i,(x,y) in enumerate(zip(actual,expected)) if x!=y][:50]
 assert after['free_head']==info['free_head']
 assert after['walk_globals']['0x81bf8']==info['available']
 assert after['walk_globals']['0x81b48']==1
 assert after['descriptors']==before['descriptors']
 assert before['tables'].keys()==after['tables'].keys()
 for p,table in before['tables'].items():assert all(x&~0x60==y&~0x60 for x,y in zip(table,after['tables'][p])),p
 for off,raw in after['events'].items():
  vals=struct.unpack('<4I',bytes.fromhex(raw));old=struct.unpack('<4I',bytes.fromhex(before['events'][off]))
  assert vals[0]==old[0] and vals[1]==1 and vals[2:]==old[2:]
 info['pfn_sha256']=hashlib.sha256(expected).hexdigest()
 info['all_pfn_and_color_bytes_match']=True;info['all_paging_entries_preserved']=True
 return info

def verify_final(read,k,descriptors,sysptes=False):
 from mapped_pfn_model import expected
 if sysptes:
  assert [5,0x160,0x2000] in descriptors
  descriptors=[([5,0x3cf,0x1d91] if d==[5,0x160,0x2000] else d) for d in descriptors]
 after=capture(read,k,descriptors);before=dict(after)
 pre=dict(after);pre['pfn']=bytes.fromhex(pre['pfn_hex'])
 pfn,tables,_=expected(pre)
 before['pfn_hex']=pfn.hex();before['free_head']=[0,1,0xffffffff,0xffffffff]
 before['walk_globals']=dict(after['walk_globals']);before['walk_globals']['0x81bf8']=0;before['walk_globals']['0x81b48']=0
 return verify(before,after,sysptes=sysptes)
