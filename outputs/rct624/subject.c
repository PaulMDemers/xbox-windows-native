/* SPDX-License-Identifier: MIT. Original stand-in, not retail game code. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
void WINAPI mainCRTStartup(void){
 HKEY k;char b[256],cwd[256];DWORD n,t,v,ok=1,done;HANDLE f;
 const char*path="C:\\xwn586-kit\\game";
 GetCurrentDirectoryA(sizeof(cwd),cwd);ok=ok&&!lstrcmpiA(cwd,path);
 if(RegOpenKeyExA(HKEY_LOCAL_MACHINE,"SOFTWARE\\Fish Technology Group\\RollerCoaster Tycoon Setup",0,KEY_READ,&k)!=ERROR_SUCCESS)ExitProcess(30);
 n=sizeof(b);ok=ok&&RegQueryValueExA(k,"Path",0,&t,(BYTE*)b,&n)==ERROR_SUCCESS&&t==REG_SZ&&!lstrcmpA(b,path);
 n=sizeof(b);ok=ok&&RegQueryValueExA(k,"SetupPath",0,&t,(BYTE*)b,&n)==ERROR_SUCCESS&&t==REG_SZ&&!lstrcmpA(b,path);
 n=sizeof(v);ok=ok&&RegQueryValueExA(k,"Language",0,&t,(BYTE*)&v,&n)==ERROR_SUCCESS&&t==REG_DWORD&&v==0;RegCloseKey(k);
 f=CreateFileA("C:\\xwn624\\subject.txt",GENERIC_WRITE,0,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);if(f==INVALID_HANDLE_VALUE)ExitProcess(31);
 b[0]=ok?'1':'0';WriteFile(f,b,1,&done,0);FlushFileBuffers(f);CloseHandle(f);
 MessageBoxA(0,ok?"Original control is running. Paths and registry values passed. Leave this open beyond three minutes, then choose OK to simulate quitting the game.":"CONTROL FAILED", "RCT launcher control",MB_OK);
 ExitProcess(ok?0:32);
}
