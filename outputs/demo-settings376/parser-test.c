#include <assert.h>
typedef int BOOL;
#define FALSE 0
static BOOL equal(const char *a,const char *b) {
    while(*a&&*a==*b){++a;++b;}
    if(*b)return FALSE;
    while(*a==' '||*a=='\t')++a;
    return *a==0;
}
int main(void){
assert(equal("outline","outline")==1);
assert(equal("outline ","outline")==1);
assert(equal("outline\t \t","outline")==1);
assert(equal("full  ","full")==1);
assert(equal("selftest ","selftest")==1);
assert(equal("status\t","status")==1);
assert(equal("outline x","outline")==0);
assert(equal("outlinefull","outline")==0);
assert(equal("out","outline")==0);
assert(equal("Outline","outline")==0);
assert(equal(" outline","outline")==0);
assert(equal("full\n","full")==0);
return 0;}
