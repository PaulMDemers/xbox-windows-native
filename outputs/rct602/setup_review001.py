"""Pin observed native display setup and retained input failures."""
import hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'setup-review001.json';assert not out.exists()
root=Path('C:/xwn602/pc001/phase1');p=root/'screen-1792466311522926900.png'
data=p.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(1024,768)
out.write_text(json.dumps(dict(passed=True,private_image=str(p),sha256=hashlib.sha256(data).hexdigest(),
 observed='Native Settings shows1024x768 HighColor16bit with confirmation dismissed; helper rechecks actual metrics before startup.',
 preserved_setup_issues=['actions001 retained599 argument; vm602 rejected it before input. actions002 corrects only that argument; failed open-display001 receipt retained.',
 'copy001 and copy-focus002 returned transport success but Run still showed control desk.cpl. No copy success inferred. Esc closed Run; fresh Run with100ms text holds showed exact cmd /c D:\\PREP.CMD before200ms Enter. All input receipts/screens remain private.',
 'Original retail media parser warns of missing UDF File Set Terminator. Full502-file mapped+supplemental ISO readback passed; media unchanged.',
 'prepare001 stdout still says fresh599; actual pinned paths, phase record and owned process are602.']),indent=2)+'\n')
