/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_NET656_H
#define XWN_NET656_H
#include <stdint.h>
#define OFF656(type,member) __builtin_offsetof(type,member)
typedef char u32_size656[sizeof(uint32_t)==4?1:-1];
#define N656_FRAME 814u
#define N656_BUFFER 1536u
struct desc656 { uint32_t address; uint16_t length; volatile uint16_t flags; };
struct dma656 {
    struct desc656 tx[2]; uint8_t pad[16]; struct desc656 rx[4];
    uint8_t txbuf[2][N656_BUFFER],rxbuf[4][N656_BUFFER];
} __attribute__((aligned(32)));
struct io656 {
    void *p;
    int (*read)(void *,unsigned,uint32_t *);
    int (*write)(void *,unsigned,uint32_t);
    int (*command)(void *,uint16_t); /* PCI command WORD only, then readback */
    uint32_t (*ticks)(void *); /* one raw 32-bit 3.579545 MHz timer read */
    void (*sync)(void *); /* native cache publication/invalidation, never a wait */
};
struct plan656 {
    uint32_t dma_bus; uint16_t command;
    uint8_t mac[6],source_ip[4]; uint16_t port;
    unsigned post_capture,admitted;
};
struct result656 {
    unsigned used,error,cleanup_error,mutated,published,completed,safe_to_continue;
    unsigned reads,writes,timer_reads,cache_syncs,phy,phase,failed_phase;
    uint32_t last_reg,last_value;
};
enum error656 { N656_OK,N656_ARGUMENT,N656_ALREADY,N656_IO,N656_TIMER,
 N656_STOP,N656_SETUP,N656_PHY,N656_LINK,N656_DESCRIPTOR,N656_TX_TIMEOUT,N656_TX_ERROR };
/* All callbacks must themselves terminate. Native admission is separate.
 * Three identical fixed-size records maximum; one-shot even after failure.
 * DMA memory belongs exclusively to this call and cannot be reused on unsafe exit.
 */
int send656(const struct io656 *,const struct plan656 *,struct dma656 *,
            const uint8_t *,unsigned,struct result656 *);
int delay656(const struct io656 *,struct result656 *,unsigned);
int frame656(uint8_t *,unsigned,const struct plan656 *,const uint8_t *,unsigned);
#endif
