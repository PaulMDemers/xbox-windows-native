"""Create804 controller metadata for the CR07 overflow step; mechanics unchanged."""
from pathlib import Path
K=Path(__file__).resolve().parent
s=(K/'physical007.py').read_text()
s=s.replace('CR09 vertical-blank-start bit5','CR07 vertical-blank-start overflow bit3')
s=s.replace('CR09 60/40/60, eight neighbors and own recovery before CR12','CR09 60/40/60 then CR07 36/3E/36, eight neighbors and own recovery before CR09 and CR12')
p=K/'physical008.py';assert not p.exists();p.write_bytes(s.encode())
print('Prepared804 controller descriptions; no physical access')
