/* Exercise only the experimental Xbox Ethernet device in the private guest. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <setupapi.h>
static HANDLE Log;
static void line(const char *s){DWORD n;WriteFile(Log,s,lstrlenA(s),&n,NULL);FlushFileBuffers(Log);}
static void number(const char *s,DWORD v){char b[16];unsigned n=sizeof(b);b[--n]=0;b[--n]='\n';b[--n]='\r';do{b[--n]='0'+v%10;v/=10;}while(v);line(s);line(b+n);}
static BOOL match(const char *s){const char *p="PCI\\VEN_10DE&DEV_01C3";while(*p){char c=*s++;if(c>='a'&&c<='z')c-=32;if(c!=*p++)return FALSE;}return *s==0||*s=='&';}
static BOOL change(HDEVINFO set,SP_DEVINFO_DATA *info,DWORD state){SP_PROPCHANGE_PARAMS p;p.ClassInstallHeader.cbSize=sizeof(SP_CLASSINSTALL_HEADER);p.ClassInstallHeader.InstallFunction=DIF_PROPERTYCHANGE;p.StateChange=state;p.Scope=DICS_FLAG_GLOBAL;p.HwProfile=0;return SetupDiSetClassInstallParamsA(set,info,&p.ClassInstallHeader,sizeof(p))&&SetupDiCallClassInstaller(DIF_PROPERTYCHANGE,set,info);}
void WINAPI mainCRTStartup(void){HDEVINFO set;SP_DEVINFO_DATA info;DWORD i,type,required,cycle,status=1;char ids[2048];BOOL found=FALSE;
 Log=CreateFileA("C:\\xwn-cycle.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
 set=SetupDiGetClassDevsA(NULL,"PCI",NULL,DIGCF_PRESENT|DIGCF_ALLCLASSES);if(set==INVALID_HANDLE_VALUE){number("Enumerate error: ",GetLastError());ExitProcess(3);}
 for(i=0;;++i){info.cbSize=sizeof(info);if(!SetupDiEnumDeviceInfo(set,i,&info))break;
  if(!SetupDiGetDeviceRegistryPropertyA(set,&info,SPDRP_HARDWAREID,&type,(PBYTE)ids,sizeof(ids),&required)||type!=REG_MULTI_SZ)continue;
  if(!match(ids))continue;found=TRUE;line("Matched Xbox PCI 10DE:01C3\r\n");
  for(cycle=1;cycle<=3;++cycle){number("Cycle: ",cycle);
   if(!change(set,&info,DICS_DISABLE)){number("Disable error: ",GetLastError());goto done;}line("Disable succeeded\r\n");Sleep(5000);
   if(!change(set,&info,DICS_ENABLE)){number("Enable error: ",GetLastError());goto done;}line("Enable succeeded\r\n");Sleep(10000);
  }line("Three cycles completed\r\n");status=0;break;
 }
 done:if(!found)line("Target device missing\r\n");number("Exit status: ",status);SetupDiDestroyDeviceInfoList(set);CloseHandle(Log);ExitProcess(status);
}
