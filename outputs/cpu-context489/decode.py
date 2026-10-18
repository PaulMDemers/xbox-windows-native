"""Independent raw CPU snapshot decoder; does not grant mapping/boot authority."""
import struct
def decode(data):
 def need(v,why):
  if not v:raise ValueError(why)
 need(len(data)==160,'size')
 w=struct.unpack('<40I',data)
 need(w[:3]==(0x39383443,1,160) and w[3] in (1,2) and w[4]==0x48900101,'identity')
 need(w[33]==1 and w[38:]==(0x454e4f44,0x48900101),'complete')
 need(not any(data[62:64]+data[70:72]+data[118:120]+data[126:132]+data[136:152]),'reserved')
 need(w[5]&2,'reserved EFLAGS bit')
 need(w[6:10]==w[24:28],'control registers changed during snapshot')
 need(data[56:62]==data[112:118] and data[64:70]==data[120:126],'descriptor registers changed')
 start=w[20]+(w[21]<<32);end=w[22]+(w[23]<<32)
 need(start<=end,'TSC reversed')
 gdt=struct.unpack_from('<HI',data,56);idt=struct.unpack_from('<HI',data,64)
 return dict(epoch=w[3],eflags=w[5],cr0=w[6],cr2=w[7],cr3=w[8],cr4=w[9],selectors=list(struct.unpack_from('<8H',data,40)),gdtr=list(gdt),idtr=list(idt),entry_esp=w[18],return_eip=w[19],tsc_start=start,tsc_end=end,atomic_snapshot=False,mapping_validated=False,descriptor_contents_read=False,physical_origin_requires_external_evidence=True)
