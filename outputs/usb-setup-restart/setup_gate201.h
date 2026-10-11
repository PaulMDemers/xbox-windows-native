/* Bounded observational gate. No installation, UI action or fabricated idle. */
#ifndef XWN_SETUP_GATE_H
#define XWN_SETUP_GATE_H
#include <stdint.h>
typedef uint32_t (*XwnSetupQuery)(void *,uint32_t);
typedef uint32_t (*XwnSetupClock)(void *);
typedef void (*XwnSetupSleep)(void *,uint32_t);
typedef void (*XwnSetupRecord)(void *,const char *,uint32_t);
static int xwn_wait_setup_idle(void *context,XwnSetupQuery query,XwnSetupClock clock,
    XwnSetupSleep pause,XwnSetupRecord record,uint32_t budget,uint32_t stable,uint32_t interval) {
    uint32_t start=clock(context),idle=0,last=0;int have_idle=0,have_last=0;
    if(!budget||budget>=0x80000000u||!stable||stable>=budget||!interval||interval>stable) {
        record(context,"FAIL_SETUP_GATE_ARGUMENT",0);return 2;
    }
    for(;;) {
        uint32_t now=clock(context),status,elapsed=now-start;
        if(elapsed>=budget) {record(context,"MEASUREMENT_BLOCKED_SETUP_TIMEOUT",elapsed);return 1;}
        status=query(context,0);
        if(!have_last||status!=last) {record(context,"INSTALL_PREFLIGHT_RESULT",status);last=status;have_last=1;}
        now=clock(context);elapsed=now-start;
        if(status!=0&&status!=258) {record(context,"MEASUREMENT_BLOCKED_SETUP_QUERY",status);return 2;}
        if(elapsed>=budget) {record(context,"MEASUREMENT_BLOCKED_SETUP_TIMEOUT",elapsed);return 1;}
        if(status==258)have_idle=0;
        else {
            if(!have_idle){idle=now;have_idle=1;}
            if(now-idle>=stable) {
                record(context,"SETUP_IDLE_OBSERVED_MS",now-idle);
                record(context,"SETUP_WAIT_ELAPSED_MS",elapsed);return 0;
            }
        }
        pause(context,interval<budget-elapsed?interval:budget-elapsed);
    }
}
#endif
