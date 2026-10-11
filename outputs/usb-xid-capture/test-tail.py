"""Exercise the actual guarded OHCI cancellation walk with real and dummy TDs."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent
s=(k/'artifacts/build003/ohci_guarded.c').read_text()
start=s.index('                while (td != NULL)\n                {\n                    /* The queue')
brace=s.index('{',start);depth=1;end=brace+1
while depth:
 if s[end]=='{':depth+=1
 elif s[end]=='}':depth-=1
 end+=1
block=s[start:end]
prefix=r'''
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <stddef.h>
#define USBH_ERR_ABORT -205
typedef struct utr {int td_cnt,status,bIsTransferDone;void (*func)(struct utr*);} UTR_T;
typedef struct td {UTR_T *utr;uintptr_t NextTD;} TD_T;
typedef struct {uint32_t TailP;} ED_T;
static TD_T nodes[2];static int freed[2],callbacks;
static void *virt_to_dma(TD_T *p){return (void*)(uintptr_t)(p==&nodes[0]?16:32);}
static TD_T *dma_to_virt(TD_T *p){return p==(TD_T*)16?&nodes[0]:p==(TD_T*)32?&nodes[1]:NULL;}
static void free_ohci_TD(TD_T *p){freed[p==&nodes[0]?0:1]++;}
static void callback(UTR_T *u){assert(u->td_cnt==0&&u->bIsTransferDone);callbacks++;}
int main(void){int cases=0;for(int tail_only=0;tail_only<2;tail_only++)for(int dummy_owner=0;dummy_owner<2;dummy_owner++){
 UTR_T u={1,0,0,callback},*utr;ED_T ed={32},*ed_p=&ed;TD_T *td,*td_next;
 nodes[0]=(TD_T){&u,32};nodes[1]=(TD_T){dummy_owner?&u:NULL,0};td=&nodes[tail_only];
 freed[0]=freed[1]=callbacks=0;
'''
suffix=r'''
 assert(freed[0]==!tail_only&&freed[1]==1&&callbacks==!tail_only);
 assert(u.td_cnt==tail_only&&u.bIsTransferDone==!tail_only);
 if(!tail_only)assert(u.status==USBH_ERR_ABORT);
 cases++;
}printf("%d dummy-tail cancellation cases passed\n",cases);return 0;}
'''
d=k/'artifacts/tail-test';d.mkdir(exist_ok=True);(d/'test.c').write_text(prefix+block+suffix)
subprocess.run(['C:/msys64/mingw64/bin/gcc.exe','-std=c11','-Wall','-Wextra','-Werror','-Wno-pointer-to-int-cast',str(d/'test.c'),'-o',str(d/'test.exe')],check=True)
reply=subprocess.check_output([str(d/'test.exe')]).decode().strip();assert reply=='4 dummy-tail cancellation cases passed'
(k/'tail-tests.json').write_text(json.dumps(dict(passed=True,cases=4,tested_block_sha256=hashlib.sha256(block.encode()).hexdigest(),scope='Actual cancellation walk with empty/active queues and NULL/shared dummy-tail owners; no controller timing claim.'),indent=2)+'\n');print(reply)
