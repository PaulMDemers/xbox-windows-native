#include <assert.h>
#include "suspend.h"
typedef struct{SU619 before,after;int ctx;int s,c,r;} MOCK;
static SU619 susp(void*p){MOCK*m=p;m->s++;return m->before;}
static int ctxt(void*p){MOCK*m=p;m->c++;return m->ctx;}
static SU619 resu(void*p){MOCK*m=p;m->r++;return m->after;}
int main(void){SR619 r;MOCK m={0,1,1,0,0,0};
 assert(sample619(&m,susp,ctxt,resu,&r)&&m.s==1&&m.c==1&&m.r==1&&!r.owned);
 m=(MOCK){~0UL,1,1,0,0,0};assert(!sample619(&m,susp,ctxt,resu,&r)&&m.s==1&&!m.c&&!m.r&&!r.owned);
 m=(MOCK){2,3,1,0,0,0};assert(!sample619(&m,susp,ctxt,resu,&r)&&m.r==1&&!m.c&&!r.owned);
 m=(MOCK){0,1,0,0,0,0};assert(!sample619(&m,susp,ctxt,resu,&r)&&m.c==1&&m.r==1&&!r.owned);
 m=(MOCK){0,~0UL,1,0,0,0};assert(!sample619(&m,susp,ctxt,resu,&r)&&m.r==1&&r.owned);
 m=(MOCK){0,0,1,0,0,0};assert(!sample619(&m,susp,ctxt,resu,&r)&&m.r==1&&r.owned);
 m=(MOCK){0,2,1,0,0,0};assert(!sample619(&m,susp,ctxt,resu,&r)&&m.r==1&&!r.owned);
 return 0;}
