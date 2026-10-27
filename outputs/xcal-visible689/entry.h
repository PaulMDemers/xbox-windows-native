/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_ENTRY689_H
#define XWN_ENTRY689_H
#include <stdint.h>
struct entry689 {
    uint32_t magic, phase, error, completed;
    uint32_t flags, cr0, cr3, cr4, cs, ds, ss;
    uint32_t pci_selector, pci_id, pci_command, pci_bar;
    uint32_t status_before, status_after;
    uint32_t cable, standard, video_flags, encoder_value;
    uint32_t failed_address, failed_register;
};
enum { E689_CONTEXT=2001, E689_DEVICE, E689_MAPPING, E689_CONFIG };
int XcalCollect689(volatile struct entry689 *);
void XcalEntry689(void) __attribute__((noreturn));
extern volatile struct entry689 XcalState689;
#endif
