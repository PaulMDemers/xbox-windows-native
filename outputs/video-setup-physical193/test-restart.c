/* Exercise actual gate with stale-idle, timeout, query failures and restart failure. */
#include <assert.h>
#include <string.h>
#include "restart_gate.h"
struct State {uint32_t answers[2];unsigned waits,requests,records;int restart_ok;const char *last;};
static uint32_t query(void *p,uint32_t ms) {
    struct State *s=p;assert(s->waits<2);assert(ms==(s->waits?0:30000));return s->answers[s->waits++];
}
static int restart(void *p) {struct State *s=p;s->requests++;return s->restart_ok;}
static void report(void *p,const char *label,uint32_t value) {struct State *s=p;(void)value;s->last=label;s->records++;}
int main(void) {
    const uint32_t inputs[][2]={{0,0},{258,0},{0,258},{0xffffffffu,0},{0,0xffffffffu},{42,0},{0,42}};
    unsigned i;
    for(i=0;i<sizeof(inputs)/sizeof(inputs[0]);i++) {
        struct State s={{inputs[i][0],inputs[i][1]},0,0,0,1,0};
        int result=xwn_guarded_restart(&s,query,restart,report);
        if(!i){assert(result==0&&s.waits==2&&s.requests==1&&s.records==3);}
        else {assert(result!=0&&s.requests==0);assert(s.waits==(inputs[i][0]?1:2));
            assert(strstr(s.last,"RESTART_BLOCKED_")==s.last);}
    }
    {struct State s={{0,0},0,0,0,0,0};assert(xwn_guarded_restart(&s,query,restart,report)==3);
     assert(s.requests==1&&!strcmp(s.last,"FAIL_RESTART"));}
    return 0;
}
