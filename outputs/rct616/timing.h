/* MIT. Bounded timestamp storage; dump only after the subject exits. */
typedef struct {unsigned int kind,id,phase,tick;} STAMP616;
typedef struct {
 unsigned int count,hits[2],first[2],last[2];
 STAMP616 rows[128];
} TIMING616;
static int hit616(TIMING616 *s,unsigned int phase,unsigned int tick){
 if(phase>1||s->hits[phase]>=4096)return 0;
 if(!s->hits[phase])s->first[phase]=tick;
 s->last[phase]=tick;s->hits[phase]++;return 1;
}
static int stamp616(TIMING616 *s,unsigned int kind,unsigned int id,unsigned int phase,unsigned int tick){
 STAMP616 *r;
 if(s->count>=128||kind>1||!id||phase>1)return 0;
 r=&s->rows[s->count++];r->kind=kind;r->id=id;r->phase=phase;r->tick=tick;return 1;
}
