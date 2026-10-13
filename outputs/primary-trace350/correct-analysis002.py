"""Preserve001 assumptions; decode actual bottom-up pair without changing trace."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
assert not (K/'trace_analysis002.py').exists() and not (K/'verify-trace002.py').exists()
s=(K/'trace_analysis.py').read_text()
s=s.replace("s['stride']==124","s['stride']==-124").replace("d['stride']==124","d['stride']==-124")
s=s.replace("assert len(bitmap_ids)==1","assert len(bitmap_ids)==2")
s=s.replace("one_shared_31_by_27_bitmap=next(iter(bitmap_ids))","two_bottom_up_31_by_27_bitmaps=sorted(bitmap_ids)")
needle="assert (surf['width'],surf['height'],surf['format'],surf['type'])==(v[4],v[5],v[11],v[12])"
assert s.count(needle)==1
s=s.replace(needle,needle+"\n                assert surf['stride']==struct.unpack_from('<i',bytes.fromhex(surf['raw']),36)[0]\n                if surf['type']==0:assert surf['pvScan0']==surf['pvBits']+(surf['height']-1)*(-surf['stride'])")
(K/'trace_analysis002.py').write_bytes(s.encode())
s=(K/'verify-trace.py').read_text().replace('from trace_analysis import','from trace_analysis002 import').replace('trace-verification001.json','trace-verification002.json').replace("K/'trace_analysis.py'","K/'trace_analysis002.py'")
(K/'verify-trace002.py').write_bytes(s.encode())
(K/'analysis-failure001.json').write_text(json.dumps(dict(error='AssertionError: expected positive124 stride; actual frozen SURFOBJ bytes encode -124. Review also found two bitmap identities, not one.',runtime_trace_unchanged=True,original_checker_preserved=True,inputs={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['trace_analysis.py','verify-trace.py']},scope='Correct observational metadata interpretation only; no changed pixel oracle or qualification gate.'),indent=2)+'\n')
