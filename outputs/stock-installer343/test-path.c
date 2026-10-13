#include <assert.h>
#include <stdio.h>
#include "report-path.h"
int main(void){
    const char input[]="\\Device\\Harddisk0\\Partition1\\Applications\\XWNECap0123abcd\\default.xbe";
    const char expected[]="\\Device\\Harddisk0\\Partition1\\Applications\\XWNECap0123abcd\\capacity.txt";
    char out[256],bad[sizeof(input)];unsigned cases=0;
    memset(out,0x55,sizeof(out));assert(xwn343_report_path(input,sizeof(input)-1,out,sizeof(out)));assert(!strcmp(out,expected));cases++;
    for(size_t n=0;n<sizeof(input)+5;n++){if(n==sizeof(input)-1)continue;memset(out,0x55,sizeof(out));assert(!xwn343_report_path(input,n,out,sizeof(out)));assert(out[0]==0x55);cases++;}
    for(size_t n=0;n<sizeof(expected);n++){memset(out,0x55,sizeof(out));assert(!xwn343_report_path(input,sizeof(input)-1,out,n));assert(out[0]==0x55);cases++;}
    for(size_t i=0;i<sizeof(input)-1;i++){memcpy(bad,input,sizeof(input));bad[i]='?';memset(out,0x55,sizeof(out));assert(!xwn343_report_path(bad,sizeof(input)-1,out,sizeof(out)));assert(out[0]==0x55);cases++;}
    assert(!xwn343_report_path(NULL,0,out,sizeof(out)));cases++;
    printf("PASS %u path length/namespace/output-preservation checks\n",cases);return 0;
}
