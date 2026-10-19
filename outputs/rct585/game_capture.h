/* SPDX-License-Identifier: MIT. Built-in Screenshot only; no fullscreen GDI. */
typedef struct {char names[64][MAX_PATH];DWORD count;} ROOTFILES;
static ROOTFILES priorfiles;
static BOOL rootfiles(ROOTFILES* out){
 WIN32_FIND_DATAA d;HANDLE h;DWORD e;char pattern[MAX_PATH];
 out->count=0;wsprintfA(pattern,"%s\\*",game);h=FindFirstFileA(pattern,&d);
 if(h==INVALID_HANDLE_VALUE)return FALSE;
 do{if(d.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY)continue;
  if(out->count>=64||lstrlenA(d.cFileName)>100){FindClose(h);return FALSE;}
  lstrcpyA(out->names[out->count++],d.cFileName);
 }while(FindNextFileA(h,&d));e=GetLastError();FindClose(h);return e==ERROR_NO_MORE_FILES;
}
static BOOL waspresent(const char* n){DWORD i;for(i=0;i<priorfiles.count;i++)if(lstrcmpiA(n,priorfiles.names[i])==0)return TRUE;return FALSE;}
static BOOL newfile(char* name,DWORD* size,FILETIME* written){
 WIN32_FIND_DATAA d;HANDLE h;DWORD count=0,e;char pattern[MAX_PATH];
 wsprintfA(pattern,"%s\\*",game);h=FindFirstFileA(pattern,&d);if(h==INVALID_HANDLE_VALUE)return FALSE;
 do{if((d.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY)||waspresent(d.cFileName))continue;
  if(d.nFileSizeHigh||d.nFileSizeLow>4*1024*1024||lstrlenA(d.cFileName)>100){FindClose(h);return FALSE;}
  count++;lstrcpyA(name,d.cFileName);*size=d.nFileSizeLow;*written=d.ftLastWriteTime;
 }while(FindNextFileA(h,&d));e=GetLastError();FindClose(h);
 if(count>1){number("screenshot_multiple_new_files",count);return FALSE;}
 return e==ERROR_NO_MORE_FILES&&count==1&&*size>0;
}
static BOOL gamecapture(const char* tag){
 DWORD start,size=0,previous=0,stable=0;FILETIME written={0,0},last={0,0};
 char name[MAX_PATH],oldname[MAX_PATH],src[MAX_PATH],dest[MAX_PATH],line[640];BOOL ok=FALSE;
 zero(name,sizeof(name));zero(oldname,sizeof(oldname));
 if(capturecount>=32||!state(tag)||!rootfiles(&priorfiles))return FALSE;
 number("screenshot_request_tick",GetTickCount());
 if(!click(44,14)||!click(76,80))goto done;
 start=GetTickCount();
 while(GetTickCount()-start<15000){
  if(newfile(name,&size,&written)){
   if(lstrcmpA(name,oldname)==0&&size==previous&&CompareFileTime(&written,&last)==0)stable++;else stable=0;
   lstrcpyA(oldname,name);previous=size;last=written;
   if(stable>=4){
    wsprintfA(src,"%s\\%s",game,name);wsprintfA(dest,"C:\\xwn585\\%02lu-%s.shot",capturecount,tag);
    ok=CopyFileA(src,dest,TRUE);
    wsprintfA(line,"game_screenshot=%s source=%s bytes=%lu copied=%lu tick=%lu\r\n",tag,name,size,(DWORD)ok,GetTickCount());bytes(logh,line,lstrlenA(line));break;
   }
  }else stable=0;
  Sleep(250);
 }
 if(!ok)number("screenshot_file_timeout_or_copy_failure",1);
 if(ok){number("screenshot_settle_begin",GetTickCount());Sleep(10000);number("screenshot_settle_end",GetTickCount());ok=state("screenshot_done");}
done:
 wsprintfA(line,"capture=%s index=%lu success=%lu error=%lu\r\n",tag,capturecount,(DWORD)ok,GetLastError());bytes(logh,line,lstrlenA(line));capturecount++;return ok;
}
