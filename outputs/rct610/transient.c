/* MIT. Original address-reuse control: one traced call inside a transient DLL. */
#define _WIN32_WINNT 0x0500
#include <windows.h>
#ifndef RETURN_BYTE
#error RETURN_BYTE required
#endif
#define STRINGIFY_INNER(x) #x
#define STRINGIFY(x) STRINGIFY_INNER(x)
DWORD __cdecl transient610(void) {
 HMODULE kernel=GetModuleHandleA("kernel32.dll");FARPROC answer;
 if(!kernel)return 0;
 __asm__ __volatile__(
  "pushl %2\n\tpushl %1\n\tcall *%3\n\t"
  ".global _life_return610\n_life_return610:\n\t.byte " STRINGIFY(RETURN_BYTE) "\n\t"
  :"=a"(answer):"r"(kernel),"r"("GetTickCount"),"r"(GetProcAddress)
  :"ecx","edx","memory","cc");
 return answer?0x610face0u:0;
}
BOOL WINAPI DllMain(HINSTANCE h,DWORD why,LPVOID unused) {
 (void)h;(void)why;(void)unused;return TRUE;
}
