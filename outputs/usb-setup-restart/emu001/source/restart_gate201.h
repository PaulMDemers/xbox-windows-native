/* Shared guest/host gate: never request restart after a non-idle observation. */
#ifndef XWN_RESTART_GATE_H
#define XWN_RESTART_GATE_H
#include <stdint.h>
typedef uint32_t (*XwnWaitInstall)(void *,uint32_t);
typedef int (*XwnRestart)(void *);
typedef void (*XwnGateRecord)(void *,const char *,uint32_t);
static int xwn_guarded_restart(void *context,XwnWaitInstall wait,XwnRestart restart,XwnGateRecord record) {
    uint32_t status=wait(context,30000);
    record(context,"INSTALL_WAIT_RESULT",status);
    if(status!=0) {
        record(context,status==258?"RESTART_BLOCKED_PENDING_INSTALL":"RESTART_BLOCKED_INSTALL_QUERY",status);
        return status==258?1:2;
    }
    status=wait(context,0);
    record(context,"INSTALL_FINAL_RESULT",status);
    if(status!=0) {
        record(context,status==258?"RESTART_BLOCKED_PENDING_INSTALL":"RESTART_BLOCKED_INSTALL_QUERY",status);
        return status==258?1:2;
    }
    record(context,"NORMAL_RESTART_REQUEST",0);
    if(!restart(context)) {record(context,"FAIL_RESTART",0);return 3;}
    return 0;
}
#endif
