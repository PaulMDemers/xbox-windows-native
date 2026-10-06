/* Owned NT5 observer: read captions/controls, never activate or dismiss a dialog. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <tlhelp32.h>
static HANDLE Log,Windows;
static DWORD SampleStart,Count;
static DWORD Installers[32],InstallerCount;
static void write(HANDLE h,const char *s) {
 DWORD n=(DWORD)lstrlenA(s),w;
 if(!WriteFile(h,s,n,&w,NULL)||w!=n)ExitProcess(91);
}
static void record(const char *s,DWORD value) {
 char line[160];wsprintfA(line,"%s %lu\r\n",s,value);write(Log,line);
 if(!FlushFileBuffers(Log))ExitProcess(91);
}
static void fatal(const char *s){record(s,GetLastError());ExitProcess(92);}
static BOOL budget(void){return Count<256 && GetTickCount()-SampleStart<10000;}
static void describe(HWND h,const char *kind) {
 char text[512],cls[80],line[800];DWORD pid=0,error;DWORD_PTR result=0;LRESULT ok;
 text[0]=cls[0]=0;GetWindowThreadProcessId(h,&pid);GetClassNameA(h,cls,sizeof(cls));
 SetLastError(0);
 ok=SendMessageTimeoutA(h,WM_GETTEXT,sizeof(text),(LPARAM)text,SMTO_ABORTIFHUNG|SMTO_BLOCK,100,&result);
 error=GetLastError();
 text[511]=0;cls[79]=0;
 wsprintfA(line,"%s pid=%lu hwnd=%08lx parent=%08lx id=%ld visible=%u enabled=%u ok=%u err=%lu class=%s text=[%s]\r\n",
 kind,pid,(DWORD)h,(DWORD)GetParent(h),(LONG)GetDlgCtrlID(h),IsWindowVisible(h),IsWindowEnabled(h),ok!=0,error,cls,text);
 write(Windows,line);Count++;
}
static BOOL CALLBACK child(HWND h,LPARAM unused) {
 (void)unused;if(!budget())return FALSE;describe(h,"CHILD");return TRUE;
}
static BOOL CALLBACK top(HWND h,LPARAM unused) {
 DWORD pid=0,i;(void)unused;if(!budget())return FALSE;
 GetWindowThreadProcessId(h,&pid);
 for(i=0;i<InstallerCount;i++)if(pid==Installers[i]){
  describe(h,"TOP");EnumChildWindows(h,child,0);break;
 }
 return TRUE;
}
static void sample(DWORD index,DWORD elapsed) {
 HANDLE snap;PROCESSENTRY32 e;char line[400];
 SampleStart=GetTickCount();Count=InstallerCount=0;
 wsprintfA(line,"SAMPLE %lu elapsed=%lu\r\n",index,elapsed);write(Windows,line);
 snap=CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS,0);
 if(snap==INVALID_HANDLE_VALUE)fatal("FAIL_SNAPSHOT");
 e.dwSize=sizeof(e);
 if(Process32First(snap,&e))do {
  if(!lstrcmpiA(e.szExeFile,"rundll32.exe")){
   wsprintfA(line,"INSTALLER pid=%lu parent=%lu image=%s\r\n",e.th32ProcessID,e.th32ParentProcessID,e.szExeFile);write(Windows,line);
   if(InstallerCount<32)Installers[InstallerCount++]=e.th32ProcessID;
  }
 }while(Process32Next(snap,&e));
 CloseHandle(snap);EnumWindows(top,0);
 wsprintfA(line,"SAMPLE_END count=%lu elapsed=%lu budget_exhausted=%u\r\n",Count,GetTickCount()-SampleStart,!budget());write(Windows,line);
 if(!FlushFileBuffers(Windows))fatal("FAIL_FLUSH_WINDOWS");
}
void WINAPI mainCRTStartup(void) {
 DWORD start,i,elapsed;HANDLE token;TOKEN_PRIVILEGES tp;
 Log=CreateFileA("C:\\xwnidle\\result.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
 if(Log==INVALID_HANDLE_VALUE)ExitProcess(90);
 Windows=CreateFileA("C:\\xwnidle\\windows.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
 if(Windows==INVALID_HANDLE_VALUE)fatal("FAIL_WINDOWS_LOG");
 record("ATTEMPT_ONCE",120000);start=GetTickCount();
 for(i=0;i<5;i++){
  elapsed=GetTickCount()-start;if(elapsed<i*30000)Sleep(i*30000-elapsed);
  sample(i,GetTickCount()-start);
 }
 CloseHandle(Windows);record("IDLE_COMPLETE_MS",GetTickCount()-start);
 if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))fatal("FAIL_TOKEN");
 tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
 if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))fatal("FAIL_LOOKUP");
 SetLastError(ERROR_SUCCESS);
 if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()!=ERROR_SUCCESS)fatal("FAIL_PRIVILEGE");
 CloseHandle(token);record("NORMAL_RESTART_REQUEST",0);
 if(!ExitWindowsEx(EWX_REBOOT,0))fatal("FAIL_RESTART");
 CloseHandle(Log);ExitProcess(0);
}
