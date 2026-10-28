"""Preserve failed002; fresh003 removes only ELF segment alignment padding."""
from pathlib import Path
import json,hashlib
K=Path(__file__).resolve().parent
s=(K/'payload_build002.py').read_text().replace('payload002','payload003').replace('--emit-relocs','--emit-relocs,-z,max-page-size=0x20')
(K/'payload_build003.py').write_text(s,newline='\n')
for n in ['host_build005.py','model.py','review_prepare.py']:
 p=K/n;p.write_text(p.read_text().replace('payload002','payload003'),newline='\n')
(K/'link-layout003.json').write_text(json.dumps({'previous_attempt':'payload002.json','previous_failure':'raw16760 exceeds14080 reserved payload due to4KiB alignment; text0x3210bytes, rodata0x104000','fresh_attempt':'payload003','change':'ELF max-page-size0x20 preserves32-byte rodata alignment and existing bridge14080-byte reserve; guest C sources unchanged','requires':'independent text/relocation/data equivalence and all fresh runtime qualification','physical_access':False},indent=2)+'\n')
