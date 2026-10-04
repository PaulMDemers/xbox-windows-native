"""Apply an opt-in, framebuffer-only PCI view for the observed unassigned BAR2."""
from pathlib import Path
import json, subprocess
k=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-f')
s=Path('/home/paul/xbox-windows-native/sources/reactos-extended')
m=json.loads((k/'patch-check-0073.json').read_text())
assert subprocess.check_output(['git','-C',str(s),'write-tree']).decode().strip()==m['result_tree']
assert not subprocess.check_output(['git','-C',str(s),'diff'])
p=s/'hal/halx86/legacy/bus/pcibus.c';t=p.read_text()
t=t.replace('PCI_CONFIG_HANDLER PCIConfigHandler;', '''PCI_CONFIG_HANDLER PCIConfigHandler;
#ifdef XBOX_NT5_FRAMEBUFFER_ONLY_PCI
/* Protected by the existing PCI configuration lock: 0 unknown, 1 mask, 2 pass. */
static ULONG HalpXboxFramebufferPciState;
#endif''',1)
needle='    /* Loop every increment */\n    while (Length)\n    {'
assert t.count(needle)==1
t=t.replace(needle,'''#ifdef XBOX_NT5_FRAMEBUFFER_ONLY_PCI
    /* This HAL is paired with the BAR0/BAR1-only framebuffer miniport. The
     * observed NV2A has an unassigned extra prefetch BAR, while its bridge
     * aperture is entirely occupied by BAR1. NT5 cannot start that resource
     * set. Omit BAR2 from this software view without changing its hardware
     * value, sizing it, or copying a different bridge configuration.
     *
     * Latch under the configuration lock BEFORE the first sizing/write cycle.
     * A different device, assigned BAR2 or different boot layout passes through.
     * An accelerated GPU driver must not use this framebuffer-only option.
     */
    if (Length && BusHandler->BusNumber == 1 && Slot.u.AsULONG == 0 &&
        !HalpXboxFramebufferPciState)
    {
        ULONG Id, Header, Bar0, Bar1, Bar2;
        PCIConfigHandler.ConfigRead[0](BusHandler->BusData, State, (PUCHAR)&Id, 0);
        PCIConfigHandler.ConfigRead[0](BusHandler->BusData, State, (PUCHAR)&Header, 12);
        PCIConfigHandler.ConfigRead[0](BusHandler->BusData, State, (PUCHAR)&Bar0, 16);
        PCIConfigHandler.ConfigRead[0](BusHandler->BusData, State, (PUCHAR)&Bar1, 20);
        PCIConfigHandler.ConfigRead[0](BusHandler->BusData, State, (PUCHAR)&Bar2, 24);
        HalpXboxFramebufferPciState =
            (Id == 0x02a010de && !(Header & 0x00ff0000) &&
             Bar0 == 0xfd000000 && Bar1 == 0xf0000008 && Bar2 == 8) ? 1 : 2;
    }
#endif

    /* Loop every increment */
    while (Length)
    {
#ifdef XBOX_NT5_FRAMEBUFFER_ONLY_PCI
        if (HalpXboxFramebufferPciState == 1 && BusHandler->BusNumber == 1 &&
            Slot.u.AsULONG == 0 && Offset >= 24 && Offset < 28)
        {
            /* Native access chunks never cross a DWORD boundary. Preserve
             * surrounding bytes for every partial or bulk header access. */
            if (ConfigIO == PCIConfigHandler.ConfigRead) *Buffer = 0;
            ++Offset;
            ++Buffer;
            --Length;
            continue;
        }
#endif''',1)
p.write_text(t)
p=s/'hal/halx86/xboxnt5/CMakeLists.txt'
p.write_text(p.read_text()+'''
option(XBOX_NT5_FRAMEBUFFER_ONLY_PCI "Omit the observed unassigned NV2A BAR2 for the framebuffer-only miniport" OFF)
if(XBOX_NT5_FRAMEBUFFER_ONLY_PCI)
    target_compile_definitions(halxboxnt5 PRIVATE XBOX_NT5_FRAMEBUFFER_ONLY_PCI=1)
endif()
''')
patch=k/'0074-nt5-framebuffer-pci-view.patch'
patch.write_bytes(subprocess.check_output(['git','-C',str(s),'diff']))
subprocess.run(['git','-C',str(s),'add','hal/halx86/legacy/bus/pcibus.c','hal/halx86/xboxnt5/CMakeLists.txt'],check=True)
m.update(previous_tree=m['result_tree'],result_tree=subprocess.check_output(['git','-C',str(s),'write-tree']).decode().strip(),clean_index_replay_verified=False)
m['patches'].append('outputs/native-windows-physical-f/'+patch.name)
(k/'patch-check-0074.json').write_text(json.dumps(m,indent=2)+'\n');print(m['result_tree'])
