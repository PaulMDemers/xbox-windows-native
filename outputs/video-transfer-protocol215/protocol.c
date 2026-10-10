/* SPDX-License-Identifier: GPL-2.0-or-later
 * Source-pinned candidate command encoding; no actual submission or ownership grant.
 */
#include "protocol.h"
#include "model-values.h"
static uint32_t header(uint32_t sub,uint32_t method,uint32_t count)
{ return (count<<18)|(sub<<13)|method; }
static int span(uint32_t off,uint32_t pitch,uint32_t width,uint32_t height,
                uint32_t capacity,uint32_t *end)
{
 uint64_t last=(uint64_t)off+(uint64_t)(height-1)*pitch+width*4u;
 if(off<16 || (off&3) || (pitch&3) || pitch>65535 || pitch<width*4u || last+16>capacity)return 0;
 *end=(uint32_t)last;return 1;
}
static uint32_t hash_slot(uint32_t handle,uint32_t channel)
{
 uint32_t h=0;
 while(handle){h^=handle&2047u;handle>>=11;}
 return h^(channel<<7);
}
int x215_plan(const X215Input *in,X215Plan *out)
{
 X215Plan p={0};uint32_t i,j,n=0;
 static const uint32_t handles[7]={0x97,0x62,0x9f,3,4,8,6};
 static const uint32_t classes[3]={NV_KELVIN_PRIMITIVE,NV_CONTEXT_SURFACES_2D,NV_IMAGE_BLIT};
 static const uint32_t dma_class[4]={NV_DMA_FROM_MEMORY_CLASS,NV_DMA_TO_MEMORY_CLASS,NV_DMA_TO_MEMORY_CLASS,NV_DMA_FROM_MEMORY_CLASS};
 if(!in || !out || !in->token || !in->width || in->width>16 || !in->height || in->height>8 || in->channel>31)return 0;
 for(i=0;i<4;i++) {
  uint64_t end=(uint64_t)in->range[i].base+in->range[i].bytes;
  if((in->range[i].base&4095) || in->range[i].bytes<4096 || in->range[i].bytes>65536 ||
     (in->range[i].bytes&4095) || end>0x03c00000u)return 0;
  for(j=0;j<i;j++)if(in->range[i].base<(uint64_t)in->range[j].base+in->range[j].bytes &&
                       in->range[j].base<end)return 0;
 }
 if(!span(in->source_offset,in->source_pitch,in->width,in->height,in->range[0].bytes,&p.source_end) ||
    !span(in->dest_offset,in->dest_pitch,in->width,in->height,in->range[1].bytes,&p.dest_end))return 0;
 if((in->ramht_base&4095) || in->ramht_base>0x1f000 || (in->objects_base&15) ||
    (uint64_t)in->objects_base+7*16>0x100000 ||
    (in->objects_base<in->ramht_base+4096 && in->ramht_base<in->objects_base+7*16))return 0;
 for(i=0;i<7;i++) {
  uint32_t slot=hash_slot(handles[i],in->channel),instance=in->objects_base+i*16;
  if(slot>=512 || (instance>>4)>65535)return 0;
  for(j=0;j<i;j++)if(in->ramht_base+slot*8==p.entry[j].address)return 0;
  p.entry[i].address=in->ramht_base+slot*8;p.entry[i].handle=handles[i];
  p.entry[i].context=0x80000000u|(in->channel<<24)|(i<3?0x10000u:0)|(instance>>4);
 }
 for(i=0;i<3;i++)p.graphics[i][0]=classes[i];
 for(i=0;i<4;i++) {
  /* pbkit descriptor form is a reference, not a verified NT5 physical DMA ABI.
   * Actual model masks frame low bits and ignores target/class validation. */
  p.dma[i][0]=dma_class[i]|0xb000u;p.dma[i][1]=in->range[i].bytes-1;
  p.dma[i][2]=p.dma[i][3]=in->range[i].base|3u;
 }
#define EMIT(x) p.words[n++]=(x)
 EMIT(header(0,0,1));EMIT(handles[0]);
 EMIT(header(0,NV097_SET_CONTEXT_DMA_SEMAPHORE,1));EMIT(handles[5]);
 EMIT(header(0,NV097_SET_SEMAPHORE_OFFSET,1));EMIT(16);
 EMIT(header(1,0,1));EMIT(handles[1]);
 EMIT(header(1,NV062_SET_CONTEXT_DMA_IMAGE_SOURCE,2));EMIT(handles[3]);EMIT(handles[4]);
 EMIT(header(1,NV062_SET_COLOR_FORMAT,4));EMIT(NV062_SET_COLOR_FORMAT_LE_A8R8G8B8);
 EMIT(in->source_pitch|(in->dest_pitch<<16));EMIT(in->source_offset);EMIT(in->dest_offset);
 EMIT(header(2,0,1));EMIT(handles[2]);
 EMIT(header(2,NV09F_SET_CONTEXT_SURFACES,1));EMIT(handles[1]);
 EMIT(header(2,NV09F_SET_OPERATION,4));EMIT(NV09F_SET_OPERATION_SRCCOPY);EMIT(0);EMIT(0);
 EMIT(in->width|(in->height<<16));
 EMIT(header(0,NV097_BACK_END_WRITE_SEMAPHORE_RELEASE,1));EMIT(in->token);
#undef EMIT
 if(n!=X215_WORDS)return 0;
 p.packet_bytes=n*4;*out=p;return 1;
}
int x215_prepare(X215Context *c,const X215Plan *p,uint32_t generation,uint64_t now,uint64_t budget)
{
 if(!c || !p || c->state!=X215_EMPTY || p->packet_bytes!=108 || p->words[25]!=0x41d70 || p->words[26]!=generation || !generation || !budget || budget>1000000 || now>UINT64_MAX-budget)return 0;
 c->generation=generation;c->last_time=now;c->deadline=now+budget;c->state=X215_PREPARED;return 1;
}
int x215_expose(X215Context *c,uint32_t proofs,uint64_t now)
{
 if(!c || c->state!=X215_PREPARED || proofs!=X215_PROOF_ALL || now<c->last_time || now>=c->deadline)return 0;
 c->last_time=now;c->state=X215_EXPOSED;return 1;
}
int x215_submit(X215Context *c)
{ if(!c || c->state!=X215_EXPOSED)return 0;c->state=X215_SUBMITTED;return 1; }
int x215_observe(X215Context *c,uint32_t generation,uint32_t token,uint64_t now,int fault)
{
 if(!c || c->state!=X215_SUBMITTED || generation!=c->generation)return 0;
 if(fault || now<c->last_time || now>=c->deadline || (token && token!=c->generation))
 {c->state=X215_QUARANTINED;return 0;}
 c->last_time=now;if(token==c->generation)c->state=X215_COMPLETE;return token==c->generation;
}
int x215_drain(X215Context *c,uint32_t generation,uint32_t proofs)
{ if(!c || c->state!=X215_COMPLETE || generation!=c->generation || proofs!=X215_DRAIN_ALL)return 0;c->state=X215_DRAINED;return 1; }
int x215_release(X215Context *c)
{ if(!c || (c->state!=X215_PREPARED && c->state!=X215_DRAINED))return 0;c->state=X215_RELEASED;return 1; }
int x215_abort(X215Context *c)
{
 if(!c)return 0;
 if(c->state==X215_PREPARED){c->state=X215_RELEASED;return 1;}
 if(c->state>=X215_EXPOSED && c->state<=X215_COMPLETE)c->state=X215_QUARANTINED;
 return 0;
}
