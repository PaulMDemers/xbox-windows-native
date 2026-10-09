#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "text_bounds.h"
static uint32_t seed=117;
static uint32_t rnd(void){seed=seed*1664525u+1013904223u;return seed;}
static int32_t coord(void){return (int32_t)(rnd()%49)-16;}
static int inside(XWT_RECT r,int x,int y){return x>=r.left&&x<r.right&&y>=r.top&&y<r.bottom;}
int main(void)
{
    unsigned n,checks=0;XWT_RECT r,out,g={2,3,5,9},o={-4,1,8,7};
    assert(XwtBounds(1,3,&g,&o,0,&out)==XWT_BOUNDED);
    assert(out.left==-4&&out.top==1&&out.right==8&&out.bottom==9);++checks;
    assert(XwtBounds(0,3,&g,&o,0,&out)==XWT_NO_STRING);++checks;
    assert(XwtBounds(1,3,&g,&o,1,&out)==XWT_EXTRA);++checks;
    r=(XWT_RECT){5,0,2,8};assert(XwtBounds(1,3,&r,NULL,0,&out)==XWT_BAD_STRING);++checks;
    r=(XWT_RECT){2,0,2,8};assert(XwtBounds(1,3,&g,&r,0,&out)==XWT_BAD_OPAQUE);++checks;
    assert(XwtBounds(1,0,&r,NULL,0,&out)==XWT_EMPTY);++checks;
    assert(XwtBounds(1,0,&r,&o,0,&out)==XWT_BOUNDED&&memcmp(&out,&o,sizeof(o))==0);++checks;
    g=(XWT_RECT){INT32_MIN,INT32_MIN,1,1};o=(XWT_RECT){0,0,INT32_MAX,INT32_MAX};
    assert(XwtBounds(1,UINT32_MAX,&g,&o,0,&out)==XWT_BOUNDED);
    assert(out.left==INT32_MIN&&out.top==INT32_MIN&&out.right==INT32_MAX&&out.bottom==INT32_MAX);++checks;
    /* Independent pixel-set oracle, including disjoint opaque area and clip holes.
       Host glyph rectangles are synthetic, not proof of actual NT5 font bounds. */
    for(n=0;n<20000;n++) {
        unsigned glyphs=rnd()%2,opaque=rnd()%2,extra=(n%23==0),has=(n%29!=0);
        int x,y,decision;uint32_t ram[16*16],screen[16*16];
        g=(XWT_RECT){coord(),coord(),coord(),coord()};
        o=(XWT_RECT){coord(),coord(),coord(),coord()};
        XWT_RECT clip={coord(),coord(),coord(),coord()};
        if(n%2) {g.right=g.left+3;g.bottom=g.top+5;o.right=o.left+7;o.bottom=o.top+9;clip=(XWT_RECT){0,0,16,16};}
        decision=XwtBounds(has,glyphs,&g,opaque?&o:NULL,extra,&out);
        for(y=0;y<16;y++)for(x=0;x<16;x++) {
            int at=y*16+x,inclip=inside(clip,x,y)&&!(x>=5&&x<9&&y>=4&&y<10);
            int touched=inclip&&((glyphs&&inside(g,x,y))||(opaque&&inside(o,x,y))||(extra&&x==13&&y==13));
            ram[at]=touched?0xaaff0011u:0x12345678u;screen[at]=0x12345678u;
            if(inclip&&((unsigned)decision>=XWT_NO_STRING||decision==XWT_BOUNDED&&inside(out,x,y)))screen[at]=ram[at];
        }
        assert(memcmp(ram,screen,sizeof(ram))==0);++checks;
    }
    XWT_COPY copied={0,0,0};XWT_STATS stats={0};g=(XWT_RECT){1,2,3,4};
    XwtCopy(&copied,UINT64_C(1)<<40);assert(copied.bytes==(UINT64_C(1)<<40)&&copied.boxes==1&&!copied.overflow);++checks;
    XwtRecord(&stats,1,XWT_BOUNDED,2,&g,&copied);assert(stats.calls==1&&stats.bounded==1&&stats.bytes==copied.bytes&&!stats.overflow);++checks;
    copied.bytes=UINT64_MAX;copied.boxes=UINT32_MAX;XwtCopy(&copied,1);assert(copied.overflow&&copied.bytes==UINT64_MAX&&copied.boxes==UINT32_MAX);++checks;
    XwtRecord(&stats,1,XWT_EMPTY,0,&g,&copied);assert(stats.overflow&&stats.bytes==UINT64_MAX&&stats.boxes==UINT32_MAX);++checks;
    stats.calls=UINT32_MAX;XwtRecord(&stats,0,XWT_EXTRA,0,&g,&copied);assert(stats.overflow&&stats.calls==UINT32_MAX&&stats.fallback==1);++checks;
    printf("CHECKS %u\n",checks);return 0;
}
