/* SPDX-License-Identifier: MIT
 * Read-only port observations. No PCI, SMBus command, interrupt or timer writes. */
#include <stdint.h>
uint32_t raw_pm(void *unused)
{
    uint32_t v; (void)unused;
    __asm__ volatile ("inl %w1, %0" : "=a"(v) : "d"((uint16_t)0x8008));
    return v;
}
uint16_t raw_smbus_status(void)
{
    uint16_t v;
    __asm__ volatile ("inw %w1, %0" : "=a"(v) : "d"((uint16_t)0xc000));
    return v;
}
uint64_t raw_tsc(void *unused)
{
    uint32_t lo,hi; (void)unused;
    __asm__ volatile ("rdtsc" : "=a"(lo), "=d"(hi));
    return ((uint64_t)hi << 32) | lo;
}
