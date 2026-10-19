/* MIT. Ephemeral NT5 SHA1 copy-integrity check against pinned retail manifest. */
#define _WIN32_WINNT 0x0500
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <wincrypt.h>
#include "assets.h"
static BYTE buffer[65536];
void WINAPI mainCRTStartup(void){
 HCRYPTPROV provider=0;HCRYPTHASH hash=0;HANDLE file=INVALID_HANDLE_VALUE,log;
 DWORD start=GetTickCount(),i=0,n,size,j,done,code=1;BYTE digest[20];char path[MAX_PATH],line[512];BOOL ok;
 log=CreateFileA("C:\\xwn582-kit\\copy-verified.txt",GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);if(log==INVALID_HANDLE_VALUE)ExitProcess(2);
 if(!CryptAcquireContextA(&provider,0,0,PROV_RSA_FULL,CRYPT_VERIFYCONTEXT|CRYPT_SILENT))goto end;
 for(i=0;i<sizeof(assets)/sizeof(assets[0]);i++){
  if(GetTickCount()-start>180000)goto end;
  wsprintfA(path,"C:\\xwn582-kit\\%s",assets[i].path);
  file=CreateFileA(path,GENERIC_READ,FILE_SHARE_READ,0,OPEN_EXISTING,FILE_FLAG_SEQUENTIAL_SCAN,0);
  if(file==INVALID_HANDLE_VALUE||GetFileSize(file,0)!=assets[i].size)goto end;
  if(!CryptCreateHash(provider,CALG_SHA1,0,0,&hash))goto end;
  do{ok=ReadFile(file,buffer,sizeof(buffer),&n,0);if(!ok||!CryptHashData(hash,buffer,n,0))goto end;}while(n);
  size=sizeof(digest);if(!CryptGetHashParam(hash,HP_HASHVAL,digest,&size,0)||size!=20)goto end;
  for(j=0;j<20;j++)if(digest[j]!=assets[i].sha1[j])goto end;
  CryptDestroyHash(hash);hash=0;CloseHandle(file);file=INVALID_HANDLE_VALUE;
 }
 code=0;
end:
 wsprintfA(line,"verified=%lu\r\nfiles=%lu\r\nexpected=%lu\r\nerror=%lu\r\nelapsed_ms=%lu\r\n",(DWORD)(code==0),i,(DWORD)(sizeof(assets)/sizeof(assets[0])),GetLastError(),GetTickCount()-start);WriteFile(log,line,lstrlenA(line),&done,0);FlushFileBuffers(log);CloseHandle(log);
 if(hash)CryptDestroyHash(hash);
 if(provider)CryptReleaseContext(provider,0);
 if(file!=INVALID_HANDLE_VALUE)CloseHandle(file);
 ExitProcess(code);
}
