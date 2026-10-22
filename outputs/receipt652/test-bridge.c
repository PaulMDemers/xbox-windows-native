/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "receipt.h"
#include "xwn_hd_adapter.h"
#include "trace649.h"
#include "readback651.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
void xwn652_bridge(struct xwn652_data *,int,unsigned,const struct xwn_hd_request *,
                  const volatile struct xwn_hd_state *,const volatile struct xwn_trace649 *,
                  const volatile struct readback651 *,const volatile struct readback651 *);
int main(int argc,char **argv) {
    struct xwn_hd_request request;struct xwn_hd_state state;
    struct xwn_trace649 trace;struct readback651 pre,post;
    struct xwn652_identity id;struct xwn652_data d;
    uint32_t raw[174];uint8_t blob[1536];unsigned i,j,k,checks=0;FILE *f;
    const uint32_t values[]={0,1,0x80,0xff,0x100,0x200,0x80000000u,0xffffffffu};
    assert(sizeof(request)==32 && sizeof(state)==36 && sizeof(trace)==252 && sizeof(pre)==188);
    assert(sizeof(d)==704);
    for(i=0;i<174;i++)for(j=0;j<sizeof(values)/sizeof(values[0]);j++) {
        memset(raw,0,sizeof(raw));raw[i]=values[j];
        memcpy(&request,raw,32);memcpy(&state,raw+8,36);
        memcpy(&trace,raw+17,252);memcpy(&pre,raw+80,188);memcpy(&post,raw+127,188);
        memset(&d,0xcc,sizeof(d));
        xwn652_bridge(&d,-1,2,&request,&state,&trace,&pre,&post);
        assert(d.result==-1 && d.post_kind==2);
        assert(!memcmp(d.request,raw,32) && !memcmp(d.state,raw+8,36));
        assert(!memcmp(d.trace,raw+17,252) && !memcmp(d.pre,raw+80,188) && !memcmp(d.post,raw+127,188));checks++;
    }
    for(i=0;i<8;i++)raw[i]=0x10000000u+i;
    for(i=0;i<9;i++)raw[8+i]=0x20000000u+i;
    for(i=0;i<63;i++)raw[17+i]=0x30000000u+i;
    for(i=0;i<47;i++){raw[80+i]=0x40000000u+i;raw[127+i]=0x50000000u+i;}
    memcpy(&request,raw,32);memcpy(&state,raw+8,36);memcpy(&trace,raw+17,252);
    memcpy(&pre,raw+80,188);memcpy(&post,raw+127,188);
    xwn652_bridge(&d,-1,2,&request,&state,&trace,&pre,&post);
    for(i=0;i<16;i++)id.attempt[i]=(uint8_t)(i+1);
    for(i=0;i<32;i++)id.candidate_sha256[i]=(uint8_t)(0xa0+i);
    assert(!xwn652_encode(&id,&d,blob));assert(argc==2);f=fopen(argv[1],"wbx");assert(f);
    assert(fwrite(blob,1,1536,f)==1536 && fclose(f)==0);checks++;
    /* Preserve absent/partial capture flags and skipped-IF fields verbatim. */
    for(i=0;i<2;i++)for(j=0;j<2;j++)for(k=0;k<2;k++) {
        pre.captured=i;pre.cr_captured=j;pre.flags_before=pre.flags_after=k?0x202:2;
        post=pre;trace.waits_started=3;trace.waits_completed=2;trace.failed_wait=3;
        xwn652_bridge(&d,1,1,&request,&state,&trace,&pre,&post);
        assert(d.result==1 && d.post_kind==1 && d.pre[0]==i && d.pre[1]==j);
        assert(d.pre[4]==pre.flags_before && d.post[5]==post.flags_after);
        assert(d.trace[0]==3 && d.trace[1]==2 && d.trace[2]==3);checks++;
    }
    printf("{\"passed\":true,\"checks\":%u,\"native_hook_installed\":false}\n",checks);
    return 0;
}
