/* MIT. Bounded timestamp storage; dump only after the subject exits. */
typedef struct {unsigned int kind,id,phase,tick;} STAMP617;
typedef struct {
 unsigned int count,hits[2],first[2],last[2];
 STAMP617 rows[128];
 unsigned int hit_ticks[2][4096];
} TIMING617;
static int hit617(TIMING617 *s,unsigned int phase,unsigned int tick){
 if(phase>1||s->hits[phase]>=4096)return 0;
 if(!s->hits[phase])s->first[phase]=tick;
 s->last[phase]=tick;s->hit_ticks[phase][s->hits[phase]]=tick;s->hits[phase]++;return 1;
}
static int stamp617(TIMING617 *s,unsigned int kind,unsigned int id,unsigned int phase,unsigned int tick){
 STAMP617 *r;
 if(s->count>=128||kind>1||!id||phase>1)return 0;
 r=&s->rows[s->count++];r->kind=kind;r->id=id;r->phase=phase;r->tick=tick;return 1;
}
