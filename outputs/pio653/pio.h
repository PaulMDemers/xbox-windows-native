/* SPDX-License-Identifier: GPL-2.0-or-later
 * Diskless prototype: no physical port bindings or deployment authorization.
 */
#ifndef XWN_PIO653_H
#define XWN_PIO653_H
#include <stdint.h>
enum reg653 { DATA653, COUNT653, LBA0653, LBA1653, LBA2653, DEVICE653,
              STATUS_COMMAND653, ALT653, BM_COMMAND653, BM_STATUS653 };
struct io653 {
    void *opaque;
    int (*read8)(void *,unsigned,uint8_t *);
    int (*read16)(void *,unsigned,uint16_t *);
    int (*write8)(void *,unsigned,uint8_t);
    int (*write16)(void *,unsigned,uint16_t);
    /* Future binding must prove >=400ns AND a finite bound. No timer assumed. */
    int (*settle)(void *);
    uint32_t (*flags)(void *);
};
struct plan653 {
    uint32_t disk_sectors,partition_start,partition_sectors,data_start;
    uint32_t sector[3],poll_limit;
    /* Must remain zero in any unreviewed/native caller. Normal ATA status reads
     * acknowledge interrupts. They are modeled here, never hidden as pure reads.
     */
    uint32_t permit_status_ack;
};
struct pio653 {
    struct io653 io;struct plan653 plan;
    unsigned poisoned,admitted,step;
    uint32_t status_reads,ack_reads,data_words,commands;
    uint8_t last_status,last_bm;
};
enum error653 { OK653, ARG653, POLICY653, POISON653, IO653, BUS653, TIMEOUT653,
                STATUS653, IDENTITY653, ORDER653, MAP653 };
/* Geometric checks only. Not proof of live FATX ownership/non-overlap. */
int map653(const struct plan653 *);
/* One IDENTIFY transaction, exact match against independent private512-byte
 * identity, LBA/flush support and capacity. No sector write before admission.
 */
int admit653(struct pio653 *,const struct io653 *,const struct plan653 *,const uint8_t *);
/* Bind these callbacks to receipt652 only after independent allocation proof.
 * Enforces RRRWWFRRWFRRR, three explicit sector addresses and single-sector PIO.
 * Every error poisons the session; no recovery/reset/retry/control-register write.
 */
int read653(void *,unsigned,uint8_t *);
int write653(void *,unsigned,const uint8_t *);
int flush653(void *);
#endif
