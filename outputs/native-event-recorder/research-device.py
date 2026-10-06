"""Identify the exact emulator device from pinned local source and build records."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent
s=Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet')
revision='e72e76bd1f12ce45c6c63b4196c6918ea2cc705d'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=s,text=True).strip()==revision
rows=[]
for rel,needles in {
    'hw/xbox/xbox.c':['/* FIXME: Stub the memory controller */','pci_create_simple(pci_bus, PCI_DEVFN(0, 3), "pci-testdev");'],
    'include/hw/pci/pci.h':['PCI_VENDOR_ID_REDHAT             0x1b36','PCI_DEVICE_ID_REDHAT_TEST        0x0005'],
    'hw/misc/pci-testdev.c':['k->vendor_id = PCI_VENDOR_ID_REDHAT;','k->device_id = PCI_DEVICE_ID_REDHAT_TEST;',
        'k->class_id = PCI_CLASS_OTHERS;','pci_register_bar(pci_dev, 0, PCI_BASE_ADDRESS_SPACE_MEMORY, &d->mmio);',
        'pci_register_bar(pci_dev, 1, PCI_BASE_ADDRESS_SPACE_IO, &d->portio);'],
}.items():
    data=(s/rel).read_bytes()
    assert data==subprocess.check_output(['git','show','HEAD:'+rel],cwd=s)
    lines=data.decode().splitlines()
    hits=[]
    for needle in needles:
        found=[(i+1,line.strip()) for i,line in enumerate(lines) if needle in line]
        assert len(found)==1,(rel,needle)
        hits.append(dict(line=found[0][0],text=found[0][1]))
    rows.append(dict(path=rel,sha256=hashlib.sha256(data).hexdigest(),matches_git_revision=True,evidence=hits))
old=json.loads((k.parent/'native-windows-physical-f/xemu-resource-model-build.json').read_text())
binary=k.parent/'native-windows-physical-f/artifacts/xemu-resource-model.exe'
assert hashlib.sha256(binary.read_bytes()).hexdigest()==old['sha256']
r=dict(scope=__doc__,source_revision=revision,files=rows,recorded_failing_emulator_sha256=old['sha256'],
    identity=dict(vendor='1b36',device='0005',model='pci-testdev',bdf='00:00.3',
                  role='Placeholder created by xbox_init_common under a memory-controller FIXME',
                  class_name='PCI_CLASS_OTHERS',interrupt_pin=0,
                  default_bars=['BAR0: 4096-byte test MMIO region','BAR1: 256-byte test I/O region'],
                  optional_bar2='Only registered when the membar property is nonzero; default zero'),
    primary_sources=[
        'https://github.com/xemu-project/xemu/blob/'+revision+'/hw/xbox/xbox.c',
        'https://github.com/xemu-project/xemu/blob/'+revision+'/hw/misc/pci-testdev.c',
        'https://www.qemu.org/docs/master/specs/pci-ids.html',
        'https://www.qemu.org/docs/master/specs/pci-testdev.html'],
    conclusions=[
        'This device is unconditionally created by the pinned Xbox machine source, not added by this project Run.ps1.',
        'It is a generic test-device placeholder, not evidence of a physical Red Hat/QEMU device on the Xbox.',
        'The source-backed memory-controller placeholder explains the emulator-only device identity.',
        'Renaming its PCI IDs or removing it would be a separate model intervention, not a proven shutdown fix.',
        'No compatible Windows driver was found in the recorded fixture installation; QEMU test-device documentation does not supply one.',
    ],
    limits='Local source plus recorded build provenance, not a new live PCI configuration capture. Physical popup owner remains unknown.')
(k/'device-research.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['identity'])
