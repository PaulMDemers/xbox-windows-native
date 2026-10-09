"""Pin actual compiled xemu hardware IDs independently of generic wizard labels."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'identity-reference.json';assert not dest.exists()
manifest=ws/'outputs/xemu-cpu-surface-evict/build003/candidate-source-pins.json';pins=json.loads(manifest.read_text());root='/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet/'
files={}
for n in ['include/hw/pci/pci_ids.h','hw/xbox/mcpx/apu/apu.c','hw/xbox/xbox_pci.c']:
 b=subprocess.check_output(['wsl','-d','Ubuntu','--','cat',root+n]);digest=hashlib.sha256(b).hexdigest();assert digest==pins[n],n
 lines=b.decode().splitlines();selected=[dict(line=i+1,text=s) for i,s in enumerate(lines) if any(v in s for v in ['PCI_DEVICE_ID_NVIDIA_MCPX_APU','PCI_DEVICE_ID_NVIDIA_NFORCE_SMBUS'])]
 files[n]=dict(sha256=digest,matched_compiled_source_manifest=True,selected_lines=selected)
ids=files['include/hw/pci/pci_ids.h']['selected_lines'];assert any('0x01b0' in v['text'] for v in ids) and any('0x01b4' in v['text'] for v in ids)
r=dict(passed=True,source_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),sources=files,
 reference='https://learn.microsoft.com/en-us/windows-hardware/drivers/install/installing-a-null-driver',
 limits='Matched actual xemu compilation source IDs support emulator device labels; generic physical wizard labels and absence of a function driver do not establish audio/SMBus functionality.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Actual compiled xemu APU/SMBus identities pinned')
