/* SPDX-License-Identifier: MIT
 * Xbox-specific PCI inventory. Never probe 00:00.1/2: physical chipset hang.
 * See ReactOS HalpXboxBlacklistedPCISlot in hal/halx86/legacy/bus/pcibus.c.
 */
#ifndef XWN_PCI_POLICY_H
#define XWN_PCI_POLICY_H
static const struct { unsigned bus, dev, fn; } pci_targets[] = {
    {0,0,0}, {0,0,3}, {0,1,0}, {0,1,1}, {0,2,0}, {0,3,0},
    {0,4,0}, {0,5,0}, {0,6,0}, {0,9,0}, {0,30,0}, {1,0,0}
};
static int pci_target_allowed(unsigned bus,unsigned dev,unsigned fn)
{
    if ((bus==0 && dev==0 && (fn==1 || fn==2)) || (bus==1 && dev!=0)) return 0;
    for (unsigned i=0;i<sizeof(pci_targets)/sizeof(pci_targets[0]);++i)
        if (pci_targets[i].bus==bus && pci_targets[i].dev==dev && pci_targets[i].fn==fn) return 1;
    return 0;
}
#endif
