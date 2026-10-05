/* Emulator-only replacement/lifetime test. Leaves deterministic files for cold audit. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <winioctl.h>
#define ROOT "C:\\xwnlife\\"
static HANDLE Log;
static BYTE Buffer[4096], Extents[16384];
static DWORD Reuse, Checks;
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
static void named(char *p,const char *kind,DWORD i) {
 lstrcpyA(p,ROOT);lstrcatA(p,kind);lstrcatA(p,"00.bin");
 {DWORD at=lstrlenA(p)-6;p[at]=(char)('0'+i/10);p[at+1]=(char)('0'+i%10);}
}
static HANDLE dirty(const char *p,DWORD seed) {
 DWORD at,n,i;HANDLE f=CreateFileA(p,GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE,0,CREATE_NEW,0,0);
 require(f!=INVALID_HANDLE_VALUE,"create dirty");
 for(at=0;at<131073;) {DWORD count=131073-at;if(count>4096)count=4096;
 for(i=0;i<count;i++)Buffer[i]=pattern(at+i,seed);
 require(WriteFile(f,Buffer,count,&n,0)&&n==count,"dirty write");at+=count;}
 return f; /* Deliberately no explicit flush. */
}
static void denial(BOOL ok,const char *where) {
 DWORD error=GetLastError();require(!ok,where);number("expected denial=",error);
 require(error==ERROR_ACCESS_DENIED||error==ERROR_SHARING_VIOLATION||error==ERROR_USER_MAPPED_FILE,"denial status");
}
static void lifetime(void) {
 HANDLE f,g,m;BYTE *view;DWORD n;BOOL ok;
 text("HANDLES-BEGIN\r\n");
 create(ROOT "source.bin",131073,21);create(ROOT "target.bin",131073,22);
 f=CreateFileA(ROOT "target.bin",GENERIC_READ,FILE_SHARE_READ,0,OPEN_EXISTING,0,0);
 require(f!=INVALID_HANDLE_VALUE,"locked target open");
 denial(MoveFileExA(ROOT "source.bin",ROOT "target.bin",MOVEFILE_REPLACE_EXISTING),"locked replacement denied");
 verify(ROOT "source.bin",131073,21);verify(ROOT "target.bin",131073,22);
 require(ReadFile(f,Buffer,4096,&n,0)&&n==4096&&Buffer[0]==pattern(0,22),"locked handle survives");
 require(CloseHandle(f),"locked close");
 require(MoveFileExA(ROOT "source.bin",ROOT "target.bin",MOVEFILE_REPLACE_EXISTING),"closed replacement");
 verify(ROOT "target.bin",131073,21);require(DeleteFileA(ROOT "target.bin"),"target delete");
 text("LOCKED-PASS\r\n");
 f=dirty(ROOT "pending.bin",31);
 g=CreateFileA(ROOT "pending.bin",GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE,0,OPEN_EXISTING,0,0);
 require(g!=INVALID_HANDLE_VALUE,"second pending handle");
 require(DeleteFileA(ROOT "pending.bin"),"mark delete pending");
 {HANDLE h=CreateFileA(ROOT "pending.bin",GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE,0,OPEN_EXISTING,0,0);
 require(h==INVALID_HANDLE_VALUE,"pending reopen denied");require(GetLastError()==ERROR_ACCESS_DENIED,"pending status");}
 SetFilePointer(f,0,0,FILE_BEGIN);Buffer[0]=0x59;require(WriteFile(f,Buffer,1,&n,0)&&n==1,"pending handle write");
 require(FlushFileBuffers(f),"pending flush");require(CloseHandle(g)&&CloseHandle(f),"pending last close");
 create(ROOT "pending.bin",131073,32);verify(ROOT "pending.bin",131073,32);
 text("PENDING-PASS\r\n");
 f=dirty(ROOT "mapped.bin",41);m=CreateFileMappingA(f,0,PAGE_READWRITE,0,0,0);
 require(m!=0,"mapping object");view=MapViewOfFile(m,FILE_MAP_WRITE,0,0,0);require(view!=0,"mapping view");
 view[65536]=0x6a;create(ROOT "source.bin",131073,42);
 denial(MoveFileExA(ROOT "source.bin",ROOT "mapped.bin",MOVEFILE_REPLACE_EXISTING),"mapped open replacement denied");
 require(view[65536]==0x6a,"mapping survives denied replace");require(CloseHandle(f),"file closes before view");
 ok=DeleteFileA(ROOT "mapped.bin");denial(ok,"mapped deletion denied");
 view[65537]=0x7b;require(FlushViewOfFile(view,0),"view flush after file close");
 require(CloseHandle(m),"mapping handle closes before view");require(view[65537]==0x7b,"view survives mapping close");
 require(UnmapViewOfFile(view),"view last close");
 require(MoveFileExA(ROOT "source.bin",ROOT "mapped.bin",MOVEFILE_REPLACE_EXISTING),"replacement after unmap");
 verify(ROOT "mapped.bin",131073,42);text("MAPPING-PASS\r\n");
}
void WINAPI mainCRTStartup(void) {
 DWORD i,j,oldFirst,oldLast,newFirst,newLast;char target[80],reuse[80];HANDLE f,m;BYTE *view;
 Log=CreateFileA("C:\\xwn-life.log",GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,0,0);
 if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
 text("LIFE-BEGIN\r\n");require(CreateDirectoryA("C:\\xwnlife",0),"lifetime directory");
 lifetime();
 for(i=0;i<32;i++) {
  named(target,"target",i);named(reuse,"reuse",i);
  create(ROOT "source.bin",131073,100+i);
  f=dirty(target,200+i);
  if(i%2){m=CreateFileMappingA(f,0,PAGE_READWRITE,0,0,0);require(m!=0,"dirty map");
   view=MapViewOfFile(m,FILE_MAP_WRITE,0,0,0);require(view!=0,"dirty view");
   for(j=0;j<131073;j+=4096)view[j]^=0x5a;
   require(UnmapViewOfFile(view)&&CloseHandle(m),"unmap without explicit flush");}
  require(CloseHandle(f),"dirty close without explicit flush");clusters(target,&oldFirst,&oldLast);
  require(MoveFileExA(ROOT "source.bin",target,MOVEFILE_REPLACE_EXISTING),"dirty existing replacement");
  create(reuse,131073,300+i);clusters(reuse,&newFirst,&newLast);if(newFirst==oldLast)++Reuse;
  verify(target,131073,100+i);verify(reuse,131073,300+i);number("cycles=",i+1);
 }
 require(Reuse>0,"replacement storage reuse observed");number("reuse=",Reuse);
 text("REPLACEMENT-PASS\r\n");
 /* Retain all resulting files through the following cache pressure/idle/reboot. */
 for(i=0;i<32;i++){named(target,"target",i);named(reuse,"reuse",i);verify(target,131073,100+i);verify(reuse,131073,300+i);}
 number("checks=",Checks);text("LIFE-PASS\r\n");CloseHandle(Log);ExitProcess(0);
}
