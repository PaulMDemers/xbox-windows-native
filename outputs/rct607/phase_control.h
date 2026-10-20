/* MIT. Exhaust startup sampling; request during a pending exported call. */
typedef DWORD (__cdecl *PHASEPROBE605)(HANDLE);
static BOOL phasecontrol605(BOOL control) {
 HANDLE request=0,ack=0;HMODULE g,m;union {FARPROC generic;DIB601 dib;} da;
 union {FARPROC generic;PHASEPROBE605 phase;} pa;
 DIB601 dib;STRETCH601 stretch;PHASEPROBE605 phase;
 BITMAPINFO info;DWORD *sa=0,*sb=0,i,j;HBITMAP a=0,b=0;HDC dc=0;HGDIOBJ old=0;BOOL ok=FALSE;
 if(control){
  SetLastError(0);request=CreateEventA(0,TRUE,FALSE,"XWN607PhaseRequest");if(!request||GetLastError()==ERROR_ALREADY_EXISTS)goto end;
  SetLastError(0);ack=CreateEventA(0,TRUE,FALSE,"XWN607PhaseAck");if(!ack||GetLastError()==ERROR_ALREADY_EXISTS)goto end;
 }else{request=OpenEventA(EVENT_MODIFY_STATE,FALSE,"XWN607PhaseRequest");ack=OpenEventA(SYNCHRONIZE,FALSE,"XWN607PhaseAck");}
 if(!request||!ack)goto end;
 g=GetModuleHandleA("GDI32.DLL");m=GetModuleHandleA("fixture.dll");if(!g||!m)goto end;
 da.generic=GetProcAddress(g,"CreateDIBSection");dib=da.dib;
 stretch=(STRETCH601)GetProcAddress(g,"StretchDIBits");pa.generic=GetProcAddress(m,"probe_phase605");phase=pa.phase;
 if(!dib||!stretch||!phase)goto end;
 zero601(&info,sizeof(info));info.bmiHeader.biSize=40;info.bmiHeader.biWidth=8;info.bmiHeader.biHeight=-8;
 info.bmiHeader.biPlanes=1;info.bmiHeader.biBitCount=32;
 a=dib(0,&info,0,(void**)&sa,0,0);b=dib(0,&info,0,(void**)&sb,0,0);if(!a||!b||!sa||!sb)goto end;
 dc=CreateCompatibleDC(0);if(!dc)goto end;old=SelectObject(dc,b);if(!old)goto end;
 for(j=0;j<71;j++){
  if(j==35){if(phase(request)!=0x605face0u)goto end;if(control&&!SetEvent(ack))goto end;}
  if(j==36){if(WaitForSingleObject(ack,1000)!=WAIT_OBJECT_0||!SetEvent(request))goto end;}
  for(i=0;i<64;i++){sa[i]=(i*0x020301u+j*0x010101u)&0xffffffu;sb[i]=0;}
  if(stretch(dc,0,0,8,8,0,0,8,8,sa,&info,0,SRCCOPY)!=8||!GdiFlush())goto end;
  for(i=0;i<64;i++)if(sa[i]!=sb[i])goto end;
 }
 ok=TRUE;
end:
 if(dc&&old)SelectObject(dc,old);
 if(a)DeleteObject(a);
 if(b)DeleteObject(b);
 if(dc)DeleteDC(dc);
 if(request)CloseHandle(request);
 if(ack)CloseHandle(ack);
 record(ok?"PHASE605 PASS: 71 exact copies, pending request, duplicate request\r\n":"PHASE605 FAIL\r\n");return ok;
}
