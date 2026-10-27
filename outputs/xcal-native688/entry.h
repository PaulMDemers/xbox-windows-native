/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_ENTRY688_H
#define XWN_ENTRY688_H
#include <stdint.h>
struct entry688 {
    uint32_t magic, phase, error, completed;
    uint32_t flags, cr0, cr3, cr4, cs, ds, ss;
    uint32_t pci_selector, pci_id, pci_command, pci_bar;
    uint32_t status_before, status_after;
    uint32_t cable, standard, video_flags, encoder_value;
    uint32_t failed_address, failed_register;
};
enum { E688_CONTEXT=2001, E688_DEVICE, E688_MAPPING, E688_CONFIG };
int XcalCollect688(volatile struct entry688 *);
void XcalEntry688(void) __attribute__((noreturn));
extern volatile struct entry688 XcalState688;
#endif
