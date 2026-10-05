/* Emulator-only synthetic WMI-style names; never touches the WMI repository. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <winioctl.h>
#define ROOT "C:\\xwnrotate\\"
static HANDLE Log;
static BYTE Buffer[4096], Extents[16384];
static DWORD Boot, Reuse, Checks;
static void text(const char *s) { DWORD n; WriteFile(Log,s,lstrlenA(s),&n,0); FlushFileBuffers(Log); }
static void number(const char *s,DWORD v) {
 char b[16]; DWORD p=15; b[p]=0; do {b[--p]=(char)('0'+v%10);v/=10;}while(v);
 text(s);text(b+p);text("\r\n");
}
static void require(BOOL ok,const char *s) {
 ++Checks; if(!ok) {DWORD e=GetLastError();text("FAIL: ");text(s);text("\r\n");number("error=",e);CloseHandle(Log);ExitProcess(1);}
}
static BYTE pattern(DWORD offset,DWORD seed) {return (BYTE)((offset*37u)^(offset>>8)^seed);}
static void create(const char *p,DWORD size,DWORD seed) {
 DWORD at=0,n,i,k; HANDLE f=CreateFileA(p,GENERIC_WRITE,0,0,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,0);
 require(f!=INVALID_HANDLE_VALUE,"create");
 while(at<size) {k=size-at;if(k>sizeof(Buffer))k=sizeof(Buffer);for(i=0;i<k;i++)Buffer[i]=pattern(at+i,seed);
 require(WriteFile(f,Buffer,k,&n,0)&&n==k,"write");at+=k;}
 require(FlushFileBuffers(f),"flush");require(CloseHandle(f),"close write");
}
static void verify(const char *p,DWORD size,DWORD seed) {
 DWORD at=0,n,i,k; HANDLE f=CreateFileA(p,GENERIC_READ,FILE_SHARE_READ,0,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,0);
 require(f!=INVALID_HANDLE_VALUE,"open verify");require(GetFileSize(f,0)==size,"size");
 while(at<size) {k=size-at;if(k>sizeof(Buffer))k=sizeof(Buffer);require(ReadFile(f,Buffer,k,&n,0)&&n==k,"read");
 for(i=0;i<k;i++){require(Buffer[i]==pattern(at+i,seed),"data mismatch");}at+=k;}
 require(CloseHandle(f),"close read");
}
static void clusters(const char *p,DWORD *first,DWORD *last) {
 STARTING_VCN_INPUT_BUFFER in; PRETRIEVAL_POINTERS_BUFFER out=(PRETRIEVAL_POINTERS_BUFFER)Extents;
 DWORD n,e; LONGLONG start;HANDLE f=CreateFileA(p,GENERIC_READ,FILE_SHARE_READ,0,OPEN_EXISTING,0,0);
 require(f!=INVALID_HANDLE_VALUE,"open mapping");in.StartingVcn.QuadPart=0;
 require(DeviceIoControl(f,FSCTL_GET_RETRIEVAL_POINTERS,&in,sizeof(in),Extents,sizeof(Extents),&n,0),"retrieval pointers");
 require(out->ExtentCount>0&&out->ExtentCount<1000,"extent bounds");e=out->ExtentCount-1;
 start=e?out->Extents[e-1].NextVcn.QuadPart:out->StartingVcn.QuadPart;
 *first=out->Extents[0].Lcn.LowPart;*last=(DWORD)(out->Extents[e].Lcn.QuadPart+out->Extents[e].NextVcn.QuadPart-start-1);
 require(CloseHandle(f),"close mapping");
}
static void guardname(char *p,DWORD i) {
 lstrcpyA(p,ROOT "guard000.bin");p[18]=(char)('0'+i/100);p[19]=(char)('0'+(i/10)%10);p[20]=(char)('0'+i%10);
}
void WINAPI mainCRTStartup(void) {
 DWORD i,n,oldFirst,oldLast,newFirst,newLast,size,previousSize=0,previousSeed=0;
 DWORD sizes[]={12,65535,65536,65537,131073};char path[80];HANDLE f;BOOL exists;
 Log=CreateFileA("C:\\xwn-rotate.log",GENERIC_WRITE,FILE_SHARE_READ,0,OPEN_ALWAYS,FILE_ATTRIBUTE_NORMAL,0);
 if(Log==INVALID_HANDLE_VALUE){ExitProcess(2);}SetFilePointer(Log,0,0,FILE_END);
 text("ROTATE-BEGIN\r\n");
 f=CreateFileA(ROOT "state.bin",GENERIC_READ,0,0,OPEN_EXISTING,0,0);exists=f!=INVALID_HANDLE_VALUE;
 if(exists){require(ReadFile(f,&Boot,sizeof(Boot),&n,0)&&n==sizeof(Boot),"state read");CloseHandle(f);require(Boot>0&&Boot<10,"state range");}
 else require(GetLastError()==ERROR_PATH_NOT_FOUND||GetLastError()==ERROR_FILE_NOT_FOUND,"state missing");
 number("boot=",Boot+1);
 if(!exists){require(CreateDirectoryA("C:\\xwnrotate",0),"root directory");require(CreateDirectoryA(ROOT "a",0),"directory a");require(CreateDirectoryA(ROOT "b",0),"directory b");}
 for(i=0;i<130;i++){guardname(path,i);if(!exists)create(path,65537,i+123);verify(path,65537,i+123);}
 text("GUARDS-PASS\r\n");
 for(i=0;i<96;i++) {
  DWORD seed=(Boot+1)*1000+i;size=sizes[i%5];
  if(i){verify(ROOT "$WinMgmt.CFG",previousSize,previousSeed);require(MoveFileA(ROOT "$WinMgmt.CFG",ROOT "$WinMgmt.CFG.BAK"),"rotate backup");}
  create(ROOT "a\\new.cfg",size,seed);require(MoveFileA(ROOT "a\\new.cfg",ROOT "$WinMgmt.CFG"),"publish config");verify(ROOT "$WinMgmt.CFG",size,seed);
  if(i){verify(ROOT "$WinMgmt.CFG.BAK",previousSize,previousSeed);require(DeleteFileA(ROOT "$WinMgmt.CFG.BAK"),"delete backup");}
  create(ROOT "a\\CIM.tmp",131073,seed+123);require(MoveFileA(ROOT "a\\CIM.tmp",ROOT "b\\CIM.REP"),"move repository");
  verify(ROOT "b\\CIM.REP",131073,seed+123);require(DeleteFileA(ROOT "b\\CIM.REP"),"delete repository");
  create(ROOT "reuse.old",131073,seed+200);clusters(ROOT "reuse.old",&oldFirst,&oldLast);
  require(DeleteFileA(ROOT "reuse.old"),"delete reuse source");create(ROOT "reuse.new",131073,seed+300);
  clusters(ROOT "reuse.new",&newFirst,&newLast);if(newFirst==oldLast)++Reuse;
  verify(ROOT "reuse.new",131073,seed+300);require(DeleteFileA(ROOT "reuse.new"),"delete reused file");
  previousSize=size;previousSeed=seed;if(i%16==15)number("cycles=",i+1);
 }
 require(DeleteFileA(ROOT "$WinMgmt.CFG"),"delete final config");require(Reuse>0,"observed freed-cluster reuse");
 for(i=0;i<130;i++){guardname(path,i);verify(path,65537,i+123);}
 /* Clear only our known disposable cache-probe files before its next run. */
 if(exists){require(DeleteFileA("C:\\xwn-cache-append.tmp"),"remove prior append");require(DeleteFileA("C:\\xwn-cache-map.tmp"),"remove prior map");require(DeleteFileA("C:\\xwn-cache-pressure.tmp"),"remove prior pressure");}
 ++Boot;f=CreateFileA(ROOT "state.bin",GENERIC_WRITE,0,0,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,0);
 require(f!=INVALID_HANDLE_VALUE,"state open");require(WriteFile(f,&Boot,sizeof(Boot),&n,0)&&n==sizeof(Boot)&&FlushFileBuffers(f),"state write");CloseHandle(f);
 number("reuse=",Reuse);number("checks=",Checks);text("ROTATE-PASS\r\n");CloseHandle(Log);ExitProcess(0);
}
