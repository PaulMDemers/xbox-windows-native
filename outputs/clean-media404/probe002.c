/* SPDX-License-Identifier: MIT
 * Private clean-install witness. No driver changes or network traffic.
 */
#define WINVER 0x0500
#define _WIN32_WINNT 0x0500
#include <windows.h>
static DWORD value(const char *sub,const char *name) {
    HKEY key;DWORD v=0xffffffff,type=0,size=sizeof(v);
    if(RegOpenKeyExA(HKEY_LOCAL_MACHINE,sub,0,KEY_QUERY_VALUE,&key)==ERROR_SUCCESS) {
        if(RegQueryValueExA(key,name,0,&type,(BYTE*)&v,&size)!=ERROR_SUCCESS || type!=REG_DWORD) v=0xffffffff;
        RegCloseKey(key);
    }
    return v;
}
void WINAPI mainCRTStartup(void) {
    char self[MAX_PATH],text[1024],vol[128];DWORD wrote,n,serial,flags,maxlen;
    OSVERSIONINFOA os;HANDLE h,token;TOKEN_PRIVILEGES tp;HKEY key;
    BOOL first,copy=TRUE,runonce=TRUE,priv=FALSE,cd;
    DWORD setup=value("SYSTEM\\Setup","SystemSetupInProgress"),kind=value("SYSTEM\\Setup","SetupType");
    { DWORD j; volatile BYTE *z=(volatile BYTE*)&os; for(j=0;j<sizeof(os);j++) z[j]=0; }os.dwOSVersionInfoSize=sizeof(os);GetVersionExA(&os);
    GetModuleFileNameA(0,self,sizeof(self));first=(self[0]=='A'||self[0]=='a');
    cd=GetVolumeInformationA("D:\\",vol,sizeof(vol),&serial,&maxlen,&flags,0,0);
    if(first) {
        copy=CopyFileA(self,"C:\\XWN404.EXE",TRUE);
        runonce=RegCreateKeyExA(HKEY_LOCAL_MACHINE,"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce",0,0,0,KEY_SET_VALUE,0,&key,0)==ERROR_SUCCESS;
        if(runonce) {const char cmd[]="C:\\XWN404.EXE";runonce=RegSetValueExA(key,"XWNCleanMedia404",0,REG_SZ,(const BYTE*)cmd,sizeof(cmd))==ERROR_SUCCESS;RegCloseKey(key);}
    }
    if(OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token)) {
        tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
        if(LookupPrivilegeValueA(0,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid)) {
            SetLastError(ERROR_SUCCESS);priv=AdjustTokenPrivileges(token,FALSE,&tp,0,0,0)&&GetLastError()==ERROR_SUCCESS;
        }
        CloseHandle(token);
    }
    n=wsprintfA(text,"XWN404\r\nphase=%s\r\nversion=%lu.%lu.%lu\r\nsetup_in_progress=%lu\r\nsetup_type=%lu\r\ncopy=%u\r\nrunonce=%u\r\ncd_readable=%u\r\nshutdown_privilege=%u\r\n",
        first?"setup-logon":"disk-only-logon",os.dwMajorVersion,os.dwMinorVersion,os.dwBuildNumber,setup,kind,copy,runonce,cd,priv);
    h=CreateFileA(first?"C:\\XWN404-SETUP.TXT":"C:\\XWN404-BOOT.TXT",GENERIC_WRITE,0,0,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,0);
    if(h==INVALID_HANDLE_VALUE) ExitProcess(90);
    if(!WriteFile(h,text,n,&wrote,0)||wrote!=n||!FlushFileBuffers(h)) {CloseHandle(h);ExitProcess(91);}
    Sleep(5000);
    if(priv&&ExitWindowsEx(EWX_SHUTDOWN|EWX_POWEROFF,0)) {
        const char ok[]="shutdown_api_accepted=1\r\n";
        WriteFile(h,ok,sizeof(ok)-1,&wrote,0);FlushFileBuffers(h);
    }
    CloseHandle(h);ExitProcess(setup==0&&kind==0&&copy&&runonce&&priv?0:92);
}
