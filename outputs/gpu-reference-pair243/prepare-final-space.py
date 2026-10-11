"""Closed243 portable copy only, guard actual exit and exact path before removal."""
from pathlib import Path
k=Path(__file__).resolve().parent
s=(k.parent/'gpu-preserve-entry239/portable-offload.ps1').read_text(encoding='utf-8').replace('closed-portable-239b','closed-portable-243-final').replace('237,238,239','243').replace("$case=if($phase -eq 239){'control001'}else{'xbe001'}","$case='preserve001'").replace('gpu-preserve-entry239/portable-offload001','gpu-reference-pair243/portable-final-offload001').replace('Closed237/238/239','Closed243')
p=k/'portable-final-offload.ps1';assert not p.exists();p.write_text(s,encoding='utf-8')
