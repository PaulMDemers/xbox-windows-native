#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "lifetime.h"
int main(void) {
 LM610 m[3]={{0x62000000,0x10000,1,1},{0x70000000,0x10000,2,1},{0}};
 LB610 b[3]={{0x62001020,0,0,1,0x90,0,0,0},{0x70001000,2,0,2,0x55,1,1,0},{0}};
 LM610 keepm[3];LB610 keepb[3];unsigned int n=0;
#define REJECT(expr) do {memcpy(keepm,m,sizeof(m));memcpy(keepb,b,sizeof(b));assert(!(expr));assert(!memcmp(m,keepm,sizeof(m))&&!memcmp(b,keepb,sizeof(b)));n++;}while(0)
 assert(load610(m,2,0x63000000,0x10000));
 REJECT(load610(m,2,0x61fff000,0x2000));
 REJECT(load610(m,2,0x62000010,0x100));
 REJECT(load610(m,2,0x61000000,0x2000000));
 REJECT(load610(m,256,0x63000000,0x10000));
 REJECT(load610(m,2,0xfffff000,0x2000));
 REJECT(load610(m,2,0x63000000,0));
 REJECT(load610(m,2,0,0x1000));
 assert(retire610(m,2,b,2,0x62000000,0,0,0)==1);
 REJECT(retire610(m,2,b,2,0x62000000,1,0,0));
 REJECT(retire610(m,2,b,2,0x62000000,0,1,0));
 REJECT(retire610(m,2,b,2,0x62000000,0,0,1));
 REJECT(retire610(m,2,b,2,0x63000000,0,0,0));
 b[0].api=1;REJECT(retire610(m,2,b,2,m[0].base,0,0,0));b[0].api=0;
 b[0].refs=1;REJECT(retire610(m,2,b,2,m[0].base,0,0,0));b[0].refs=0;
 b[0].enabled=1;REJECT(retire610(m,2,b,2,m[0].base,0,0,0));b[0].enabled=0;
 b[0].armed=1;REJECT(retire610(m,2,b,2,m[0].base,0,0,0));b[0].armed=0;
 b[0].generation=2;REJECT(retire610(m,2,b,2,m[0].base,0,0,0));b[0].generation=1;
 b[0].address=0x63000000;REJECT(retire610(m,2,b,2,m[0].base,0,0,0));b[0].address=0x62001020;
 m[2]=m[0];REJECT(retire610(m,3,b,2,m[0].base,0,0,0));m[2].active=0;
 b[0].retired=1;m[0].active=0;
 REJECT(retire610(m,2,b,2,m[0].base,0,0,0));
 assert(load610(m,2,0x62000000,0x10000));
 m[2].active=1;m[2].generation=3;
 b[2]=b[0];b[2].retired=0;b[2].generation=3;b[2].original=0xf8;
 assert(retire610(m,3,b,3,0x62000000,0,0,0)==3);
 assert(b[0].original==0x90&&b[2].original==0xf8);
 printf("LIFETIME610 PASS: 2 generations, %u read-only rejection checks\n",n);
 return 0;
}
