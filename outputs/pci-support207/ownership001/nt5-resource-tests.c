#define _WIN32_WINNT 0x0500
#include <windows.h>
#include "resource-tests.h"
static void number(HANDLE f,unsigned n)
{
    char buf[16];unsigned i=14;DWORD done;buf[15]='\n';
    do{buf[i--]=(char)('0'+n%10);n/=10;}while(n);
    WriteFile(f,buf+i+1,15-i,&done,NULL);
}
void WINAPI mainCRTStartup(void)
{
    DWORD done;int line;HANDLE f;
    f=CreateFileA("C:\\xwnpciown1\\resources.log",GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(f==INVALID_HANDLE_VALUE)ExitProcess(2);
    line=run_tests();
    WriteFile(f,"RESOURCE_POLICY_TESTS\r\nCASES ",sizeof("RESOURCE_POLICY_TESTS\r\nCASES ")-1,&done,NULL);number(f,cases);
    WriteFile(f,"FAILURE_LINE ",sizeof("FAILURE_LINE ")-1,&done,NULL);number(f,(unsigned)line);
    if(!line)WriteFile(f,"PASS_NO_HARDWARE_IO\r\n",sizeof("PASS_NO_HARDWARE_IO\r\n")-1,&done,NULL);
    FlushFileBuffers(f);CloseHandle(f);ExitProcess(line ? 1 : 0);
}
