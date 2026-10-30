/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "firmware/led830.h"
static unsigned reads,writes,starts,acks,stage,reg,data,fail_at;
static uint16_t entry,terminal,final;
static unsigned command_regs[128],command_data[128];
static uint32_t clock830,step;
static unsigned tick_calls;
static void reset(void){reads=writes=starts=acks=stage=reg=data=fail_at=tick_calls=0;entry=final=0;terminal=0x10;clock830=0xfffffe00u;step=1687500;}
static uint16_t r16(void *p,unsigned off){assert(!p&&off==0);++reads;return stage==0?entry:stage==1?terminal:final;}
static void w8(void *p,unsigned off,uint8_t v){
 assert(!p);++writes;
 if(off==4){assert(v==0x20);stage=0;}
 else if(off==8){assert(v==7||v==8);reg=v;}
 else {assert(off==2&&v==0x0a&&starts<128);command_regs[starts]=reg;command_data[starts]=data;++starts;stage=1;if(fail_at&&starts==fail_at)terminal=0x11;}
}
static void w16(void *p,unsigned off,uint16_t v){assert(!p);++writes;if(off==6){assert(v<=255);data=v;}else{assert(off==0&&v==(terminal&0x37)&&!(terminal&0x808));++acks;stage=2;}}
static uint32_t tick(void *p){assert(!p);++tick_calls;clock830+=step;return clock830;}
static struct xcal_bus bus={0,0,r16,w8,w16,3};
static void expect_frame(unsigned ph,unsigned er){
 unsigned j=0;
#define CMD(r,v) do {assert(command_regs[j]==(r)&&command_data[j]==(v));++j;} while(0)
 CMD(8,255);CMD(7,1);CMD(8,0);
 for(unsigned i=0;i<ph;++i){CMD(8,240);CMD(8,0);}
 for(unsigned i=0;i<er;++i){CMD(8,15);CMD(8,0);}
 assert(j==starts&&acks==starts);
 assert(tick_calls==2*(22+2*(ph+er)));
#undef CMD
}
int main(void){
 unsigned cases=0;
 for(unsigned s=0;s<65536;++s){reset();entry=(uint16_t)s;int want=(s&0x808)?XCAL_BUSY:(s&0x37)?XCAL_DIRTY_STATUS:XCAL_OK;
  assert(led_write830(&bus,8,240)==want);if(want)assert(!writes&&!starts&&!acks&&reads==1);else assert(starts==1&&acks==1&&reads==3);++cases;}
 for(unsigned s=0;s<65536;++s){reset();terminal=(uint16_t)s;int want=(s&0x808)||!(s&0x37)?XCAL_TIMEOUT:(s&0x27)?XCAL_BUS_ERROR:XCAL_OK;
  assert(led_write830(&bus,8,15)==want);assert(starts==1);if(want==XCAL_TIMEOUT)assert(!acks&&reads==4);else assert(acks==1&&reads==3);++cases;}
 for(unsigned s=0;s<65536;++s){reset();final=(uint16_t)s;assert(led_write830(&bus,7,1)==((s&0x83f)?XCAL_FINAL_STATUS:XCAL_OK));assert(starts==1&&acks==1);++cases;}
 for(unsigned ph=0;ph<=11;++ph)for(unsigned er=1;er<=14;++er){reset();assert(led_frame830(&bus,tick,0,ph,er)==0);expect_frame(ph,er);++cases;}
 for(unsigned i=1;i<=53;++i){reset();fail_at=i;assert(led_frame830(&bus,tick,0,11,14)==XCAL_BUS_ERROR);assert(starts==i&&acks==i);++cases;}
 reset();step=0;assert(led_wait830(tick,0,1)==XCAL_TIMEOUT&&tick_calls==10000001);++cases;
 reset();step=0xffffffff;assert(led_wait830(tick,0,1)==XCAL_TIMEOUT&&tick_calls==2);++cases;
 reset();step=3375001;assert(led_wait830(tick,0,1)==XCAL_TIMEOUT&&tick_calls==2);++cases;
 reset();assert(led_frame830(&bus,tick,0,12,1)==XCAL_ARGUMENT&&!writes&&!tick_calls);++cases;
 reset();assert(led_frame830(&bus,tick,0,1,0)==XCAL_ARGUMENT&&!writes&&!tick_calls);++cases;
 reset();assert(led_frame830(&bus,tick,0,1,15)==XCAL_ARGUMENT&&!writes&&!tick_calls);++cases;
 reset();assert(led_write830(&bus,2,1)==XCAL_ARGUMENT&&!writes&&!reads);++cases;
 reset();assert(led_write830(&bus,7,0)==XCAL_ARGUMENT&&!writes&&!reads);++cases;
 reset();assert(led_write830(0,7,1)==XCAL_ARGUMENT&&!writes&&!reads);++cases;
 reset();assert(led_wait830(0,0,1)==XCAL_ARGUMENT&&!tick_calls);++cases;
 reset();assert(led_wait830(tick,0,0)==XCAL_ARGUMENT&&!tick_calls);++cases;
 reset();assert(led_wait830(tick,0,9)==XCAL_ARGUMENT&&!tick_calls);++cases;
 printf("{\"passed\":true,\"cases\":%u,\"all_status_words\":true,\"all_report_codes\":true,\"per_command_fail_stop\":true}\n",cases);
}
