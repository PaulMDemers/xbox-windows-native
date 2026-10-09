#ifndef XWN_READY201_H
#define XWN_READY201_H
#include <stdint.h>
struct xwn_ready201 {uint32_t pid,lo,hi,hwnd,since;int present;};
static void xwn_ready_reset(struct xwn_ready201 *r) {r->present=0;}
static int xwn_ready_hold(struct xwn_ready201 *r,int verified,uint32_t pid,uint32_t lo,uint32_t hi,uint32_t hwnd,uint32_t now) {
 if(!verified){xwn_ready_reset(r);return 0;}
 if(!r->present||r->pid!=pid||r->lo!=lo||r->hi!=hi||r->hwnd!=hwnd){r->pid=pid;r->lo=lo;r->hi=hi;r->hwnd=hwnd;r->since=now;r->present=1;return 0;}
 return (uint32_t)(now-r->since)>=5000;
}
#endif
