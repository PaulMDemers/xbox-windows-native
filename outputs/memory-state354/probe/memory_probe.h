/* Capture raw diagnostic output even when it contains an explicit refusal.
 * Refusal is analyzed separately; never replace it with a successful retry. */
static BOOL memory_capture(const char *name)
{
 DWORD written=0;BOOL ok=FALSE;HANDLE f=INVALID_HANDLE_VALUE;
 void *p=VirtualAlloc(NULL,66560,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
 if(!p)return FALSE;
 if(ExtEscape(Screen,0x5857443a,0,NULL,66560,(char *)p)==1){
  f=CreateFileA(name,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
  if(f!=INVALID_HANDLE_VALUE){ok=WriteFile(f,p,66560,&written,NULL)&&written==66560;CloseHandle(f);}
 }
 VirtualFree(p,0,MEM_RELEASE);return ok;
}
