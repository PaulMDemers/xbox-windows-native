/* MIT. Verify pristine and traced results, actual address reuse, restored code. */
static BOOL lifetimecontrol610(void) {
 const char *names[3]={"C:\\xwn610-kit\\lifea.dll","C:\\xwn610-kit\\lifeb.dll","C:\\xwn610-kit\\lifea.dll"};
 const BYTE bytes[3]={0x90,0xf8,0x90};DWORD i,base=0,address=0;
 typedef DWORD (__cdecl *LIFEFN)(void);
 for(i=0;i<3;i++) {
  HMODULE h=LoadLibraryA(names[i]);FARPROC f;BYTE *ret;
  if(!h)return FALSE;
  f=GetProcAddress(h,"transient610");ret=(BYTE *)GetProcAddress(h,"life_return610");
  if(!f||!ret||*ret!=bytes[i])return FALSE;
  if(i&&((DWORD)h!=base||(DWORD)ret!=address))return FALSE;
  base=(DWORD)h;address=(DWORD)ret;
  if(((LIFEFN)f)()!=0x610face0u||*ret!=bytes[i])return FALSE;
  if(!FreeLibrary(h))return FALSE;
  if(GetModuleHandleA(i==1?"lifeb.dll":"lifea.dll"))return FALSE;
 }
 record("LIFETIME610 PASS: A/B/A reused base and return address, restored 90/f8/90\r\n");
 return TRUE;
}
