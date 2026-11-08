from pathlib import Path
import subprocess,json,hashlib
K=Path(__file__).resolve().parent; s=(K/'main.c').read_text(); body=s[s.index('static int save_report'):s.index('\n\nstatic int geometry')]
prefix=r'''#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
typedef FILE * HANDLE; typedef unsigned long DWORD; typedef long LONG; typedef int IO_STATUS_BLOCK;
#define INVALID_HANDLE_VALUE NULL
#define GENERIC_WRITE 1
#define GENERIC_READ 2
#define CREATE_ALWAYS 3
#define OPEN_EXISTING 4
#define FILE_SHARE_READ 1
#define FILE_ATTRIBUTE_NORMAL 0
static char report[32768],verify[32768]; static size_t used; static int writes,reads;
static HANDLE CreateFileA(const char*p,int mode,int share,void*a,int disposition,int attr,void*b) { (void)share;(void)a;(void)attr;(void)b; if(strcmp(p,"E:\\Applications\\XWNEBoot\\boot-report.json")) abort(); if(mode==GENERIC_WRITE && disposition==CREATE_ALWAYS){writes++;return fopen("status.tmp","wb");} if(mode==GENERIC_READ && disposition==OPEN_EXISTING){reads++;return fopen("status.tmp","rb");} abort(); }
static int WriteFile(HANDLE f,void*p,DWORD n,DWORD*out,void*x){(void)x;*out=fwrite(p,1,n,f);return *out==n;}
static int ReadFile(HANDLE f,void*p,DWORD n,DWORD*out,void*x){(void)x;*out=fread(p,1,n,f);return !ferror(f);}
static LONG NtFlushBuffersFile(HANDLE f,IO_STATUS_BLOCK*i){(void)i;return fflush(f)?-1:0;}
static int CloseHandle(HANDLE f){return fclose(f)==0;}
'''
suffix=r'''
int main(void) { char path[64]; for(int i=0;i<150;i++){used=snprintf(report,sizeof(report),"{\"run\":%d}\n",i);if(save_report(path,sizeof(path)))return 1;} if(writes!=150 || reads!=150)return 2; FILE *f=fopen("status.tmp","rb"); char b[100]={0};fread(b,1,sizeof(b)-1,f);fclose(f);if(strcmp(b,"{\"run\":149}\n"))return 3;return 0; }
'''
O=Path('/mnt/d/xwn-bundle844/report-test001'); O.mkdir(); (O/'test.c').write_text(prefix+body+suffix)
subprocess.run(['gcc-12','-std=c11','-Wall','-Wextra','-Werror',str(O/'test.c'),'-o',str(O/'test')],check=True)
subprocess.run([str(O/'test')],cwd=O,check=True)
r={'passed':True,'scope':'150 sequential calls to actual save_report with host file API substitutes; final file contains latest report. Does not emulate Xbox filesystem or power loss.','source_sha256':hashlib.sha256((K/'main.c').read_bytes()).hexdigest()}
(K/'report-test001.json').write_text(json.dumps(r,indent=2)+'\n')
