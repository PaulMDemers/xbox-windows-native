"""Actual paint function, guarded buffers and independent expected pixels; no GPU."""
import hashlib,json,os,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/mnt/c/xwn430/host001')
assert not P.exists() and not (K/'host001.json').exists();P.mkdir()
s=(K/'main.c').read_text();paint=s[s.index('static void paint('):s.index('static int capture(')]
(P/'pattern.h').write_bytes((K/'pattern.h').read_bytes())
code='''#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include "pattern.h"
static unsigned flushes;
static void XVideoFlushFB(void){flushes++;}
'''+paint+'''
static unsigned expected(unsigned x,unsigned y,unsigned p){
 unsigned n=y+(p==1);
 if(x/320==0)return (n%2)*0xffffff;
 if(x/320==1)return ((n/2)%2)*0xffffff;
 if(x<960)return ((n/(1u<<((x-640)/32)))%2)*0xffffff;
 return n%2?0x00ff00:0xff00ff;
}
int main(void){
 unsigned long long checks=0;
 for(unsigned mode=0;mode<2;mode++){
  unsigned w=mode?1920:1280,h=mode?1080:720,n=w*h;
  uint32_t *a=malloc((n+2)*4);assert(a);a[0]=0x12345678;a[n+1]=0x87654321;
  for(unsigned p=0;p<4;p++)for(unsigned pos=0;pos<2;pos++){
   unsigned x0=pos?111:32,y0=pos?95:32;
   paint(a+1,w,h,p,x0,y0,mode);
   for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++){
    unsigned e=y<16?(mode?0xff8020:0x2040ff):0x202020;
    if(x>=x0&&x<x0+FW&&y>=y0&&y<y0+FH)e=expected(x-x0,y-y0,p);
    assert(a[1+y*w+x]==e);checks++;
   }
   assert(a[0]==0x12345678&&a[n+1]==0x87654321);checks+=2;
  }free(a);
 }assert(flushes==16);printf("%llu\\n",checks);return 0;
}
'''
(P/'host.c').write_text(code)
cmd=['gcc','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(P/'host.c'),'-o',str(P/'host')]
subprocess.run(cmd,check=True,timeout=60)
r=subprocess.run([str(P/'host')],check=True,capture_output=True,timeout=60,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result=dict(passed=True,checks=int(r.stdout),paint_sha256=hashlib.sha256(paint.encode()).hexdigest(),source_sha256=sha(K/'main.c'),pattern_sha256=sha(K/'pattern.h'),files={p.name:sha(p) for p in P.iterdir()},command=cmd,scope='Actual paint and independent color/bounds oracle, modeled flush, no video API execution')
(K/'host001.json').write_text(json.dumps(result,indent=2)+'\n');print(result['checks'])
