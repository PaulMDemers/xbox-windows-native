/* One dual capture: original cold packet retained even on missing page. */
static BOOL memory_capture(const char *name)
{
 DWORD written=0,i;BOOL ok=FALSE;HANDLE f=INVALID_HANDLE_VALUE;char cold[64];
 char *p=VirtualAlloc(NULL,133120,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
 if(!p)return FALSE;
 for(i=0;name[i]&&i<54;i++)cold[i]=name[i];
 if(name[i])goto done;
 cold[i++]='.';cold[i++]='c';cold[i++]='o';cold[i++]='l';cold[i++]='d';cold[i]=0;
 if(ExtEscape(Screen,0x5857443b,0,NULL,133120,p)!=1)goto done;
 f=CreateFileA(cold,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
 if(f==INVALID_HANDLE_VALUE)goto done;
 ok=WriteFile(f,p,66560,&written,NULL)&&written==66560;CloseHandle(f);if(!ok)goto done;
 f=CreateFileA(name,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,NULL);
 if(f==INVALID_HANDLE_VALUE){ok=FALSE;goto done;}
 ok=WriteFile(f,p+66560,66560,&written,NULL)&&written==66560;CloseHandle(f);
done:VirtualFree(p,0,MEM_RELEASE);return ok;
}
