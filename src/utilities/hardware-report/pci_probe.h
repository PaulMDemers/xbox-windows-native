/* SPDX-License-Identifier: MIT
 * Original inventory policy using documented Xbox PCI hardware constraints.
 * Hardware facts: ReactOS7c35fc4ead884e1bd0640a9613f652c40bca8b2e,
 * hal/halx86/legacy/bus/pcibus.c: HalpXboxBlacklistedPCISlot.
 * 00:00.1/.2 config cycles can hang hardware. Bus1 device aliases are omitted.
 * These addresses are unprobed, not reported as absent devices.
 */
#ifndef XWN_PCI_PROBE_H
#define XWN_PCI_PROBE_H
static int xwn_pci_probe_allowed(unsigned bus, unsigned device, unsigned function)
{
    if (device >= 32 || function >= 8) return 0;
    switch (bus) {
    case 0:
        if (device != 0) return 1;
        return function == 0 || function >= 3;
    case 1:
        return device == 0;
    default:
        return 0;
    }
}
#endif
