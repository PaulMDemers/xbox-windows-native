/* MIT. An original DLL with one known ordinal, for resolution controls. */
#include <windows.h>
__declspec(dllexport) DWORD __cdecl probe597(DWORD n) { return n ^ 0x597abcde; }
BOOL WINAPI DllMain(HINSTANCE h,DWORD why,LPVOID reserved) {
    (void)h; (void)why; (void)reserved; return TRUE;
}
