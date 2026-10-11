"""Preserved physical189 PCI resource subkeys and bus service enumeration, read-only."""
import json,sys
from pathlib import Path
sys.dont_write_bytecode=True
from inventory import snapshot,sha
k=Path(__file__).resolve().parent
root=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
source=json.loads((k/'physical189-inventory.json').read_text())
r={'scope':__doc__,'inventory_sha256':sha(k/'physical189-inventory.json'),'source_sha256':sha(Path(__file__)),'phases':{}}
for phase,row in source['phases'].items():
    p=root/row['pins']['system']['path'];assert sha(p)==row['pins']['system']['sha256']
    values=snapshot(p);cs=row['current_control_set'];prefix='\\'+cs+'\\'
    selected={key:val for key,val in values.items() if key.startswith(prefix) and
              (('\\Enum\\PCI\\' in key and any(id in key for id in ('DEV_01B4','DEV_01C1','DEV_01B1'))) or
               key.startswith(prefix+'Services\\pci') or
               ('\\Enum\\' in key and any(s.get('decoded')=='pci' for s in [val.get('Service',{})])))}
    r['phases'][phase]=selected
dest=k/'physical189-resources.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n')
for key,values in r['phases']['after'].items():
    print(key,{name:val.get('decoded',val['hex']) for name,val in values.items() if name not in ('HardwareID','CompatibleIDs')})
