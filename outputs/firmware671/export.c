/* SPDX-License-Identifier: GPL-2.0-or-later
 * Diagnostic-only terminal export. No deployment is authorized by this file.
 * Hardware capture has already returned. Freeze maskable interrupt producers
 * BEFORE copying their saved RAM; record this new boundary explicitly.
 */
#include "boot.h"
#include "BootEEPROM.h"
#include "integration.h"
#include "classify.h"
#include "xwn_hd_adapter.h"
#include "trace649.h"
#include "readback651.h"
#include "identity657.h"
extern EEPROMDATA eeprom;
extern void BootDetectMemorySize(void);
volatile struct boundary667 Memory667;
/* Retain667's observation around the original memory-detection call. */
__attribute__((noinline)) void XwnMemoryBoundary667(void){
 unsigned f;
 __asm__ __volatile__("pushfl; popl %0":"=r"(f)::"memory");
 Memory667.before=f;Memory667.valid_before=0x667b0001;
 BootDetectMemorySize();
 __asm__ __volatile__("pushfl; popl %0":"=r"(f)::"memory");
 Memory667.after=f;Memory667.valid_after=0x667a0001;
}
extern void xwn652_bridge(struct xwn652_data *,int,unsigned,const struct xwn_hd_request *,
 const volatile struct xwn_hd_state *,const volatile struct xwn_trace649 *,
 const volatile struct readback651 *,const volatile struct readback651 *);
struct xwn652_data Frozen671;
struct config670 Config671;
uint32_t FreezeBefore671,FreezeAfter671;
volatile unsigned Owner671,Phase671,FreezeError671,PrepareError671;
__attribute__((noreturn)) void XwnExport657(int result,const struct xwn_hd_request *request,
 const volatile struct xwn_hd_state *state,const volatile struct xwn_trace649 *trace,
 const volatile struct readback651 *pre,const volatile struct readback651 *post){
 unsigned i;
 /* One owner only. A nested/repeated diagnostic is terminal, never a retry.
  * Capture before this boundary can have been interrupted; do not claim that
  * this operation retroactively makes those earlier observations atomic. */
 if(!__sync_bool_compare_and_swap(&Owner671,0,1))irq_hold669();
 Phase671=1;
 FreezeError671=(unsigned)irq_enter669(0,&FreezeBefore671,&FreezeAfter671);
 if(FreezeError671 || FreezeAfter671!=(FreezeBefore671&~0x200u) || (irq_flags669(0)&0x200u))irq_hold669();
 Phase671=2;
 xwn652_bridge(&Frozen671,result,result<0?2:1,request,state,trace,pre,post);
 for(i=0;i<6;i++)Config671.mac[i]=eeprom.MACAddress[i];
 for(i=0;i<4;i++)Config671.ip[i]=SourceIP657[i];
 Config671.port=Port657;
 Phase671=3;PrepareError671=prepare670(&Identity657,&Frozen671);
 if(PrepareError671)irq_hold669();
 Phase671=4;terminal670(&Config671);
}
