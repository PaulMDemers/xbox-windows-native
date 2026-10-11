#ifndef XWN_WIZARD_POLICY201
#define XWN_WIZARD_POLICY201
#include <stdint.h>
static unsigned char xwn_lower(unsigned char c) { return c>='A'&&c<='Z'?(unsigned char)(c+32):c; }
static int xwn_equal(const char *a,const char *b) {
    unsigned i;for(i=0;i<512;i++){if(xwn_lower((unsigned char)a[i])!=xwn_lower((unsigned char)b[i]))return 0;if(!a[i])return 1;}return 0;
}
/* Exact observed command and full instance, never a generic device label/prefix. */
static unsigned xwn_target(const char *command,unsigned emulator) {
    static const char prefix[]="rundll32.exe newdev.dll,DevInstall ";
    static const char *ids[]={
        "PCI\\VEN_10DE&DEV_01B0&SUBSYS_00000000&REV_B1\\2&ebb567f&0&28",
        "PCI\\VEN_10DE&DEV_01B4&SUBSYS_00000000&REV_B1\\2&ebb567f&0&09",
        "PCI\\VEN_10DE&DEV_01C1&SUBSYS_00000000&REV_B1\\2&ebb567f&0&31",
        "USB\\Vid_ffff&Pid_ffff\\5&296d47dc&0&3",
        "PCI\\VEN_1B36&DEV_0005&SUBSYS_00000000&REV_00\\2&ebb567f&0&03",
        "USB\\Vid_045e&Pid_0202\\1-pci.0:02.0-1.3.1"};
    unsigned i,j;
    for(i=0;i<sizeof(prefix)-1;i++)if(!command[i]||xwn_lower((unsigned char)command[i])!=xwn_lower((unsigned char)prefix[i]))return 0;
    for(j=0;j<6;j++)if((j<4||emulator==1)&&xwn_equal(command+i,ids[j]))return j+1;
    return 0;
}
struct xwn_window201 {uint32_t pid,tid,hwnd,button,visible,enabled,button_visible,button_enabled,button_id,button_pid;const char *title,*cls,*button_text,*button_class;};
static int xwn_eligible(const struct xwn_window201 *w,uint32_t pid) {
    return pid&&w->pid==pid&&w->tid&&w->hwnd&&w->button&&w->visible==1&&w->enabled==1&&
        w->button_visible==1&&w->button_enabled==1&&w->button_id==2&&w->button_pid==pid&&
        xwn_equal(w->title,"Found New Hardware Wizard")&&xwn_equal(w->cls,"#32770")&&
        xwn_equal(w->button_text,"Cancel")&&xwn_equal(w->button_class,"Button");
}
#endif
