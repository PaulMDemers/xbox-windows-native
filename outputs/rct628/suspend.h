/* MIT. Balance exactly the suspension acquired by this probe. */
typedef unsigned long SU619;
typedef struct {SU619 prior,resumed;int context_ok,owned;} SR619;
typedef SU619 (*SUSP619)(void*);
typedef int (*CTX619)(void*);
static int sample619(void *p,SUSP619 suspend,CTX619 context,SUSP619 resume,SR619*r){
 r->prior=~0UL;r->resumed=~0UL;r->context_ok=0;r->owned=0;
 r->prior=suspend(p);if(r->prior==~0UL)return 0;
 r->owned=1;
 if(r->prior==0)r->context_ok=context(p);
 r->resumed=resume(p);
 if(r->resumed!=~0UL&&r->resumed>0)r->owned=0;
 return r->prior==0&&r->context_ok&&r->resumed==1&&!r->owned;
}
