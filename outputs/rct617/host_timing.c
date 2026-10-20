/* MIT. Boundary checks for the exact target timestamp storage. */
#include <assert.h>
#include <string.h>
#include "timing.h"
int main(void){
 TIMING617 t,old;unsigned int i;memset(&t,0,sizeof(t));
 for(i=0;i<128;i++)assert(stamp617(&t,i&1,i+1,i/64,i));
 old=t;assert(!stamp617(&t,0,129,1,200));assert(!memcmp(&old,&t,sizeof(t)));
 memset(&t,0,sizeof(t));
 assert(!stamp617(&t,2,1,0,0));assert(!stamp617(&t,0,0,0,0));assert(!stamp617(&t,0,1,2,0));
 assert(!hit617(&t,2,0));
 for(i=0;i<4096;i++)assert(hit617(&t,1,100+i));
 assert(t.hits[1]==4096&&t.first[1]==100&&t.last[1]==4195);
 old=t;assert(!hit617(&t,1,5000));assert(!memcmp(&old,&t,sizeof(t)));
 return 0;
}
