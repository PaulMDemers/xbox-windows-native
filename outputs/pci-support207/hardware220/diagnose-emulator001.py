"""Preserve the failed first rehearsal's typed state differences; no guest writes."""
import json,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent
sys.path.insert(0,str(k.parent));from inventory import snapshot
out=k/'emulator001/diagnosis.json';assert not out.exists()
a=snapshot(k/'emulator001/artifacts/before-system');b=snapshot(k/'emulator001/artifacts/audit/after-system')
select=lambda values:{key:data for key,data in values.items() if any(t in key.lower() for t in ('\\enum\\pci\\','\\control\\class\\','\\control\\deviceclasses\\')) or ('\\services\\' in key.lower() and key.lower().endswith(('\\xwnsmb','\\xwnfatx','\\xboxvnt5','\\nvnetnt5')))}
a,b=select(a),select(b)
delta=[dict(path=key,before=a.get(key),after=b.get(key)) for key in sorted(set(a)|set(b)) if a.get(key)!=b.get(key)]
log=(k/'emulator001/artifacts/audit/observer.log').read_bytes()
first=next((i for i,v in enumerate(log) if v>=128 or (v<32 and v not in (10,13,9))),len(log))
result=dict(binding_delta=delta,observer_bytes=len(log),observer_first_nontext_offset=first,
            observer_valid_tail=log[max(0,first-1200):first].decode('ascii'),
            result_bytes=(k/'emulator001/artifacts/audit/result.txt').stat().st_size,
            conclusion='Host-stopped incomplete observer with unreadable tail and empty command exit log. Retain failed attempt; cause not proven. Inventory footer complete; one zero-size NV2A OS resource payload unavailable.')
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(changed_keys=len(delta),paths=[v['path'] for v in delta],observer_first_nontext_offset=first),indent=2))
