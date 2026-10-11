"""Compile the actual guarded control function with deterministic completion faults."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;build=k/'artifacts/build002'
source=(build/'usb_core_guarded.c').read_text()
start=source.index('int usbh_ctrl_xfer(');end=source.index('\n}\n',start)+2
function=source[start:end]
prefix=r'''
#include <stdint.h>
#include <stdlib.h>
#include <assert.h>
#include <setjmp.h>
#include <stdio.h>
#define USBH_ERR_MEMORY_OUT -10
#define USBH_ERR_TIMEOUT -203
typedef struct {void *hw_pipe;} EP;
typedef struct utr_t UTR_T;
typedef struct {int (*ctrl_xfer)(UTR_T*);} HC;
typedef struct {HC *hc_driver;EP ep0;} UDEV_T;
struct utr_t {struct {uint8_t bmRequestType,bRequest;uint16_t wValue,wIndex,wLength;} setup;
 uint8_t *buff;uint32_t data_len,xfer_len;volatile uint8_t bIsTransferDone;int status;};
static UTR_T req;static int ticks,freed,cancelled,mode,delay,after_cancel,guarded,calls;static jmp_buf jump;
static UTR_T *alloc_utr(UDEV_T *d){(void)d;req=(UTR_T){0};return &req;}
static void free_utr(UTR_T *r){assert(r==&req);assert(mode==0||r->bIsTransferDone);freed++;}
static uint32_t get_ticks(void){assert(++calls<1000);ticks++;if(mode==2 && ticks==3){req.bIsTransferDone=1;req.xfer_len=16;}if(cancelled && ++after_cancel>=delay && delay>=0)req.bIsTransferDone=1;return ticks;}
static void delay_us(int n){assert(n==1000);}
static int usbh_quit_utr(UTR_T *r){assert(r==&req);cancelled++;return 0;}
__attribute__((noreturn)) void xid_guard_reboot(void){guarded++;longjmp(jump,1);}
static int submit(UTR_T *r){if(mode==0)return -201;if(mode==1){r->bIsTransferDone=1;r->xfer_len=16;}return 0;}
'''
suffix=r'''
int main(void){HC hc={submit};UDEV_T d={&hc,{0}};unsigned char b[16];uint32_t n;int cases=0;
 for(int m=0;m<4;m++)for(int z=-1;z<=105;z++){
  mode=m;delay=z;ticks=freed=cancelled=after_cancel=guarded=calls=0;
  if(!setjmp(jump)){
   int status=usbh_ctrl_xfer(&d,0xc1,6,0x4200,0,16,b,&n,2);
   assert(freed==1&&!guarded);
   if(m==0)assert(status==-201&&n==0&&!cancelled);
   else if(m<3)assert(status==0&&n==16&&!cancelled);
   else assert(status==USBH_ERR_TIMEOUT&&cancelled==1&&req.bIsTransferDone&&n==0);
  }else assert(m==3&&cancelled==1&&!freed&&guarded==1&&!req.bIsTransferDone);
  cases++;
 }
 printf("%d control ownership cases passed\n",cases);return 0;}
'''
dest=k/'artifacts/guard-test';dest.mkdir(exist_ok=True)
(dest/'test.c').write_text(prefix+function+suffix)
subprocess.run(['C:/msys64/mingw64/bin/gcc.exe','-std=c11','-Wall','-Wextra','-Werror',str(dest/'test.c'),'-o',str(dest/'test.exe')],check=True)
reply=subprocess.check_output([str(dest/'test.exe')]).decode().strip();assert reply=='428 control ownership cases passed'
r=dict(passed=True,cases=428,tested_function_sha256=hashlib.sha256(function.encode()).hexdigest(),scope='Actual guarded control function, deterministic submit/completion/cancel/no-drain faults. No hardware or IRQ timing claim.',output=reply)
(k/'guard-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(reply)
