/* MIT. Exact614 counter and bounded COM1 primitives. */
typedef BOOL (WINAPI *MEMFN)(HANDLE,PPROCESS_MEMORY_COUNTERS,DWORD);
typedef struct {ULONGLONG q,k,u;DWORD tick,ws,peak,page;} SNAP;
static MEMFN memfn;
static HANDLE logh;
static void zero(void *p,DWORD n){BYTE *b=p;while(n--)*b++=0;}
static ULONGLONG ft(FILETIME f){return ((ULONGLONG)f.dwHighDateTime<<32)|f.dwLowDateTime;}
static void hex64(char *s,ULONGLONG v){int i;for(i=15;i>=0;i--){s[i]="0123456789abcdef"[(DWORD)v&15];v>>=4;}s[16]=0;}
static BOOL snap(HANDLE p,SNAP *s,BOOL memory){
 FILETIME c,e,k,u;LARGE_INTEGER q;PROCESS_MEMORY_COUNTERS m;
 if(!QueryPerformanceCounter(&q)||q.QuadPart<0||!GetProcessTimes(p,&c,&e,&k,&u))return FALSE;
 zero(&m,sizeof(m));m.cb=sizeof(m);
 if(memory&&!memfn(p,&m,sizeof(m)))return FALSE;
 s->q=(ULONGLONG)q.QuadPart;s->tick=GetTickCount();s->k=ft(k);s->u=ft(u);
 s->ws=m.WorkingSetSize;s->peak=m.PeakWorkingSetSize;s->page=m.PagefileUsage;
 return TRUE;
}
static BOOL text(const char *s){DWORD n=lstrlenA(s),w;return WriteFile(logh,s,n,&w,0)&&n==w&&FlushFileBuffers(logh);}
static BOOL row(const char *tag,DWORD id,DWORD index,SNAP *s){
 char b[256],q[17],k[17],u[17];hex64(q,s->q);hex64(k,s->k);hex64(u,s->u);
 wsprintfA(b,"%s %lu %lu %s %lu %s %s %lu %lu %lu\r\n",tag,id,index,q,s->tick,k,u,s->ws,s->peak,s->page);
 return text(b);
}
static BOOL init(const char *path){
 HMODULE m;LARGE_INTEGER f;char b[80],h[17];
 m=LoadLibraryA("psapi.dll");if(!m)return FALSE;
 memfn=(MEMFN)GetProcAddress(m,"GetProcessMemoryInfo");if(!memfn)return FALSE;
 logh=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);
 if(logh==INVALID_HANDLE_VALUE||!QueryPerformanceFrequency(&f)||f.QuadPart<=0)return FALSE;
 hex64(h,(ULONGLONG)f.QuadPart);wsprintfA(b,"FREQ %s\r\n",h);return text(b);
}
static HANDLE serialh;
static BOOL mark(const char *tag,DWORD id,SNAP *s){
 char b[100];DWORD n,w;wsprintfA(b,"MARK %s %lu %lu\r\n",tag,id,s->tick);n=lstrlenA(b);
 return WriteFile(serialh,b,n,&w,0)&&n==w;
}
static BOOL serial_open(void){
 DCB d;COMMTIMEOUTS t;
 serialh=CreateFileA("\\\\.\\COM1",GENERIC_WRITE,0,0,OPEN_EXISTING,0,0);if(serialh==INVALID_HANDLE_VALUE)return FALSE;
 zero(&d,sizeof(d));d.DCBlength=sizeof(d);if(!GetCommState(serialh,&d))return FALSE;
 d.BaudRate=CBR_115200;d.ByteSize=8;d.Parity=NOPARITY;d.StopBits=ONESTOPBIT;
 d.fBinary=TRUE;d.fParity=FALSE;d.fOutxCtsFlow=FALSE;d.fOutxDsrFlow=FALSE;
 d.fOutX=FALSE;d.fInX=FALSE;d.fDtrControl=DTR_CONTROL_ENABLE;d.fRtsControl=RTS_CONTROL_ENABLE;
 zero(&t,sizeof(t));t.WriteTotalTimeoutConstant=1000;
 return SetCommState(serialh,&d)&&SetCommTimeouts(serialh,&t);
}
