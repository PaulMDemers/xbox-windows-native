/* Exercise the actual production gate with deterministic monotonic wrap/timing. */
#include <assert.h>
#include <string.h>
#include "setup_gate.h"
struct State {uint32_t now,origin,mode,queries,pending_until;int saw_idle,saw_timeout,saw_error;};
static uint32_t clock_tick(void *p){return ((struct State*)p)->now;}
static uint32_t query(void *p,uint32_t timeout) {
    struct State *s=p;uint32_t elapsed=s->now-s->origin;assert(timeout==0);s->queries++;
    if(s->mode==1)return 258;
    if(s->mode==2)return 0xffffffffu;
    if(s->mode==3&&elapsed==1000)return 258;
    if(s->mode==4){s->now+=10000;return 0;}
    if(s->mode==5&&elapsed>=1000)return 42;
    return elapsed<s->pending_until?258:0;
}
static void pause_poll(void *p,uint32_t ms){struct State *s=p;assert(ms>0&&ms<=250);s->now+=ms;}
static void report(void *p,const char *label,uint32_t value) {
    struct State *s=p;
    if(!strcmp(label,"SETUP_IDLE_OBSERVED_MS")){assert(value>=1000);s->saw_idle++;}
    if(!strcmp(label,"MEASUREMENT_BLOCKED_SETUP_TIMEOUT"))s->saw_timeout++;
    if(!strcmp(label,"MEASUREMENT_BLOCKED_SETUP_QUERY")||!strcmp(label,"FAIL_SETUP_GATE_ARGUMENT"))s->saw_error++;
}
static void run(uint32_t origin,uint32_t mode,uint32_t pending,int expected,uint32_t end) {
    struct State s={origin,origin,mode,0,pending,0,0,0};
    int r=xwn_wait_setup_idle(&s,query,clock_tick,pause_poll,report,5000,1000,250);
    assert(r==expected&&s.now-origin==end);
    assert(s.saw_idle==(r==0)&&s.saw_timeout==(r==1)&&s.saw_error==(r==2));
}
int main(void) {
    unsigned i;
    for(i=0;i<1000;i++) {
        uint32_t start=i&1?0xfffff800u:0;
        run(start,0,0,0,1000);run(start,0,2000,0,3000);
        run(start,0,4250,1,5000);run(start,1,0,1,5000);
        run(start,2,0,2,0);run(start,3,0,0,2250);
        run(start,4,0,1,10000);run(start,5,0,2,1000);
    }
    {struct State s={0,0,0,0,0,0,0,0};
     assert(xwn_wait_setup_idle(&s,query,clock_tick,pause_poll,report,0,1000,250)==2);
     assert(s.queries==0&&s.saw_error==1);}
    /* Actual fifteen-minute/five-second production constants, including wrap. */
    for(i=0;i<10;i++) {
        uint32_t pending[5]={0,600000,894750,895000,900000};
        uint32_t ends[5]={5000,605000,899750,900000,900000};
        uint32_t origin=i>=5?0xfffff800u:0;unsigned at=i%5;
        struct State s={origin,origin,0,0,pending[at],0,0,0};
        int r=xwn_wait_setup_idle(&s,query,clock_tick,pause_poll,report,900000,5000,250);
        assert(r==(at<3?0:1)&&s.now-origin==ends[at]);
        assert(s.saw_idle==(r==0)&&s.saw_timeout==(r==1)&&!s.saw_error);
    }
    return 0;
}
