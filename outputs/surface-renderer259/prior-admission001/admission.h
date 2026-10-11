/* SPDX-License-Identifier: GPL-2.0-or-later
 * Pure admission checks shared with the future runtime collector. This code
 * does not collect evidence, lock a renderer, grant ownership or call GL.
 */
#ifndef X259_ADMISSION_H
#define X259_ADMISSION_H
#include <stdint.h>
#define X259_FAMILIES 7u
#define X259_MAX_REFS 2048u
enum {X259_SURFACE=0,X259_TEXTURE,X259_PALETTE,X259_VERTEX,X259_SCANOUT,X259_OVERLAY,X259_CALLBACK};
enum {X259_ACCEPT=0,X259_BAD_ARENA,X259_UNKNOWN,X259_BAD_RANGE,X259_OVERLAP,X259_BAD_AGE,X259_BUSY};
typedef struct {uint64_t begin,length,identity;uint32_t family;} X259Ref;
typedef struct {
    uint64_t physical,owner,virtual_base,pages[4],ram_bytes;
    uint32_t generation,closed,attempted,reads,writes;
    uint32_t complete_families,expected[X259_FAMILIES],count;
    uint32_t unclassified,pending_reports,pending_cpu_jobs,active_primitives;
    uint32_t producer_halted,cpu_stopped,frontend_closed,worker_joined;
    uint32_t render_fenced,display_fenced;
    int64_t frame_time;
} X259Admission;
/* AGE checks operate on one new test surface. Other ages are read-only. */
unsigned x259_admit(const X259Admission *,const X259Ref *,const int64_t *,uint32_t);
#endif
