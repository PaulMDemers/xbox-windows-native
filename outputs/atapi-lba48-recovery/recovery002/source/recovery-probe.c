#define _WIN32_WINNT 0x0500
#include <windows.h>
static HANDLE Log;
static BYTE Buffer[65536];
static char Path[MAX_PATH], Text[MAX_PATH+64];
static void line(const char *s)
{
    DWORD n=lstrlenA(s),written;
    if(!WriteFile(Log,s,n,&written,NULL)||written!=n||!FlushFileBuffers(Log))ExitProcess(92);
}
static BOOL matches(const char *path)
{
    HANDLE f;DWORD size,n,*words=(DWORD*)Buffer;
    f=CreateFileA(path,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);
    if(f==INVALID_HANDLE_VALUE)return FALSE;
    size=GetFileSize(f,NULL);
    if(size!=sizeof(Buffer)||!ReadFile(f,Buffer,sizeof(Buffer),&n,NULL)||n!=sizeof(Buffer)){
        CloseHandle(f);return FALSE;
    }
    CloseHandle(f);
    if(words[0]!=0x45474150||words[1]!=0x504d5544||words[10]!=0xe058d103||
       words[11]!=0x44554d50||words[12]!=0x103||words[13]!=0x10000||words[14]!=1)return FALSE;
    wsprintfA(Text,"DUMP_FILE %s\r\n",path);line(Text);line("DUMP_BYTES 65536\r\n");return TRUE;
}
void __stdcall mainCRTStartup(void)
{
    DWORD start=GetTickCount(),count;BOOL found=FALSE;HANDLE search,token,volume;
    WIN32_FIND_DATAA info;TOKEN_PRIVILEGES tp;
    Log=CreateFileA("C:\\xwnrecover105\\result.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,
                    FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,NULL);
    if(Log==INVALID_HANDLE_VALUE)ExitProcess(90);
    line("RECOVERY_ONCE E058D103 44554D50 00000103 00010000 00000001\r\n");
    while(GetTickCount()-start<120000&&!found){
        search=FindFirstFileA("C:\\WINNT\\Minidump\\*.dmp",&info);
        if(search!=INVALID_HANDLE_VALUE){
            count=0;
            do{
                if(++count>256){line("FAIL_TOO_MANY_DUMPS\r\n");break;}
                if(info.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY)continue;
                if(lstrlenA(info.cFileName)>MAX_PATH-24)continue;
                wsprintfA(Path,"C:\\WINNT\\Minidump\\%s",info.cFileName);
                if(matches(Path)){found=TRUE;break;}
            }while(FindNextFileA(search,&info));
            FindClose(search);
        }
        if(!found)found=matches("C:\\WINNT\\MEMORY.DMP");
        if(!found)Sleep(1000);
    }
    line(found?"RECOVERY_FILE_FOUND\r\n":"FAIL_NO_MATCHING_RECOVERED_DUMP\r\n");
    Sleep(5000);
    volume=CreateFileA("\\\\.\\C:",GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);
    if(volume==INVALID_HANDLE_VALUE||!FlushFileBuffers(volume)){line("FAIL_FLUSH\r\n");ExitProcess(93);}
    CloseHandle(volume);
    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token)){line("FAIL_TOKEN\r\n");ExitProcess(94);}
    tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
    if(!LookupPrivilegeValueA(NULL,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid)){line("FAIL_LOOKUP\r\n");ExitProcess(95);}
    SetLastError(ERROR_SUCCESS);
    if(!AdjustTokenPrivileges(token,FALSE,&tp,0,NULL,NULL)||GetLastError()!=ERROR_SUCCESS){line("FAIL_PRIVILEGE\r\n");ExitProcess(96);}
    CloseHandle(token);line("NORMAL_RESTART_REQUEST\r\n");
    if(!ExitWindowsEx(EWX_REBOOT,0)){line("FAIL_RESTART\r\n");ExitProcess(97);}
    CloseHandle(Log);ExitProcess(found?0:91);
}
