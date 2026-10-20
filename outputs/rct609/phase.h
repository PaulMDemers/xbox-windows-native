/* MIT. One latched phase transition, deferred until recorded calls drain. */
typedef struct {unsigned int phase,deferred;} PHASE605;
/* 0 unchanged/duplicate,1 deferred,2 committed,-1 malformed state/input. */
static int phase605(PHASE605*s,unsigned int requested,unsigned int pending) {
 if(s->phase>1||s->deferred>1||requested>1)return -1;
 if(!requested||s->phase==1)return 0;
 if(pending){s->deferred=1;return 1;}
 s->phase=1;return 2;
}
