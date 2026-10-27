/* Kernel-owned context sampling only. PCI reads use the kernel's serialized API;
 * no direct CF8 writes and no native transition. CRTC/SQ indices are restored. */
static int context707(void)
{
 static const unsigned cfg[][3]={{1,0,0},{1,0,4},{1,0,0x10},
  {0,33,0},{0,33,4},{0,33,0x14},{0,1,0},{0,1,4},{0,1,0x10},{0,1,0x84}};
 append("  \"pci_kernel_reads\":[");
 for(unsigned i=0;i<10;++i){ULONG value=0xffffffff;
  HalReadWritePCISpace(cfg[i][0],cfg[i][1],cfg[i][2],&value,4,FALSE);
  append("%s[%u,%u,%u,%lu]",i?",":"",cfg[i][0],cfg[i][1],cfg[i][2],(unsigned long)value);
 }
 append("],\n");
 static const unsigned char fields[]={0,1,2,3,4,5,6,7,9,0x10,0x11,0x12,0x13,
  0x14,0x15,0x16,0x17,0x18,0x19,0x1a,0x1b,0x1f,0x21,0x22,0x25,0x28,0x2d,0x33,0x39,0x44};
 unsigned char index=VIDEOREG8(0x6013d4),seq=VIDEOREG8(0xc03c4),values[sizeof(fields)],sq[5];
 for(unsigned i=0;i<sizeof(fields);++i){VIDEOREG8(0x6013d4)=fields[i];values[i]=VIDEOREG8(0x6013d5);}
 VIDEOREG8(0x6013d4)=index;
 for(unsigned i=0;i<5;++i){VIDEOREG8(0xc03c4)=i;sq[i]=VIDEOREG8(0xc03c5);}
 VIDEOREG8(0xc03c4)=seq;
 int restored=VIDEOREG8(0x6013d4)==index && VIDEOREG8(0xc03c4)==seq;
 append("  \"crtc_kernel_reads\":[");
 for(unsigned i=0;i<sizeof(fields);++i)append("%s[%u,%u]",i?",":"",fields[i],values[i]);
 append("],\n  \"sequencer_kernel_reads\":[%u,%u,%u,%u,%u],\n",sq[0],sq[1],sq[2],sq[3],sq[4]);
 append("  \"selectors_restored\":%s,\"native_transition\":false,\"native_video_programming\":false,\n",restored?"true":"false");
 uint32_t cr0,cr3,cr4,flags;uint16_t cs,ds,ss;
 __asm__ volatile("mov %%cr0,%0":"=r"(cr0));
 __asm__ volatile("mov %%cr3,%0":"=r"(cr3));
 __asm__ volatile("mov %%cr4,%0":"=r"(cr4));
 __asm__ volatile("pushfl;popl %0":"=r"(flags)::"memory");
 __asm__ volatile("mov %%cs,%0":"=r"(cs));
 __asm__ volatile("mov %%ds,%0":"=r"(ds));
 __asm__ volatile("mov %%ss,%0":"=r"(ss));
 append("  \"pre_file_write_cpu\":[%lu,%lu,%lu,%lu,%u,%u,%u],\n",(unsigned long)flags,(unsigned long)cr0,(unsigned long)cr3,(unsigned long)cr4,cs,ds,ss);
 int saved=checkpoint("kernel_context_captured",0);
 return saved || !restored;
}

static int contiguous707(void *v,uint32_t p,uint32_t n)
{
 for(uint32_t off=0;off<n;off+=4096)if(MmGetPhysicalAddress((char*)v+off)!=p+off)return 0;
 return MmGetPhysicalAddress((char*)v+n-1)==p+n-1;
}
static int allocation_probe707(uint32_t fb,uint32_t fb_bytes,uint32_t fb_allocation)
{
 struct plan705 p={0};p.framebuffer=fb;p.framebuffer_size=fb_bytes;p.framebuffer_allocation=fb_allocation;
 void *source=NULL,*stub=NULL,*alias=NULL;SIZE_T region=32768;int copied=0,alias_created=0;
 LONG free_status=0;
 if(checkpoint("before_allocations",0))return 0;
 source=MmAllocateContiguousMemoryEx(0x100000,0x200000,0x1ffffff,0,PAGE_READWRITE);
 if(source){
  p.source=MmGetPhysicalAddress(source);p.source_size=0x100000;p.source_allocation=MmQueryAllocationSize(source);
  if(p.source_allocation>=p.source_size && p.source>=0x200000 && p.source<=0x1f00000 && !(p.source&4095))p.source_contiguous=contiguous707(source,p.source,p.source_size);
 }
 if(p.source_contiguous)stub=MmAllocateContiguousMemoryEx(32768,0x1000000,0x1ffffff,16,PAGE_READWRITE);
 if(stub){
  p.stub=MmGetPhysicalAddress(stub);p.stub_size=32768;p.stub_allocation=MmQueryAllocationSize(stub);
  if(p.stub_allocation>=32768 && p.stub>=0x1000000 && p.stub<=0x1ff8000 && !(p.stub&4095))p.stub_contiguous=contiguous707(stub,p.stub,32768);
 }
 p.status=0xffffffff;
 if(p.stub_contiguous){
  p.requested=p.stub;alias=(void*)p.requested;
  p.status=NtAllocateVirtualMemory(&alias,0,&region,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
  alias_created=!(p.status&0x80000000);p.returned=(uint32_t)alias;p.region_size=region;
  if(alias_created && reservation_contains705(p.requested,p.returned,region)){
   for(unsigned i=0;i<8;++i){p.alias[i]=MmGetPhysicalAddress((void*)(p.requested+4096*i));p.alias_last[i]=MmGetPhysicalAddress((void*)(p.requested+4096*i+4095));}
  }
 }
 uint32_t refusal=admit705(&p);
 append("  \"allocation_plan_words\":[");
 uint32_t words[31];_Static_assert(sizeof(p)==sizeof(words),"plan schema");memcpy(words,&p,sizeof(words));
 for(unsigned i=0;i<sizeof(p)/sizeof(uint32_t);++i)append("%s%lu",i?",":"",(unsigned long)words[i]);
 append("],\n  \"allocation_refusal_bits\":%lu,\n",(unsigned long)refusal);
 if(!checkpoint("after_allocations",0) && !refusal){
  /* Deterministic page-distinct data, never executable code. Full comparisons
   * through both mappings are required, including identity aliases. */
  unsigned char *bytes=source;
  for(unsigned i=0;i<32768;++i)bytes[i]=(unsigned char)((i*73u)^(i>>8)^(i>>12)^0xa5u);
  memcpy((void*)p.requested,source,32768);memcpy(stub,source,32768);
  copied=!memcmp((void*)p.requested,source,32768)&&!memcmp(stub,source,32768);
 }
 if(alias_created){SIZE_T zero=0;free_status=NtFreeVirtualMemory(&alias,&zero,MEM_RELEASE);}
 if(stub)MmFreeContiguousMemory(stub);
 if(source)MmFreeContiguousMemory(source);
 append("  \"cleanup\":{\"copies_verified\":%s,\"bytes\":32768,\"alias_created\":%s,\"alias_free_status\":%lu,\"source_freed\":%s,\"stub_freed\":%s,\"native_transition\":false},\n",
  copied?"true":"false",alias_created?"true":"false",(unsigned long)free_status,source?"true":"false",stub?"true":"false");
 int saved=checkpoint("allocations_released",0);
 return !refusal && copied && free_status>=0 && !saved;
}
