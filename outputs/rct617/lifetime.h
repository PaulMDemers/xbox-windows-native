/* MIT. Read-only admission: callers mutate only after complete validation. */
#ifndef LIFETIME610_H
#define LIFETIME610_H
typedef unsigned int LU610;
typedef struct {LU610 base,size,generation;int active;} LM610;
typedef struct {
 LU610 address,api,refs,generation;unsigned char original;
 int armed,enabled,retired;
} LB610;
static int load610(const LM610 *m,LU610 count,LU610 base,LU610 size) {
 LU610 i;
 if(count>=256||!base||!size||base>0xffffffffu-size)return 0;
 for(i=0;i<count;i++)if(m[i].active&&base<m[i].base+m[i].size&&m[i].base<base+size)return 0;
 return 1;
}
static LU610 retire610(const LM610 *m,LU610 mc,const LB610 *b,LU610 bc,
 LU610 base,LU610 pending,LU610 step,LU610 held) {
 LU610 i,j,found=0;
 if(mc>256||bc>256||pending||step||held)return 0;
 for(i=0;i<mc;i++)if(m[i].active&&m[i].base==base) {
  if(found||!m[i].generation||!m[i].size||base>0xffffffffu-m[i].size)return 0;
  found=i+1;
 }
 if(!found)return 0;
 i=found-1;
 for(j=0;j<bc;j++)if(!b[j].retired) {
  int inside=b[j].address>=base&&b[j].address-base<m[i].size;
  if((b[j].generation==m[i].generation)!=inside)return 0;
  if(inside&&(b[j].api||b[j].refs||b[j].enabled||b[j].armed))return 0;
 }
 return found;
}
#endif
