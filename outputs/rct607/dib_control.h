/* MIT. Original header probes; invalid pointers never passed to GDI. */
typedef DWORD (__cdecl *DIBPROBE604)(const void*);
static BOOL dibcontrol604(void) {
 HMODULE m;DIBPROBE604 probe;union {FARPROC generic;DIBPROBE604 probe;} address;
 DWORD h[10],i,old;BYTE *pages;BOOL ok=TRUE;
 m=LoadLibraryA("C:\\xwn607-kit\\fixture.dll");if(!m)return FALSE;
 address.generic=GetProcAddress(m,"probe_dib604");probe=address.probe;if(!probe)return FALSE;
 pages=VirtualAlloc(0,8192,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);if(!pages)return FALSE;
 if(!VirtualProtect(pages+4096,4096,PAGE_NOACCESS,&old)){VirtualFree(pages,0,MEM_RELEASE);return FALSE;}
 for(i=0;i<10;i++)h[i]=0;
 h[0]=40;h[1]=8;h[2]=(DWORD)-8;h[3]=(32u<<16)|1;
 #define TEST604(p) do {if(probe(p)!=0x604d1b00u)ok=FALSE;} while(0)
 TEST604(h);h[2]=8;TEST604(h);h[2]=(DWORD)-8;
 TEST604(0);TEST604((void*)0xffffffffu);TEST604(pages+4096);
 *(DWORD*)(pages+4092)=40;TEST604(pages+4092);
 h[0]=124;TEST604(h);h[0]=40;
 h[1]=0;TEST604(h);h[1]=8;
 h[2]=0x80000000u;TEST604(h);h[2]=(DWORD)-8;
 h[3]=(32u<<16)|2;TEST604(h);h[3]=(3u<<16)|1;TEST604(h);h[3]=(32u<<16)|1;
 h[4]=1;TEST604(h);h[4]=0;
 h[1]=16385;TEST604(h);h[1]=8;
 h[5]=1;TEST604(h);h[5]=0;
 h[8]=257;TEST604(h);h[8]=0;
 #undef TEST604
 if(!VirtualFree(pages,0,MEM_RELEASE))ok=FALSE;
 record(ok?"DIB604 PROBES PASS\r\n":"DIB604 PROBES FAIL\r\n");return ok;
}
