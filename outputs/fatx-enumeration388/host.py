from pathlib import Path
import hashlib,json,subprocess
K=Path(__file__).resolve().parent;src=Path('/mnt/e/xwn388/source001/create.c').read_text();out=Path('/mnt/e/xwn388/host001');out.mkdir(parents=True,exist_ok=False)
a=src.index('        if (rcFcb)');brace=src.index('{',a);depth=1;i=brace+1
while depth:
 if src[i]=='{':depth+=1
 if src[i]=='}':depth-=1
 i+=1
block=src[a:i];assert 'startIndex += 2;' in block and 'DirContext->DirIndex = rcFcb->dirIndex;' in block
fixed=block.replace('DirContext->StartIndex = rcFcb->startIndex;\n                DirContext->DirIndex = rcFcb->dirIndex;','DirContext->StartIndex = rcFcb->startIndex;\n                DirContext->DirIndex = rcFcb->dirIndex;\n                if (IsFatX && !vfatFCBIsRoot(Parent))\n                {\n                    DirContext->StartIndex += 2;\n                    DirContext->DirIndex += 2;\n                }')
assert fixed!=block
head=r"""/* SPDX-License-Identifier: GPL-2.0-or-later
 * Exact pinned ReactOS-derived cached-FCB branch; host adapters only. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
typedef uint32_t ULONG;
typedef int NTSTATUS;
typedef struct { uint32_t value; } UNICODE_STRING;
typedef struct { uint32_t value; } DIR_ENTRY;
typedef struct { ULONG startIndex,dirIndex; UNICODE_STRING LongNameU,ShortNameU; DIR_ENTRY entry; } FCB;
typedef struct { ULONG StartIndex,DirIndex; UNICODE_STRING LongNameU,ShortNameU; DIR_ENTRY DirEntry; } CONTEXT;
static unsigned Checks,Released,Freed;
#define STATUS_SUCCESS 0
#define STATUS_UNSUCCESSFUL -1
#define TAG_NAME 0
#define DPRINT(...) ((void)0)
#define vfatFCBIsRoot(p) (*(p))
#define RtlCopyMemory memcpy
static void RtlCopyUnicodeString(UNICODE_STRING *a,const UNICODE_STRING *b){*a=*b;}
static void vfatReleaseFCB(void *d,FCB *f){(void)d;(void)f;++Released;}
static void ExFreePoolWithTag(void *p,int t){(void)p;(void)t;++Freed;}
static void check(int value){++Checks;if(!value){fprintf(stderr,"check %u failed\n",Checks);exit(2);}}
"""
def fun(name,b):return '\nstatic NTSTATUS '+name+'(FCB *rcFcb,CONTEXT *DirContext,int fatx,int root) {\n int IsFatX=fatx;int *Parent=&root; void *DeviceExt=NULL,*PathNameBuffer=NULL;NTSTATUS Status;\n'+b+'\nreturn STATUS_UNSUCCESSFUL;\n}\n'
test=r"""
int main(void){
 const ULONG indices[]={0,1,2,3,62,63,64,65,1023,65535,0x03fffffd};
 unsigned n;int fatx,root;FCB f={0};CONTEXT c={0};NTSTATUS rc;
 f.startIndex=7;f.dirIndex=7;c.DirIndex=0;
 check(original(&f,&c,1,0)==0&&c.DirIndex==7);
 c.DirIndex++;check(original(&f,&c,1,0)==0&&c.DirIndex==7);
 c.DirIndex++;check(original(&f,&c,1,0)==0&&c.DirIndex==7);
 for(fatx=0;fatx<2;++fatx)for(root=0;root<2;++root)for(n=0;n<sizeof(indices)/sizeof(indices[0]);++n){
  ULONG offset=fatx&&!root?2:0;ULONG cursor;
  f.startIndex=indices[n];f.dirIndex=indices[n];f.LongNameU.value=42;f.ShortNameU.value=19;f.entry.value=88;
  for(cursor=0;cursor<4;++cursor){
   memset(&c,0,sizeof(c));c.DirIndex=cursor==0?0:indices[n]+offset+cursor-1;
   ULONG before=c.DirIndex;unsigned released=Released,freed=Freed;
   rc=candidate(&f,&c,fatx,root);
   check(Released==released+1&&Freed==freed+1);
   check((rc==0)==(before<=indices[n]+offset));
   if(rc==0){
    check(c.DirIndex==indices[n]+offset&&c.StartIndex==indices[n]+offset);
    check(c.LongNameU.value==42&&c.ShortNameU.value==19&&c.DirEntry.value==88);
    check(c.StartIndex-offset==f.startIndex&&c.DirIndex-offset==f.dirIndex);
    c.DirIndex++;check(candidate(&f,&c,fatx,root)==STATUS_UNSUCCESSFUL);
   }
  }
 }
 check(Released==Freed);
 printf("{\"checks\":%u,\"balanced_release_cleanup\":%u,\"original_duplicate_reproduced\":true}\n",Checks,Released);
 return 0;
}
"""
p=out/'test.c';p.write_text(head+fun('original',block)+fun('candidate',fixed)+test)
cc=Path('/usr/bin/gcc');cmd=[str(cc),'-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(p),'-o',str(out/'test')]
r=subprocess.run(cmd,capture_output=True,text=True);(out/'compile-stdout.txt').write_text(r.stdout);(out/'compile-stderr.txt').write_text(r.stderr);assert r.returncode==0,r.stderr
r=subprocess.run([str(out/'test')],capture_output=True,text=True,timeout=30);(out/'stdout.txt').write_text(r.stdout);(out/'stderr.txt').write_text(r.stderr)
record={'scope':'Exact original cached-FCB branch with modeled strings/release/cleanup; proposed index normalization HOST ONLY; no driver build or physical result','source_sha256':hashlib.sha256(src.encode()).hexdigest(),'original_block_sha256':hashlib.sha256(block.encode()).hexdigest(),'harness_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'compiler':subprocess.check_output([str(cc),'--version'],text=True),'command':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
(K/'host001.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2));assert r.returncode==0
