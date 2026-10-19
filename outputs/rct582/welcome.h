/* MIT. Close only the cold-verified NT5 Welcome process, never unknown blockers. */
static DWORD welcome_closed;
static HWND welcome_window;
static DWORD welcome_count;
static BOOL welcome_path(DWORD pid,char *path){
 HANDLE h;MODULEENTRY32 m;BOOL ok;
 h=CreateToolhelp32Snapshot(TH32CS_SNAPMODULE,pid);if(h==INVALID_HANDLE_VALUE)return FALSE;
 zero(&m,sizeof(m));m.dwSize=sizeof(m);ok=Module32First(h,&m);
 if(ok)lstrcpyA(path,m.szExePath);
 CloseHandle(h);return ok;
}
static BOOL welcome_identity(HWND w,DWORD *pid){
 char title[200],cls[100],path[MAX_PATH],expected[MAX_PATH];UINT n;
 if(!IsWindowVisible(w)||!GetWindowTextA(w,title,sizeof(title))||lstrcmpA(title,"Getting Started with Windows 2000"))return FALSE;
 if(!GetClassNameA(w,cls,sizeof(cls))||lstrcmpA(cls,"_BerksWin2kWelcomeApp_"))return FALSE;
 GetWindowThreadProcessId(w,pid);if(!welcome_path(*pid,path))return FALSE;
 n=GetWindowsDirectoryA(expected,sizeof(expected));if(!n||n>MAX_PATH-14)return FALSE;
 lstrcatA(expected,"\\welcome.exe");return lstrcmpiA(path,expected)==0;
}
static BOOL CALLBACK welcome_find(HWND w,LPARAM ignored){DWORD pid;(void)ignored;if(welcome_identity(w,&pid)){welcome_window=w;welcome_count++;}return TRUE;}
static void blocker(HWND w){
 char title[200]={0},cls[100]={0},path[MAX_PATH]={0},line[768];DWORD pid=0;
 w=GetAncestor(w,GA_ROOT);GetWindowThreadProcessId(w,&pid);GetWindowTextA(w,title,sizeof(title));GetClassNameA(w,cls,sizeof(cls));welcome_path(pid,path);
 wsprintfA(line,"blocker pid=%lu class=%s module=%s title=%s\r\n",pid,cls,path,title);bytes(logh,line,lstrlenA(line));
}
static BOOL welcome_clear(void){
 DWORD pid=0,again=0,wait;HANDLE process;BOOL posted,gone;
 welcome_window=0;welcome_count=0;EnumWindows(welcome_find,0);
 if(!welcome_count)return TRUE;
 number("welcome_candidates",welcome_count);
 if(welcome_count!=1||welcome_closed>=3||!welcome_identity(welcome_window,&pid))return FALSE;
 blocker(welcome_window);process=OpenProcess(SYNCHRONIZE|PROCESS_QUERY_INFORMATION,FALSE,pid);if(!process)return FALSE;
 if(!welcome_identity(welcome_window,&again)||again!=pid){CloseHandle(process);return FALSE;}
 posted=PostMessageA(welcome_window,WM_CLOSE,0,0);number("welcome_close_posted",posted);
 wait=posted?WaitForSingleObject(process,10000):WAIT_FAILED;gone=!IsWindow(welcome_window);CloseHandle(process);
 number("welcome_wait",wait);number("welcome_window_gone",gone);
 if(!posted||wait!=WAIT_OBJECT_0||!gone)return FALSE;
 welcome_closed++;number("welcome_closed_count",welcome_closed);return TRUE;
}
static BOOL welcome_inject_pc(void){
 char path[MAX_PATH],cmd[MAX_PATH+3];UINT n;STARTUPINFOA si;PROCESS_INFORMATION pi;DWORD start;
 if(GetFileAttributesA("C:\\xwn582-kit\\inject-late-welcome.flag")==INVALID_FILE_ATTRIBUTES)return TRUE;
 n=GetWindowsDirectoryA(path,sizeof(path));if(!n||n>MAX_PATH-14)return FALSE;lstrcatA(path,"\\welcome.exe");
 wsprintfA(cmd,"\"%s\"",path);zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);
 if(!CreateProcessA(path,cmd,0,0,FALSE,0,0,0,&si,&pi))return FALSE;
 number("pc_welcome_injected_pid",pi.dwProcessId);CloseHandle(pi.hThread);CloseHandle(pi.hProcess);
 start=GetTickCount();do{welcome_count=0;EnumWindows(welcome_find,0);if(welcome_count==1)return TRUE;Sleep(100);}while(GetTickCount()-start<10000);
 number("pc_welcome_injection_timeout",1);return FALSE;
}
