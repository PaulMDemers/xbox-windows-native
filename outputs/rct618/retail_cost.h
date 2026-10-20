/* MIT. Open the debugger's actual game child, preserving its birth identity. */
typedef DWORD (WINAPI *NAME618)(HANDLE,HMODULE,LPSTR,DWORD);
static BOOL cost_identity(HANDLE recorder,DWORD recorder_pid){
 HANDLE file=INVALID_HANDLE_VALUE;DWORD id[4],got,start=GetTickCount();BOOL valid=FALSE;
 FILETIME ct,et,kt,ut;char image[MAX_PATH],line[200];NAME618 namefn;
 do{
  file=CreateFileA("C:\\xwn618\\identity.bin",GENERIC_READ,FILE_SHARE_READ,0,OPEN_EXISTING,0,0);
  if(file!=INVALID_HANDLE_VALUE){
   valid=GetFileSize(file,0)==sizeof(id)&&ReadFile(file,id,sizeof(id),&got,0)&&got==sizeof(id);
   CloseHandle(file);if(valid)break;
  }
  if(WaitForSingleObject(recorder,100)!=WAIT_TIMEOUT)return FALSE;
 }while(GetTickCount()-start<10000);
 if(!valid||!id[0]||id[1]!=recorder_pid||id[0]==id[1]||id[0]==GetCurrentProcessId())return FALSE;
 gamehandle=OpenProcess(PROCESS_QUERY_INFORMATION|PROCESS_VM_READ|SYNCHRONIZE,FALSE,id[0]);
 if(!gamehandle||!GetProcessTimes(gamehandle,&ct,&et,&kt,&ut)||ct.dwLowDateTime!=id[2]||ct.dwHighDateTime!=id[3])return FALSE;
 namefn=(NAME618)GetProcAddress(GetModuleHandleA("psapi.dll"),"GetModuleFileNameExA");
 if(!namefn)return FALSE;
 zero(image,sizeof(image));got=namefn(gamehandle,0,image,sizeof(image));
 if(!got||got>=sizeof(image)||lstrcmpiA(image,"C:\\xwn618-kit\\game\\RCT.EXE")!=0)return FALSE;
 gamepid=id[0];
 wsprintfA(line,"IDENTITY 1 %lu %lu %lu %lu %lu\r\n",id[0],id[1],GetCurrentProcessId(),id[2],id[3]);
 return text(line);
}
static BOOL cost_game(void){
 HANDLE request=0,ack=0;DWORD n=0;BOOL ok=FALSE;char line[80];
 if(!gamehandle||!tracehandle)return FALSE;
 request=OpenEventA(EVENT_MODIFY_STATE,FALSE,"XWN618PhaseRequest");
 ack=OpenEventA(SYNCHRONIZE,FALSE,"XWN618PhaseAck");
 if(!request||!ack)goto done;
 if(!window617(gamehandle,tracehandle,request,ack,1,&n))goto done;
 wsprintfA(line,"SAMPLES %lu\r\n",n);ok=text(line)&&text("COST_DONE\r\n");
done:
 if(request)CloseHandle(request);
 if(ack)CloseHandle(ack);
 return ok;
}
