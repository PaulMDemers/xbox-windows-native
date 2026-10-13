import hashlib,json
from pathlib import Path
from phase349_analysis import analyze
K=Path(__file__).resolve().parent;dest=K/'protocol-tests001.json';assert not dest.exists();checks=0
text=(K/'control001/artifacts/sample0/gdi-baseline.txt').read_text();rows=text.splitlines()
assert analyze(text,0)['passed']
for i,v in enumerate(rows):
    if v.startswith('PRIMARY348_'):
        damaged=rows[:i]+rows[i+1:];assert not analyze('\n'.join(damaged),0)['passed'];checks+=1
for ident in range(15):
    start=rows.index(f'PRIMARY348_PACKET {ident} 0 1');block=rows[start:start+66]
    # Remove/duplicate/relocate a complete otherwise-valid block: projection
    # alone could hide relocation, full schema must not accept it.
    for damaged in [rows[:start]+rows[start+66:]+block,rows[:start]+block+rows[start:]]:
        assert not analyze('\n'.join(damaged),0)['passed'];checks+=1
for i,v in enumerate(rows):
    if v.startswith('LARGE_PIXEL_CHECK'):
        parts=v.split();parts[-1]='0';damaged=rows.copy();damaged[i]=' '.join(parts)
        assert not analyze('\n'.join(damaged),0)['passed'];checks+=1
assert not analyze('\n'.join(v for v in rows if not v.startswith('PRIMARY348_')),0)['passed'];checks+=1
dest.write_text(json.dumps(dict(passed=True,negative_controls=checks,source_sha256=hashlib.sha256((K/'phase349_analysis.py').read_bytes()).hexdigest(),control_log_sha256=hashlib.sha256((K/'control001/artifacts/sample0/gdi-baseline.txt').read_bytes()).hexdigest(),physical_access=False),indent=2)+'\n');print(checks,'actual log schema/pixel controls rejected')
