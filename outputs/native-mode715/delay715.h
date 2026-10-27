/* SPDX-License-Identifier: MIT
 * Bounded diagnostic interval at the separately admitted kernel3375000Hz rate.
 * One nominal second, not independent clock calibration. Reject discontinuities
 * including24-bit wrap; caller must attempt restoration even on failure.
 */
#ifndef XWN_DELAY715_H
#define XWN_DELAY715_H
#include "delay_candidate.h"
static enum delay_result wait715(uint32_t (*read_tick)(void *),void *ctx,
 struct delay_observation *o)
{
 if(!read_tick||!o)return DELAY_ARGUMENT;
 o->first=read_tick(ctx);o->last=o->first;o->elapsed=0;o->reads=1;
 for(unsigned i=0;i<1000000;++i){
  uint32_t now=read_tick(ctx),step=now-o->last;
  o->last=now;o->elapsed=now-o->first;++o->reads;
  if(step>33750||o->elapsed>3408750)return DELAY_DISCONTINUITY;
  if(o->elapsed>=3375000)return DELAY_OK;
 }
 return DELAY_LIMIT;
}
#endif
