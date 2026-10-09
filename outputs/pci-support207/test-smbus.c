/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "smbus.h"
typedef struct model {
    unsigned initial, final, starts, writes, reads, delay, aborts, data_reads;
    unsigned collision_count, busy_polls, timeout, stuck, high_busy;
    unsigned regs[16];
} model;
static xwn_u16 read16(void *ctx, unsigned reg)
{
    model *m = ctx; assert(reg == 0); ++m->reads;
    if (!m->starts) return (xwn_u16)m->initial;
    if (m->aborts) return m->stuck ? 8 : 1;
    if (m->timeout) return 8;
    if (m->busy_polls) { --m->busy_polls; return m->high_busy ? 0x800 : 8; }
    return (xwn_u16)(m->starts <= m->collision_count ? 2 : m->final);
}
static xwn_u8 read8(void *ctx, unsigned reg)
{
    model *m = ctx; assert(reg == 2 || reg == 6);
    if (reg == 6) { ++m->data_reads; return 0x2a; }
    return (xwn_u8)m->regs[reg];
}
static void write8(void *ctx, unsigned reg, xwn_u8 value)
{
    model *m = ctx; ++m->writes; assert(reg == 0 || reg == 2 || reg == 4 || reg == 8);
    if (reg == 2 && (value & 8)) { assert(value == 0x0a); ++m->starts; }
    if (reg == 2 && (value & 0x20)) ++m->aborts;
    if (reg == 4) assert(value & 1); /* Never a slave write */
    m->regs[reg] = value;
}
static void delay(void *ctx) { ++((model *)ctx)->delay; }
int main(void)
{
    model m; xwn_smb_reply r; unsigned status, count = 0;
    xwn_smb_io io = {&m, read8, read16, write8, delay};
    for (status = 0; status < 64; ++status) {
        if (!(status & 0x37) || (status & 8)) continue;
        memset(&m, 0, sizeof(m)); m.final = status;
        r = xwn_smb_read(&io, 0x10, 4);
        assert((r.result == XWN_SMB_OK) == ((status & 0x37) == 0x10));
        assert(m.data_reads == (r.result == XWN_SMB_OK));
        assert(r.attempts <= 3 && r.polls <= 3); ++count;
    }
    for (status = 0; status < 2048; ++status) {
        memset(&m, 0, sizeof(m)); m.final = 0x10; m.busy_polls = status;
        m.high_busy = status & 1;
        r = xwn_smb_read(&io, 0x4c, status & 1);
        assert(r.result == XWN_SMB_OK && r.data == 0x2a && r.polls == status + 1); ++count;
    }
    memset(&m, 0, sizeof(m)); m.initial = 0x800;
    r = xwn_smb_read(&io, 0x10, 4); assert(r.result == XWN_SMB_BUSY && !m.writes); ++count;
    memset(&m, 0, sizeof(m)); m.initial = 8;
    r = xwn_smb_read(&io, 0x10, 4); assert(r.result == XWN_SMB_BUSY && !m.writes); ++count;
    memset(&m, 0, sizeof(m)); m.final = 0x10; m.collision_count = 2;
    r = xwn_smb_read(&io, 0x10, 4); assert(r.result == XWN_SMB_OK && r.attempts == 3); ++count;
    memset(&m, 0, sizeof(m)); m.timeout = 1;
    r = xwn_smb_read(&io, 0x10, 4); assert(r.result == XWN_SMB_TIMEOUT && m.aborts == 1 && r.polls == 10001); ++count;
    memset(&m, 0, sizeof(m)); m.timeout = m.stuck = 1;
    r = xwn_smb_read(&io, 0x10, 4); assert(r.result == XWN_SMB_STUCK && r.polls == 11000 && m.regs[2] == 0x20); ++count;
    for (status = 0; status < 65536; ++status) {
        unsigned address = status >> 8, command = status & 255;
        if (xwn_smb_allowed(address, command)) continue;
        memset(&m, 0, sizeof(m));
        r = xwn_smb_read(&io, address, command);
        assert(r.result == XWN_SMB_INVALID && !m.reads && !m.writes); ++count;
    }
    printf("{\"cases\":%u,\"passed\":true,\"scope\":\"host transaction engine only\"}\n", count);
    return 0;
}
