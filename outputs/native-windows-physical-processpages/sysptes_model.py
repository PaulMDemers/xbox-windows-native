"""Model the pinned system-PTE caches and PFN flags from native code."""
import struct
SIZES=[1,2,4,8,16];COUNTS=[400,100,60,50,40]
START=0xc03e3000;COUNT=22702;END=START+COUNT*4
FLAGS={0x374:2,0x3cd:4,0x17c:6,0x17d:6,0x17e:6,0x17f:6}
def model(k):
 ptes=[0]*COUNT;g={0x81258:START,0x81260:END-4,0x81268:3,0x81254:0,0x81bfc:COUNT,0x6cae4:0,0x6cae8:0};at=0
 for i in reversed(range(5)):
  size,n=SIZES[i],COUNTS[i];a=START+at*4
  g[0x81240+i*4]=((a-0xc0200000)//4)<<12;g[0x81220+i*4]=a+(n-1)*size*4;g[0x81280+i*4]=n
  for j in range(n):
   ptes[at+j*size]=0xfffff000 if j==n-1 else ((a+(j+1)*size*4-0xc0200000)//4)<<12
   if size>1:ptes[at+j*size+1]=0x2000
  at+=n*size
 assert at==1880
 ptes[at]=0xfffff000;ptes[at+1]=(COUNT-at)<<12;g[0x81218]=COUNT-at;g[0x82398]=((START+at*4-0xc0200000)//4)<<12
 return ptes,g

def verify(read,k):
 ptes,g=model(k)
 actual=b''.join(read(START+o,min(4096,COUNT*4-o)) for o in range(0,COUNT*4,4096))
 assert actual==struct.pack('<'+str(COUNT)+'I',*ptes),'System PTE contents differ from cache model'
 for o,v in g.items():assert struct.unpack('<I',read(k+o,4))[0]==v,(hex(o),hex(v))
 for i,n in enumerate(SIZES):assert struct.unpack('<I',read(k+0x72e50+i*4,4))[0]==n
 return {'all_system_ptes_verified':COUNT,'cached_ptes':1880,'cache_blocks':sum(COUNTS),'remaining_ptes':COUNT-1880,'cache_heads_tails_counts_verified':True,'pfn_flags_changed':len(FLAGS)}
