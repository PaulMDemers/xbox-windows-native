#ifndef XWN_ACTIVATION313
#define XWN_ACTIVATION313
#include <stdint.h>
struct x313_gui { uint32_t ok,active,flags,capture,menu,move; };
struct x313_state {
    uint32_t enabled,mode,emulator,pid,lo,hi,hwnd,tid,fg,fgpid,fgtid;
    struct x313_gui target,foreground;
};
struct x313_ticket { uint32_t pid,lo,hi; };
struct x313_budget { uint32_t count; struct x313_ticket owners[8]; };
static int x313_gui_clear(struct x313_gui g,uint32_t h) {
    return g.ok==1 && h && g.active==h && !(g.flags&~1u) && !g.capture && !g.menu && !g.move;
}
/* GUI_CARETBLINKING is the only permitted flag. No menu/move/capture/unknown state. */
static int x313_admit(const struct x313_state *s) {
    return s->enabled==1 && s->mode==1 && s->emulator==1 && s->pid && (s->lo||s->hi) &&
      s->hwnd && s->tid && s->fg && s->fg!=s->hwnd && s->fgpid && s->fgtid &&
      x313_gui_clear(s->target,s->hwnd) && x313_gui_clear(s->foreground,s->fg);
}
static int x313_same(const struct x313_state *a,const struct x313_state *b) {
    return x313_admit(a)&&x313_admit(b)&&a->pid==b->pid&&a->lo==b->lo&&a->hi==b->hi&&
      a->hwnd==b->hwnd&&a->tid==b->tid&&a->fg==b->fg&&a->fgpid==b->fgpid&&a->fgtid==b->fgtid;
}
/* Reserve before durable logging/API call; a failed call never returns its ticket. */
static int x313_reserve(struct x313_budget *b,const struct x313_state *s) {
    uint32_t i;
    if(!x313_admit(s)||b->count>=8)return 0;
    for(i=0;i<b->count;i++)if(b->owners[i].pid==s->pid&&b->owners[i].lo==s->lo&&b->owners[i].hi==s->hi)return 0;
    b->owners[b->count].pid=s->pid;b->owners[b->count].lo=s->lo;b->owners[b->count].hi=s->hi;b->count++;
    return 1;
}
#endif
