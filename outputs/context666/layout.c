/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <stddef.h>
#include <stdio.h>
#include "readback651.h"
#include "receipt.h"
#include "admission.h"
typedef char RBSize[sizeof(struct readback651)==188?1:-1];
typedef char RBCaptured[offsetof(struct readback651,captured)==0?1:-1];
typedef char RBBefore[offsetof(struct readback651,flags_before)==16?1:-1];
typedef char RBAfter[offsetof(struct readback651,flags_after)==20?1:-1];
typedef char Pre[offsetof(struct xwn652_data,pre)==328?1:-1];
typedef char Post[offsetof(struct xwn652_data,post)==516?1:-1];
typedef char Adm[offsetof(struct admission656,flags)==4?1:-1];
int main(void){puts("{\"readback_bytes\":188,\"captured_offset\":0,\"flags_before_offset\":16,\"flags_after_offset\":20,\"pre_offset\":328,\"post_offset\":516,\"admission_flags_offset\":4}");return 0;}
