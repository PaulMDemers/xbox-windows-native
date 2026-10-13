/* SPDX-License-Identifier: MIT
 * Windows 2000 per-user outline-drag setting; no driver or mode changes. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>

static void say(const char *s) {
    DWORD n=0, done=0;
    while(s[n])++n;
    WriteFile(GetStdHandle(STD_OUTPUT_HANDLE),s,n,&done,NULL);
}
static BOOL equal(const char *a,const char *b) {
    while(*a&&*a==*b){++a;++b;}return *a==*b;
}
static const char *argument(void) {
    const char *p=GetCommandLineA();BOOL quoted=FALSE;
    if(*p=='"'){quoted=TRUE;++p;}
    while(*p&&((quoted&&*p!='"')||(!quoted&&*p!=' '&&*p!='\t')))++p;
    if(quoted&&*p=='"')++p;
    while(*p==' '||*p=='\t')++p;
    return p;
}
static BOOL get_drag(BOOL *value) {
    return SystemParametersInfoA(SPI_GETDRAGFULLWINDOWS,0,value,0);
}
static BOOL set_drag(BOOL value) {
    BOOL actual=!value;
    if(!SystemParametersInfoA(SPI_SETDRAGFULLWINDOWS,value,NULL,
                             SPIF_UPDATEINIFILE|SPIF_SENDCHANGE))return FALSE;
    return get_drag(&actual)&&actual==value;
}
static BOOL profile_matches(BOOL value) {
    HKEY key;char data[8]={0};DWORD type=0,size=sizeof(data);LONG rc;
    rc=RegOpenKeyExA(HKEY_CURRENT_USER,"Control Panel\\Desktop",0,KEY_QUERY_VALUE,&key);
    if(rc!=ERROR_SUCCESS)return FALSE;
    rc=RegQueryValueExA(key,"DragFullWindows",NULL,&type,(BYTE*)data,&size);
    RegCloseKey(key);
    return rc==ERROR_SUCCESS&&type==REG_SZ&&size>=2&&size<=sizeof(data)&&
           data[0]==(value?'1':'0')&&data[1]==0;
}
void WINAPI mainCRTStartup(void) {
    const char *arg=argument();BOOL old=FALSE,actual=FALSE,want=FALSE;DWORD result=1;
    say("XWN display preferences 372\r\n");
    if(!get_drag(&old)){say("FAIL: cannot query current drag setting.\r\n");goto done;}
    say(old?"BEFORE full\r\n":"BEFORE outline\r\n");
    if(equal(arg,"status")) {
        say(old?"CURRENT full\r\n":"CURRENT outline\r\n");result=0;goto done;
    }
    if(equal(arg,"selftest")) {
        BOOL passed=set_drag(!old)&&profile_matches(!old);
        /* Always try restoration even when the test write/readback fails. */
        BOOL restored=set_drag(old)&&profile_matches(old);
        say(passed&&restored?"SELFTEST PASS; original setting restored.\r\n":
                            "SELFTEST FAIL; inspect current setting.\r\n");
        result=passed&&restored?0:1;goto done;
    }
    if(equal(arg,"outline"))want=FALSE;
    else if(equal(arg,"full"))want=TRUE;
    else {say("Usage: display-settings.exe outline | full | status | selftest\r\n");result=2;goto done;}
    if(!set_drag(want)||!profile_matches(want)||!get_drag(&actual)||actual!=want) {
        say("FAIL: requested setting was not fully verified.\r\n");goto done;
    }
    say(want?"AFTER full\r\n":"AFTER outline\r\n");
    say("PASS: current-user setting and saved profile agree.\r\n");result=0;
done:
    ExitProcess(result);
}
