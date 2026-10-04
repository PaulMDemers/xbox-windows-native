/* Emulator-only Windows 2000 filesystem experiment; no CRT required. */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <winsvc.h>
static HANDLE Log;
static DWORD Failures;
static void line(const char *s) {
 DWORD n;WriteFile(Log,s,lstrlenA(s),&n,NULL);FlushFileBuffers(Log);
}
static void number(const char *s,DWORD v) {
 char b[20];unsigned n=sizeof(b);b[--n]=0;b[--n]='\n';b[--n]='\r';
 do{b[--n]='0'+v%10;v/=10;}while(v);line(s);line(b+n);
}
static void fail(const char *s) {DWORD error=GetLastError();++Failures;line(s);number("Error: ",error);}

static BYTE Pattern[32768];
static BOOL verify(const char *name,DWORD size) {
 HANDLE f;BYTE b[2048];DWORD pos=0,n,i;BOOL okay=TRUE;
 f=CreateFileA(name,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 if(f==INVALID_HANDLE_VALUE){fail("Stress reopen failed\r\n");return FALSE;}
 while(pos<size){DWORD want=size-pos;if(want>sizeof(b))want=sizeof(b);
  if(!ReadFile(f,b,want,&n,NULL)||n!=want){fail("Stress read failed\r\n");okay=FALSE;break;}
  for(i=0;i<n;++i)if(b[i]!=Pattern[(pos+i)%sizeof(Pattern)]){SetLastError(ERROR_CRC);fail("Stress bytes differ\r\n");okay=FALSE;break;}
  if(!okay)break;pos+=n;
 }
 CloseHandle(f);return okay;
}
static void stress(void) {
 DWORD i,j,n;HANDLE f,find,map;BYTE *view;WIN32_FIND_DATAA fd;char name[]="Q:\\XWNStress\\file000.dat";
 if(!CreateDirectoryA("Q:\\XWNStress",NULL)&&GetLastError()!=ERROR_ALREADY_EXISTS){fail("Stress mkdir failed\r\n");return;}
 for(i=0;i<sizeof(Pattern);++i)Pattern[i]=(BYTE)((i*31)^(i>>8)^0x96);
 for(i=0;i<180;++i){
  name[17]=(char)('0'+i/100);name[18]=(char)('0'+(i/10)%10);name[19]=(char)('0'+i%10);
  f=CreateFileA(name,GENERIC_WRITE|GENERIC_READ,0,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
  if(f==INVALID_HANDLE_VALUE){fail("Stress create failed\r\n");return;}
  for(j=0;j<8;++j)if(!WriteFile(f,Pattern,32768,&n,NULL)||n!=32768){fail("Buffered write failed\r\n");CloseHandle(f);return;}
  if(!FlushFileBuffers(f)){fail("Buffered flush failed\r\n");CloseHandle(f);return;}CloseHandle(f);
  if(!verify(name,8*32768))return;
 }
 line("180 buffered files verified\r\n");
 find=FindFirstFileA("Q:\\XWNStress\\*",&fd);i=0;
 if(find==INVALID_HANDLE_VALUE){fail("Stress enumeration failed\r\n");return;}
 do{if(fd.cFileName[0]=='.')continue;if(lstrlenA(fd.cFileName)!=11){fail("Stress directory name damaged\r\n");break;}++i;}while(FindNextFileA(find,&fd));FindClose(find);
 if(i!=180){SetLastError(ERROR_INVALID_DATA);fail("Stress directory count differs\r\n");}
 else line("180 directory entries verified\r\n");
 f=CreateFileA("Q:\\XWNStress\\mapped.dat",GENERIC_READ|GENERIC_WRITE,0,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
 if(f==INVALID_HANDLE_VALUE){fail("Mapping file create failed\r\n");return;}
 map=CreateFileMappingA(f,NULL,PAGE_READWRITE,0,32768,NULL);
 if(!map){fail("CreateFileMapping failed\r\n");CloseHandle(f);return;}
 view=MapViewOfFile(map,FILE_MAP_WRITE,0,0,32768);
 if(!view)fail("MapViewOfFile failed\r\n");else{
  for(i=0;i<32768;++i)view[i]=Pattern[i];
  if(!FlushViewOfFile(view,32768))fail("FlushViewOfFile failed\r\n");UnmapViewOfFile(view);
 }
 CloseHandle(map);if(!FlushFileBuffers(f))fail("Mapped file flush failed\r\n");CloseHandle(f);
 if(verify("Q:\\XWNStress\\mapped.dat",32768))line("Mapped file flush and readback verified\r\n");
}
void WINAPI mainCRTStartup(void) {
 SC_HANDLE scm=NULL,svc=NULL;HANDLE f=INVALID_HANDLE_VALUE,find;WIN32_FIND_DATAA fd;
 BYTE *buffer=NULL;DWORD i,block,n,flags,serial,maxname;char fs[40],label[80];BOOL okay=TRUE;
 Log=CreateFileA("C:\\xwn-fatx.log",GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
 if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);
 line("Private emulator FATX runtime test\r\n");
 scm=OpenSCManagerA(NULL,NULL,SC_MANAGER_CREATE_SERVICE);
 if(!scm){fail("OpenSCManager failed\r\n");goto done;}
 svc=CreateServiceA(scm,"XwnFatx","XWN FATX experiment",SERVICE_START|SERVICE_QUERY_STATUS,
  SERVICE_FILE_SYSTEM_DRIVER,SERVICE_DEMAND_START,SERVICE_ERROR_NORMAL,"C:\\xwnfatx.sys",NULL,NULL,NULL,NULL,NULL);
 if(!svc){fail("CreateService failed\r\n");goto done;}
 line("Starting filesystem driver\r\n");
 if(!StartServiceA(svc,0,NULL)){fail("StartService failed\r\n");goto done;}
 line("Filesystem driver loaded\r\n");
 if(!DefineDosDeviceA(DDD_RAW_TARGET_PATH,"Q:","\\Device\\Harddisk0\\Partition2")){
  fail("DefineDosDevice failed\r\n");goto done;
 }
 line("Querying private FATX volume\r\n");
 if(!GetVolumeInformationA("Q:\\",label,sizeof(label),&serial,&maxname,&flags,fs,sizeof(fs))){
  fail("GetVolumeInformation failed\r\n");goto done;
 }
 line("Filesystem: ");line(fs);line("\r\n");number("Maximum component length: ",maxname);
 if(lstrcmpiA(fs,"FATX")){SetLastError(ERROR_INVALID_DATA);fail("Expected FATX volume; refusing test writes\r\n");goto done;}
 find=FindFirstFileA("Q:\\*",&fd);
 if(find==INVALID_HANDLE_VALUE){fail("Root enumeration failed\r\n");goto done;}
 n=0;do{line("Entry: ");line(fd.cFileName);line("\r\n");++n;}while(n<50&&FindNextFileA(find,&fd));FindClose(find);
 if(!CreateDirectoryA("Q:\\XWNTest",NULL)&&GetLastError()!=ERROR_ALREADY_EXISTS){fail("Directory creation failed\r\n");goto done;}
 buffer=VirtualAlloc(NULL,65536,MEM_COMMIT,PAGE_READWRITE);if(!buffer){fail("Buffer allocation failed\r\n");goto done;}
 f=CreateFileA("Q:\\XWNTest\\roundtrip.bin",GENERIC_WRITE,0,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,NULL);
 if(f==INVALID_HANDLE_VALUE){fail("FATX create failed\r\n");goto done;}
 for(block=0;block<16;++block){
  for(i=0;i<65536;++i)buffer[i]=(BYTE)((i*17+block*29)^0xa5);
  if(!WriteFile(f,buffer,65536,&n,NULL)||n!=65536){fail("FATX write failed\r\n");okay=FALSE;break;}
 }
 if(!FlushFileBuffers(f)){fail("FATX flush failed\r\n");okay=FALSE;}
 CloseHandle(f);f=INVALID_HANDLE_VALUE;if(!okay)goto done;
 line("One MiB written and flushed\r\n");
 f=CreateFileA("Q:\\XWNTest\\roundtrip.bin",GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 if(f==INVALID_HANDLE_VALUE){fail("FATX reopen failed\r\n");goto done;}
 for(block=0;block<16;++block){
  if(!ReadFile(f,buffer,65536,&n,NULL)||n!=65536){fail("FATX read failed\r\n");okay=FALSE;break;}
  for(i=0;i<65536;++i)if(buffer[i]!=(BYTE)((i*17+block*29)^0xa5)){SetLastError(ERROR_CRC);fail("FATX comparison failed\r\n");okay=FALSE;break;}
  if(!okay)break;
 }
 if(okay){line("One MiB reopen/read comparison passed\r\n");CloseHandle(f);f=INVALID_HANDLE_VALUE;stress();}
 done:
 if(f!=INVALID_HANDLE_VALUE)CloseHandle(f);
 if(buffer)VirtualFree(buffer,0,MEM_RELEASE);
 if(svc)CloseServiceHandle(svc);if(scm)CloseServiceHandle(scm);
 number("Failures: ",Failures);CloseHandle(Log);ExitProcess(Failures);
}
