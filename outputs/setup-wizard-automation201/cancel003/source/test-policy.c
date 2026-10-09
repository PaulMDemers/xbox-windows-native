#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "policy.h"
static unsigned Checks;
static void numeric(struct xwn_window201 *w,unsigned i,uint32_t v) {
    switch(i) {case 0:w->pid=v;break;case 1:w->tid=v;break;case 2:w->hwnd=v;break;
    case 3:w->button=v;break;case 4:w->visible=v;break;case 5:w->enabled=v;break;
    case 6:w->button_visible=v;break;case 7:w->button_enabled=v;break;
    case 8:w->button_id=v;break;case 9:w->button_pid=v;break;default:assert(0);}
}
#define CHECK(expr) do {assert(expr);Checks++;}while(0)
int main(void) {
    const char *good="rundll32.exe newdev.dll,DevInstall PCI\\VEN_10DE&DEV_01B0&SUBSYS_00000000&REV_B1\\2&ebb567f&0&28";
    const char *qemu="rundll32.exe newdev.dll,DevInstall PCI\\VEN_1B36&DEV_0005&SUBSYS_00000000&REV_00\\2&ebb567f&0&03";
    char b[512];unsigned i,j;struct xwn_window201 w={100,101,102,103,1,1,1,1,2,100,"Found New Hardware Wizard","#32770","Cancel","Button"};
    CHECK(xwn_target(good,0)==1);CHECK(xwn_target(good,1)==1);CHECK(xwn_target(qemu,1)==5);
    CHECK(xwn_target(qemu,0)==0);CHECK(xwn_target(qemu,2)==0);
    CHECK(xwn_target("rundll32.exe newdev.dll,DevInstallUiOnly 1812",1)==0);
    CHECK(xwn_target("rundll32.exe newdev.dll,DevInstall PCI\\VEN_10DE&DEV_01B0",1)==0);
    CHECK(xwn_target("C:\\WINNT\\system32\\rundll32.exe newdev.dll,DevInstall PCI\\VEN_10DE&DEV_01B0",1)==0);
    for(i=0;i<strlen(good);i++) {
        strcpy(b,good);b[i]=0;CHECK(xwn_target(b,1)==0);
        strcpy(b,good);b[i]='!';CHECK(xwn_target(b,1)==0);
    }
    strcpy(b,good);strcat(b," ");CHECK(xwn_target(b,1)==0);
    strcpy(b,good);strcat(b," malicious");CHECK(xwn_target(b,1)==0);
    strcpy(b,good);for(i=0;b[i];i++)if(b[i]>='a'&&b[i]<='z')b[i]=(char)(b[i]-32);CHECK(xwn_target(b,1)==1);
    memset(b,'a',sizeof(b));CHECK(xwn_target(b,1)==0);
    CHECK(xwn_eligible(&w,100)==1);CHECK(xwn_eligible(&w,0)==0);CHECK(xwn_eligible(&w,99)==0);
    for(i=0;i<10;i++) {
        struct xwn_window201 bad=w;
        for(j=0;j<3;j++) {
            numeric(&bad,i,j==0?0:j==1?0xffffffff:999);
            if(i>=1&&i<=3&&j>0) CHECK(xwn_eligible(&bad,100));
            else CHECK(!xwn_eligible(&bad,100));
        }
    }
    w.title="Found New Hardware";CHECK(!xwn_eligible(&w,100));w.title="Found New Hardware Wizard";
    w.cls="Button";CHECK(!xwn_eligible(&w,100));w.cls="#32770";
    w.button_text="Finish";CHECK(!xwn_eligible(&w,100));w.button_text="Cancel";
    w.button_class="Static";CHECK(!xwn_eligible(&w,100));
    printf("POLICY_CHECKS %u\n",Checks);return 0;
}
