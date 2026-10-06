/* Diagnostic: finish only the exactly identified successful GPU wizard once. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <tlhelp32.h>
static HANDLE Log,Windows;
static DWORD SampleStart,Count;
static DWORD Installers[32],InstallerCount;
typedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);
static WAIT_INSTALL WaitInstall;
static HWND Candidate,FinishButton,ThisTop,ThisButton;
static DWORD Matches,ThisFlags;
static BOOL FinishAttempted,RestartDeferred;
static DWORD GpuPid,RestartMatches;
static HWND RestartDialog,NoButton,ThisNo;
static BOOL ThisQuestion,ThisYes;
static void write(HANDLE h,const char *s) {
 DWORD n=(DWORD)lstrlenA(s),w;
 if(!WriteFile(h,s,n,&w,NULL)||w!=n)ExitProcess(91);
}
static void record(const char *s,DWORD value) {
 char line[160];wsprintfA(line,"%s %lu\r\n",s,value);write(Log,line);
 if(!FlushFileBuffers(Log))ExitProcess(91);
}
static void fatal(const char *s){record(s,GetLastError());ExitProcess(92);}
/* Controls on this NT5 dialog return LF, while other versions use CRLF.
   Normalize only CR preceding LF; every other byte remains exact. */
static BOOL sameText(const char *a,const char *b){
 while(*a || *b){if(*a=='\r' && a[1]=='\n')a++;if(*b=='\r' && b[1]=='\n')b++;if(*a!=*b)return FALSE;if(!*a)break;a++;b++;}return TRUE;
}
static BOOL budget(void){return Count<256 && GetTickCount()-SampleStart<10000;}
static void describe(HWND h,const char *kind) {
 char text[512],cls[80],line[800];DWORD pid=0,error;DWORD_PTR result=0;LRESULT ok;
 text[0]=cls[0]=0;GetWindowThreadProcessId(h,&pid);GetClassNameA(h,cls,sizeof(cls));
 SetLastError(0);
 ok=SendMessageTimeoutA(h,WM_GETTEXT,sizeof(text),(LPARAM)text,SMTO_ABORTIFHUNG|SMTO_BLOCK,100,&result);
 error=GetLastError();
 text[511]=0;cls[79]=0;
 if(ok && IsWindowVisible(h) && IsWindowEnabled(h)){
  if(sameText(text,"You must restart your computer before the new settings will take effect.\r\n\r\nDo you want to restart your computer now?"))ThisQuestion=TRUE;
  if(!lstrcmpA(cls,"Button") && !lstrcmpA(text,"&No") && GetDlgCtrlID(h)==7 && GetParent(h)==ThisTop)ThisNo=h;
  if(!lstrcmpA(cls,"Button") && !lstrcmpA(text,"&Yes") && GetDlgCtrlID(h)==6 && GetParent(h)==ThisTop)ThisYes=TRUE;
  if(!lstrcmpA(text,"Completing the Found New Hardware Wizard"))ThisFlags|=1;
  if(!lstrcmpA(text,"Xbox NV2A firmware framebuffer (experimental)"))ThisFlags|=2;
  if(sameText(text,"Windows has finished installing the software for this device.\r\n\r\nThe hardware you installed will not work until you restart your computer."))ThisFlags|=4;
  if(!lstrcmpA(text,"To close this wizard, click Finish."))ThisFlags|=8;
  if(!lstrcmpA(cls,"Button") && !lstrcmpA(text,"Finish") && GetDlgCtrlID(h)==12325 && GetParent(h)==ThisTop)ThisButton=h;
 }
 wsprintfA(line,"%s pid=%lu hwnd=%08lx parent=%08lx id=%ld visible=%u enabled=%u ok=%u err=%lu class=%s text=[%s]\r\n",
 kind,pid,(DWORD)h,(DWORD)GetParent(h),(LONG)GetDlgCtrlID(h),IsWindowVisible(h),IsWindowEnabled(h),ok!=0,error,cls,text);
 write(Windows,line);Count++;
}
static BOOL CALLBACK child(HWND h,LPARAM unused) {
 (void)unused;if(!budget())return FALSE;describe(h,"CHILD");return TRUE;
}
static BOOL CALLBACK top(HWND h,LPARAM unused) {
 DWORD pid=0,i;char title[128],cls[80];(void)unused;if(!budget())return FALSE;
 GetWindowThreadProcessId(h,&pid);
 for(i=0;i<InstallerCount;i++)if(pid==Installers[i]){
  ThisTop=h;ThisButton=ThisNo=NULL;ThisFlags=0;ThisQuestion=ThisYes=FALSE;
  describe(h,"TOP");EnumChildWindows(h,child,0);
  GetWindowTextA(h,title,sizeof(title));GetClassNameA(h,cls,sizeof(cls));
  if(ThisFlags==15 && ThisButton && IsWindowVisible(h) && IsWindowEnabled(h) &&
     !lstrcmpA(cls,"#32770") && !lstrcmpA(title,"Found New Hardware Wizard")){
   Candidate=h;FinishButton=ThisButton;Matches++;
  }
  if(FinishAttempted && pid==GpuPid && ThisQuestion && ThisYes && ThisNo && IsWindowVisible(h) && IsWindowEnabled(h) &&
     !lstrcmpA(cls,"#32770") && !lstrcmpA(title,"System Settings Change")){
   RestartDialog=h;NoButton=ThisNo;RestartMatches++;
  }
  break;
 }
 return TRUE;
}
static void sample(DWORD index,DWORD elapsed) {
 HANDLE snap;PROCESSENTRY32 e;char line[400];
 SampleStart=GetTickCount();Count=InstallerCount=Matches=RestartMatches=0;Candidate=FinishButton=RestartDialog=NoButton=NULL;
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
 wsprintfA(line,"PENDING_INSTALL status=%08lx matches=%lu flags=%lu\r\n",WaitInstall(0),Matches,ThisFlags);write(Windows,line);
 if(index>=1 && !FinishAttempted && Matches==1){
  BOOL posted;FinishAttempted=TRUE;GetWindowThreadProcessId(Candidate,&GpuPid);
  /* Normal button notification to the observed parent and control. No error dialog dismissal. */
  posted=PostMessageA(Candidate,WM_COMMAND,MAKEWPARAM(12325,BN_CLICKED),(LPARAM)FinishButton);
  wsprintfA(line,"GPU_FINISH_ONCE dialog=%08lx button=%08lx posted=%u\r\n",(DWORD)Candidate,(DWORD)FinishButton,posted);write(Windows,line);
 }
 if(!RestartDeferred && RestartMatches==1){
  BOOL posted;RestartDeferred=TRUE;
  posted=PostMessageA(RestartDialog,WM_COMMAND,MAKEWPARAM(7,BN_CLICKED),(LPARAM)NoButton);
  wsprintfA(line,"GPU_RESTART_DEFER_ONCE pid=%lu dialog=%08lx button=%08lx posted=%u\r\n",GpuPid,(DWORD)RestartDialog,(DWORD)NoButton,posted);write(Windows,line);
 }
 wsprintfA(line,"SAMPLE_END count=%lu elapsed=%lu budget_exhausted=%u\r\n",Count,GetTickCount()-SampleStart,!budget());write(Windows,line);
 if(!FlushFileBuffers(Windows))fatal("FAIL_FLUSH_WINDOWS");
}
void WINAPI mainCRTStartup(void) {
 DWORD start,i,elapsed,pending;HANDLE token;TOKEN_PRIVILEGES tp;HMODULE setup;
 Log=CreateFileA("C:\\xwnidle\\result.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
 if(Log==INVALID_HANDLE_VALUE)ExitProcess(90);
 Windows=CreateFileA("C:\\xwnidle\\windows.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
 if(Windows==INVALID_HANDLE_VALUE)fatal("FAIL_WINDOWS_LOG");
 setup=LoadLibraryA("setupapi.dll");
 WaitInstall=setup?(WAIT_INSTALL)GetProcAddress(setup,"CMP_WaitNoPendingInstallEvents"):NULL;
 if(!WaitInstall)fatal("FAIL_PENDING_API");
 record("ATTEMPT_ONCE",120000);start=GetTickCount();
 for(i=0;i<5;i++){
  elapsed=GetTickCount()-start;if(elapsed<i*30000)Sleep(i*30000-elapsed);
  sample(i,GetTickCount()-start);
 }
 CloseHandle(Windows);record("IDLE_COMPLETE_MS",GetTickCount()-start);
 pending=WaitInstall(0);
 if(pending!=WAIT_OBJECT_0 || !FinishAttempted || !RestartDeferred){
  record("RESTART_BLOCKED_PENDING_INSTALL",pending);CloseHandle(Log);ExitProcess(93);
 }
 record("INSTALL_QUEUE_IDLE_BEFORE_RESTART",pending);
 if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))fatal("FAIL_TOKEN");
 tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
 if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid))fatal("FAIL_LOOKUP");
 SetLastError(ERROR_SUCCESS);
 if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()!=ERROR_SUCCESS)fatal("FAIL_PRIVILEGE");
 CloseHandle(token);record("NORMAL_RESTART_REQUEST",0);
 if(!ExitWindowsEx(EWX_REBOOT,0))fatal("FAIL_RESTART");
 CloseHandle(Log);ExitProcess(0);
}
