"""Complete only the unexecuted tail after preserved missing-directory failure."""
from pathlib import Path
k=Path(__file__).resolve().parent
assert not (k/'portable-offload.ps1').exists()
s=(k.parent/'gpu-preserve-entry239/portable-offload.ps1').read_text(encoding='utf-8')
s=s.replace('closed-portable-239b','closed-portable-242').replace('237,238,239','240,241').replace("$case=if($phase -eq 239){'control001'}else{'xbe001'}","$case='preserve001'").replace('gpu-preserve-entry239/portable-offload001','gpu-reference-pair242/portable-offload001')
(k/'portable-offload.ps1').write_text(s,encoding='utf-8')
(k/'setup-failure001.json').write_text('{"stage":"scaffold", "error":"absent case-local before directory; audit actually opens immutable seed", "guest_launch":false, "mutation_after_failure":false, "repeated":false}\n',encoding='utf-8')
