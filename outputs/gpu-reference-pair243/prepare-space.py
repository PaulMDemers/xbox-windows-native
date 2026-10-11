"""One readback-verified closed242 portable offload, never move disk chains."""
from pathlib import Path
k=Path(__file__).resolve().parent
s=(k.parent/'gpu-preserve-entry239/portable-offload.ps1').read_text(encoding='utf-8')
s=s.replace('closed-portable-239b','closed-portable-243').replace('237,238,239','242').replace("$case=if($phase -eq 239){'control001'}else{'xbe001'}","$case='preserve001'").replace('gpu-preserve-entry239/portable-offload001','gpu-reference-pair243/portable-offload001').replace('Closed237/238/239','Closed242')
p=k/'portable-offload.ps1';assert not p.exists();p.write_text(s,encoding='utf-8')
