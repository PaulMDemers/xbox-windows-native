/* SPDX-License-Identifier: MIT
 * Bounded MCPX byte-data read engine. The caller owns/serializes the controller,
 * pins its resources and prevents power/remove while this synchronous call runs.
 * No slave writes, EEPROM reads or SMC read-to-clear commands are exposed here.
 */
#ifndef XWN_SMBUS207_H
#define XWN_SMBUS207_H
typedef unsigned char xwn_u8;
typedef unsigned short xwn_u16;
typedef struct xwn_smb_io {
    void *context;
    xwn_u8 (*read8)(void *, unsigned);
    xwn_u16 (*read16)(void *, unsigned);
    void (*write8)(void *, unsigned, xwn_u8);
    void (*delay10us)(void *);
} xwn_smb_io;
enum xwn_smb_result {
    XWN_SMB_OK, XWN_SMB_INVALID, XWN_SMB_BUSY, XWN_SMB_PROTOCOL,
    XWN_SMB_COLLISION, XWN_SMB_TIMEOUT, XWN_SMB_ABORTED, XWN_SMB_STUCK
};
typedef struct xwn_smb_reply {
    unsigned result, polls, attempts;
    xwn_u16 status;
    xwn_u8 data;
} xwn_smb_reply;
/* Only passive telemetry: SMC AV pack and ADM1032 local/remote temperature.
 * Not all Xbox revisions contain an ADM1032. NACK is an honest failure.
 */
static int xwn_smb_allowed(unsigned address, unsigned command)
{
    return (address == 0x10 && command == 0x04) ||
           (address == 0x4c && (command == 0 || command == 1));
}
static xwn_smb_reply xwn_smb_read(const xwn_smb_io *io, unsigned address,
                                 unsigned command)
{
    xwn_smb_reply r = {XWN_SMB_INVALID, 0, 0, 0, 0};
    unsigned n;
    xwn_u8 control;
    if (!io || !io->read8 || !io->read16 || !io->write8 || !io->delay10us ||
        !xwn_smb_allowed(address, command)) return r;
    /* Never clear/abort a transaction which was already owned by another master. */
    r.status = io->read16(io->context, 0);
    if (r.status & 0x808) { r.result = XWN_SMB_BUSY; return r; }
    control = io->read8(io->context, 2) & 0x17; /* omit start/abort strobes */
    for (r.attempts = 1; r.attempts <= 3; ++r.attempts) {
        /* Collision retry must also respect a newly busy external master. */
        r.status = io->read16(io->context, 0);
        if (r.status & 0x808) { r.result = XWN_SMB_BUSY; break; }
        io->write8(io->context, 0, 0x37); /* W1C, no busy bits */
        io->write8(io->context, 4, (xwn_u8)((address << 1) | 1));
        io->write8(io->context, 8, (xwn_u8)command);
        io->write8(io->context, 2, 0x0a); /* BYTE_DATA, START, polling */
        for (n = 0; n < 10000; ++n) {
            r.status = io->read16(io->context, 0); ++r.polls;
            if (!(r.status & 0x808) && (r.status & 0x37)) break;
            io->delay10us(io->context);
        }
        if (n == 10000) {
            /* We started this transaction. Abort and wait boundedly for idle. */
            io->write8(io->context, 2, 0x20);
            for (n = 0; n < 1000; ++n) {
                r.status = io->read16(io->context, 0); ++r.polls;
                if (!(r.status & 0x808)) break;
                io->delay10us(io->context);
            }
            r.result = n == 1000 ? XWN_SMB_STUCK : XWN_SMB_TIMEOUT;
            break;
        }
        /* An error wins even if the completion bit is also set. */
        if (r.status & 0x20) r.result = XWN_SMB_TIMEOUT;
        else if (r.status & 0x04) r.result = XWN_SMB_PROTOCOL;
        else if (r.status & 0x01) r.result = XWN_SMB_ABORTED;
        else if (r.status & 0x02) r.result = XWN_SMB_COLLISION;
        else { r.data = io->read8(io->context, 6); r.result = XWN_SMB_OK; }
        if (r.result != XWN_SMB_COLLISION || r.attempts == 3) break;
        io->delay10us(io->context);
    }
    /* A stuck engine requires caller quarantine; do not issue more strobes. */
    if (r.result != XWN_SMB_STUCK && r.result != XWN_SMB_BUSY) {
        io->write8(io->context, 0, 0x37);
        io->write8(io->context, 2, control);
    }
    return r;
}
#endif
