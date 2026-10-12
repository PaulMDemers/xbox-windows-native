"""Create a new helper, preserving the entire original Cancel implementation."""
from pathlib import Path
import hashlib,json
k=Path(__file__).resolve().parent
p=k.parent/'setup-wizard-automation201'
source=(p/'wizard006.c').read_text()
anchor='static BOOL CALLBACK top(HWND h,LPARAM unused) {'
call='    info.cbSize=sizeof(info);\n    if(GetForegroundWindow()!=h'
assert source.count(anchor)==1 and source.count(call)==1
new=source.replace(anchor,'#include "activation.inc"\n'+anchor).replace(call,'    activate313(h,w.tid);\n'+call)
dest=k/'wizard313.c';assert not dest.exists()
dest.write_text(new,newline='\n')
(k/'policy.h').write_bytes((p/'policy.h').read_bytes())
assert new.replace('#include "activation.inc"\n','').replace('    activate313(h,w.tid);\n','')==source
(k/'source-review001.json').write_text(json.dumps(dict(original_sha256=hashlib.sha256((p/'wizard006.c').read_bytes()).hexdigest(),source_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),original_cancel_body_reconstructed=True,policy_byte_identical=True,physical_mode_activation=False,source_comment='Original header comment describes original body; opt-in313 separately uses SetForegroundWindow.'),indent=2)+'\n')
