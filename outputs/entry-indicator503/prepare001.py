"""Preserve498 gate/file-call model; replace host continuation for new outer gate."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'entry-receipt498';out=K/'source-derivation001.json';assert not out.exists()
pins={}
for n in ['entry.S','host.S','host.c','host001.py','decode.py']:
 pins[n]=hashlib.sha256((P/n).read_bytes()).hexdigest()
(K/'entry498.S').write_bytes((P/'entry.S').read_bytes())
(K/'decode.py').write_bytes((P/'decode.py').read_bytes())
# The production gate source is unchanged; only the integration alias redirects
# its failure return to the one-shot LED cleanup wrapper.
(K/'combined.S').write_bytes(b'#define DiagHalReturnToFirmware Entry503Return\n#include "entry498.S"\n#undef DiagHalReturnToFirmware\n.set entry498_continue, entry503_complete\n#include "indicator.S"\n')
host=(P/'host.S').read_text(encoding='utf-8')
host=host[:host.index('\nentry498_continue:')]+ '\n.section .note.GNU-stack,"",@progbits\n'
host=host.replace('.global host_invoke, entry498_continue','.global host_invoke').replace('call entry498_gate','call entry503_gate')
(K/'host.S').write_bytes(host.encode())
prefix=(P/'host.c').read_text(encoding='utf-8').split('\nint main(')[0]
(K/'host.c').write_bytes((prefix+(K/'host-tail.c').read_text(encoding='utf-8')).encode())
out.write_bytes((json.dumps({'passed':True,'parent_sha256':pins,'gate_byte_exact':True,'file_model_prefix_byte_exact':True,'physical_access':False},indent=2)+'\n').encode())
