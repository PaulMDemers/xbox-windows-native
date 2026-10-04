"""Pinned independent model of MmInitializeProcessAddressSpace's initial-process path."""
import struct

def process_model(raw,process,ws):
 b=bytearray(raw)
 values={0xd0:0,0xd4:0,0xdc:1,0xe0:4,0xe4:4,0xe8:50,0xec:450,0xf0:0xc0501000,0x114:1,0x130:1,0x138:0,0x140:0,0x144:process+0x144,0x148:process+0x144,0x150:ws,0x158:1,0x160:0,0x168:0,0x16c:process+0x16c,0x170:process+0x16c,0x1e8:process+0x1e8,0x1ec:process+0x1e8,0x280:0}
 for off,v in values.items():struct.pack_into('<I',b,off,v)
 for off,v in {0x13c:1,0x13e:4,0x156:2,0x164:1,0x166:4}.items():b[off]=v
 return b

def finish(read,k,e,data,head,info):
 u=lambda o:struct.unpack_from('<I',data,o)[0]
 def w(o,v):struct.pack_into('<I',data,o,v&0xffffffff)
 co=90*4096+256;p=u(co);assert p<0x3c00 and p&31==0 and p==e[294]
 o=p*24;nxt=u(o);prev=u(o+8)
 if prev==0xffffffff:head[2]=nxt
 else:w(prev*24,nxt)
 if nxt==0xffffffff:head[3]=prev
 else:w(nxt*24+8,prev)
 head[0]-=1;w(co,u(o+16))
 old=e[266];table=e[262];ws=e[263];proc=e[265]
 rows={old:[proc,0xc0300c00,3,0x10601,0x80,old],table:[1,0xc0300c04,3,0x10601,0x80,old],ws:[2,0xc0301404,1,0x10601,0x80,table],p:[3,0xc0301bc8,1,0x10601,0x80,table]}
 for pfn,row in rows.items():struct.pack_into('<6I',data,pfn*24,*row)
 assert struct.unpack('<I',read(0xc0300c04,4))[0]&~0x60==(table<<12)|3
 actual=list(struct.unpack('<1024I',read(0xc0301000,4096)))
 expect=[0]*1024;expect[0]=expect[754]=(p<<12)|3;expect[257]=(ws<<12)|3
 assert all((a&~0x60 if b else a)==b for a,b in zip(actual,expect))
 working=[0]*1024
 fields={0:50,4:4,8:4,12:50,16:3,20:0xc0501694,28:0x25a,36:0xc06f2000,40:512,44:0xc06f2000,48:0xc0800000}
 for off,v in fields.items():working[off//4]=v
 working[421:425]=[0xc0300203,0xc0301203,0xc0501203,0xc06f2203]
 for i in range(425,1023):working[i]=(i-420)<<4
 working[1023]=0xfffffff0
 assert list(struct.unpack('<1024I',read(0xc0501000,4096)))==working
 assert read(0xc06f2000,4096)==bytes(4096)
 for off,v in {0x81e08:1,0x82340:1,0x81bf8:info['available']-3}.items():assert struct.unpack('<I',read(k+off,4))[0]==v
 for off,v in {0xdc:1,0xe0:4,0xe4:4,0xe8:50,0xec:450,0xf0:0xc0501000,0x114:1,0x150:ws}.items():assert struct.unpack('<I',read(proc+off,4))[0]==v
 assert e[293]==e[296]==e[297]==e[298]==e[299]==e[300]==e[305]==1 and e[304]==0 and e[303]==1
 info['process_initialization']={'native_return_status':e[304],'hash_page_pfn':p,'working_set_entries':4,'working_set_dwords_verified':1024,'page_table_dwords_verified':1024,'hash_page_zero_bytes_verified':4096,'full_process_and_thread_snapshot_checked_by_hal':True,'full_process_delta_checked_in_emulator_trace':True}
 return p
