"""Read-only audit of retained source and link map; no runtime reopens."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
K=Path(__file__).resolve().parent;S=Path('C:/xwn651/source001')
assert not (K/'source-audit001.json').exists()
tree=subprocess.check_output(['git','-C',str(S),'write-tree'],text=True).strip()
assert tree=='2fda813f3b8109dfc6b70f6d37e21d2cf9a66d55'
assert not subprocess.check_output(['git','-C',str(S),'diff','--name-only'])
paths={
 'Makefile':['ETHERBOOT :='],
 'boot/BootResetAction.c':['BootVgaInitializationKernelNG','BootPciInterruptEnable','0xfef000a8','BootIde'],
 'drivers/pci/pci.c':['Ethernet','0xfef00000'],
 'drivers/video/xwn_hd_adapter.c':['s->error=','s->stage=','return 0;'],
 'etherboot/arch/i386/core/xbox.c':['virt_offset','eth_probe','eth_load_configuration','wait_us'],
 'etherboot/arch/i386/include/io.h':['virt_to_phys','virt_to_bus'],
 'etherboot/core/nic.c':['int ip_transmit','IP_BROADCAST','int udp_transmit','return 1;'],
 'etherboot/drivers/net/forcedeth.c':['reg_delay','forcedeth_reset','set_multicast','start_rx(nic);','forcedeth_transmit','forcedeth_disable','return 1;'],
}
files={}
for rel,anchors in paths.items():
    p=S/rel;b=p.read_bytes();lines=b.decode().splitlines()
    files[rel]=dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),
                   anchors={a:[i for i,line in enumerate(lines,1) if a in line] for a in anchors})
m=Path('C:/xwn654/build001/image-crom.map');b=m.read_bytes()
maplines=b.decode().splitlines()
selected=[line for line in maplines if any('/'+n+'.o' in line for n in ('forcedeth','nic','xbox'))]
r=dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_tree=tree,files=files,
       retained654_map_sha256=hashlib.sha256(b).hexdigest(),linked_object_evidence=selected,
       physical_access=False,runtime_reopened=False,
       search_failure='One rg used nonexistent boot_rom/BootResetAction.c and exited1 (OS error2); rg --files resolved boot/BootResetAction.c. No file changed.')
(K/'source-audit001.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(files=len(files),linked_lines=len(selected),physical_access=False)))
