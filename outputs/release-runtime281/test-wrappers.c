#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include "release.h"
typedef struct{unsigned unused;}NV2AState;
static unsigned compare(unsigned *p,unsigned a,unsigned b){unsigned old=*p;if(old==a)*p=b;return old;}
#define qatomic_cmpxchg(p,a,b) compare(p,a,b)
#define qatomic_fetch_or(p,v) (*(p)|=(v))
#define qatomic_fetch_and(p,v) (*(p)&=(v))
static struct{unsigned busy,transport_error,capture_mask,events;}x269;
static unsigned fail,entered,snapshots;
static bool x269_enter(void){if(fail==5)return false;assert(!x269.busy);x269.busy=1;entered++;return true;}
static bool x269_snapshot(NV2AState*d,unsigned i,unsigned stage){(void)d;assert(stage==2&&x269.busy&&i==snapshots);snapshots++;return fail!=i+1;}
static unsigned pgraph_gl_reuse269_error(void){return x269.transport_error;}
static X279Result x279_release(NV2AState*d,const X279Proof*p){(void)d;(void)p;return(X279Result){X279_REFUSED,0};}
#include "texture-wrappers.c"
int main(void)
{
    unsigned checks=0;NV2AState d={0};
    for(unsigned n=0;n<=5;n++) {
        x281_post_attempted=0; /* Fresh process model, not a runtime reset API. */
        x269=(typeof(x269)){0};fail=n;entered=snapshots=0;
        assert(pgraph_gl_reuse280_post(&d)==(n==0));checks++;
        assert(!x269.busy&&!x269.capture_mask&&!x269.events);checks++;
        assert(snapshots==(n==0?4:n==5?0:n));checks++;
        unsigned prior=snapshots;assert(!pgraph_gl_reuse280_post(&d)&&prior==snapshots);checks++;
        if(n>=1&&n<=4){assert(x269.transport_error==4);checks++;}
    }
    assert(pgraph_gl_release280(&d,NULL).status==X279_REFUSED);checks++;
    printf("PASS %u actual post-snapshot wrapper checks; gate/snapshot/GL/file/helper interfaces modeled; no fake bind/mask and no retry\n",checks);return 0;
}
