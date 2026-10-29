"""Derive fresh808 freeze gate from closed806 SOURCE only."""
from pathlib import Path
import re
K=Path(__file__).resolve().parent
s=(K.parent/'native-vblank-low806/review_prepare001.py').read_text()
parts=re.split(r'(0x[0-9a-fA-F]+)',s)
s=''.join(re.sub(r'^0x806(?=[0-9a-f]{0,2}$)','0x808',p) if i%2 else p.replace('806','808') for i,p in enumerate(parts))
s=s.replace('==22\nassert len(read(\'model002','==23\nassert len(read(\'model002')
for a,b in [('934','974'),('924','964'),('2920','3040'),('0x7368','0x73e0'),('0xb00','0x900'),('23744','24256'),('probe-shared-native.c','probe-bitmap-native.c'),('Twenty-two masks omitted raw; final success requires all30','Twenty-three masks omitted raw; final success requires all31'),('Same-value CR02/NVVVALIDSTART/CR07total write/undo drops indistinguishable','Same-value CR07linecompare and earlier same-value write/undo drops indistinguishable')]:s=s.replace(a,b)
s=s.replace("'not_admitted':['physical008.py','cpu005.py','build012.py','probe-native.c','probe-compact-native.c','measure001','measure002','measure003/shared-no-unwind']","'not_admitted':['probe-native.c','probe-compact-native.c','probe-shared-native.c','measure001','measure002']")
assert "['omitted_aggregate_masks'])==23" in s
with (K/'review_prepare001.py').open('xb') as f:f.write(s.encode())
