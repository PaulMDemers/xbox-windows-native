/* MIT. Original recursive cdecl target; volatile indirection prevents inlining. */
#define _WIN32_WINNT 0x0500
#include <windows.h>
typedef DWORD (__cdecl *PROBE)(DWORD,DWORD);
DWORD __cdecl probe601(DWORD depth,DWORD seed);
static PROBE volatile again=probe601;
DWORD __cdecl probe601(DWORD depth,DWORD seed) {
    DWORD v;
    if(!depth) {Sleep(1);return seed^0x601abcdeu;}
    v=again(depth-1,seed+1); return v+depth;
}
BOOL WINAPI DllMain(HINSTANCE h,DWORD why,LPVOID reserved) {
    (void)h;(void)why;(void)reserved;return TRUE;
}
