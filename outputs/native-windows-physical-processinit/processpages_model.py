"""Independent model of the first two MiRemoveAnyPage calls and static pool setup."""
import copy,struct,hashlib

def baseline(s):
 s=copy.deepcopy(s);new=s['directory'][769]>>12
 s['directory'][769]=0;s['tables'][s['directory'][768]>>12][769]=0
 if new:s['tables'].pop(new)
 return s

def verify_final(read,k,descriptors,e,processinit=False):
 from mapped_pfn_model import snapshot,expected
 from freewalk_model import capture,model
 from sysptes_model import FLAGS
 actual=capture(read,k,descriptors);pre=baseline(snapshot(read,k));data,_,_=expected(pre)
 before=dict(actual);before['directory']=pre['directory'];before['pfn_hex']=data.hex()
 before['descriptors']=[([5,0x3cf,0x1d91] if d==[5,0x160,0x2000] else d) for d in descriptors]
 before['free_head']=[0,1,0xffffffff,0xffffffff];before['walk_globals']=dict(actual['walk_globals']);before['walk_globals']['0x81bf8']=0
 data,info=model(before);head=list(info['free_head']);available=info['available']
 u=lambda o:struct.unpack_from('<I',data,o)[0]
 def w(o,v):struct.pack_into('<I',data,o,v&0xffffffff)
 for p,f in FLAGS.items():w(p*24+12,u(p*24+12)|f)
 chosen=[]
 for _ in range(2):
  co=90*4096+256;p=u(co);assert p<0x3c00 and p&31==0 and p in info['free_pfns']
  o=p*24;nxt=u(o);prev=u(o+8)
  if prev==0xffffffff:head[2]=nxt
  else:w(prev*24,nxt)
  if nxt==0xffffffff:head[3]=prev
  else:w(nxt*24+8,prev)
  head[0]-=1;w(co,u(o+16));w(o,0);w(o+8,0);w(o+12,(u(o+12)&0xffff0000)|(((u(o+12)>>4)&7)<<4));chosen.append(p)
 old=e[11]>>12;assert old not in chosen;w(old*24+8,0);w(old*24+12,u(old*24+12)&0xffff)
 if processinit:
  from processinit_model import finish
  chosen.append(finish(read,k,e,data,head,info))
 count=len(chosen)
 got=bytes.fromhex(actual['pfn_hex']);assert got==data,[(hex(i),hex(a),hex(b)) for i,(a,b) in enumerate(zip(got,data)) if a!=b][:30]
 assert actual['free_head']==head and actual['walk_globals']['0x81bf8']==available-count
 assert list(e[262:264])==chosen[:2] and e[264]==available-2 and e[266]==old
 u32=lambda a:struct.unpack('<I',read(a,4))[0]
 for off,typ in [(0x74ca0,0),(0x75600,2)]:
  values=list(struct.unpack('<264I',read(k+off,1056)))
  expect=[typ,0,0,0,0,0,0,k+0x6ca9c]+[k+off+(i&~1)*4 for i in range(8,264)]
  assert values==expect,(hex(off),[(i,hex(a),hex(b)) for i,(a,b) in enumerate(zip(values,expect)) if a!=b][:10])
 for off,value in {0x755f0:k+0x74ca0,0x755f8:k+0x75600,0x7534c:0,0x6ca9c:0,0x81ab8:0xc0301000,0x81b90:0xc03013fc,0x82374:0xc0501000,0x81aa8:0xc0501694}.items():assert u32(k+off)==value,hex(off)
 if not processinit:
  assert u32(0xc0300c04)&~0x60==(chosen[0]<<12)|3
  assert u32(0xc0301000)&~0x60==(chosen[1]<<12)|3
  assert read(0xc0301004,4092)==bytes(4092) and read(0xc0400000,4096)==bytes(4096)
  assert tuple(e[268:272])==(1,256,1,1)
 info.update(available_before_allocations=available,available=available-count,free_head=head,free_pfns=[p for p in info['free_pfns'] if p not in chosen],pfn_sha256=hashlib.sha256(data).hexdigest(),all_pfn_and_color_bytes_match=True)
 info['process_pages']={'page_table_pfn':chosen[0],'working_set_pfn':chosen[1],'pool_descriptor_list_heads_verified':256,'working_set_bytes_zero_verified':4096,'unused_page_table_bytes_zero_verified':4092,'all_pfn_and_color_bytes_match':True,'working_set_published':False}
 if processinit:info['process_pages']['scope']='Historical first-page checkpoint; zero contents verified before publication by the returning guard and emulator trace.'
 return info
