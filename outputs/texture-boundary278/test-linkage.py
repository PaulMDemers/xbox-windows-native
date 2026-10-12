"""Actual276 graph linked to modeled278 proof; never retroactively qualifies276."""
import hashlib,json,re,struct
from pathlib import Path
import decode
k=Path(__file__).resolve().parent;dest=k/'linkage-host001.json';assert not dest.exists()
out=Path('E:/Codex-archive/xbox-windows-native/boundary278-linkage001');out.mkdir(exist_ok=False)
for n in ['decode.py','test-linkage.py']:(out/n).write_bytes((k/n).read_bytes())
old=k.parent/'callback-inventory276/emu001';trace=json.loads((old/'trace.json').read_text());original=[]
for record in trace['initial_pages']:
    data=(old/record['file']).read_bytes();assert hashlib.sha256(data).hexdigest()==record['sha256']
    original.extend(list(map(int,v.split(':'))) for v in re.findall(r'(?<!\w)r\d+=([0-9:]+)',data.decode()))
proof=[list(row) for row in struct.iter_unpack('<8Q',Path('E:/Codex-archive/xbox-windows-native/boundary278-worker001/rows.bin').read_bytes())]
# Convert MODEL phase2 to MODEL phase1; no actual evidence rewritten.
for r in proof:
    if r[0] in (64,69):r[1]=1
    if r[0]==17:r[7]-=2
rows=proof+[r for r in original if 1<=r[0]<=5];allocations=trace['checkpoints'][0]['state_header'][10:14]
assert decode.validate_graph(rows,1,allocations)['full_graph_and_native_allocations_linked']
mutations=[]
for i,row in enumerate(rows):
    columns={1:[2,3,4,5,6,7],2:[3,4,5,6],3:[2,3],4:[2,3],5:[2,3,4]}.get(row[0],[])
    if row[0] in (2,4,5) and (row[2] if row[0]==2 else row[1]) not in {r[2] for r in proof if r[0]==67}:continue
    for col in columns:
        m=[r.copy() for r in rows];m[i][col]^=1;mutations.append(m)
for m in mutations:
    try:decode.validate_graph(m,1,allocations)
    except (AssertionError,KeyError):pass
    else:raise AssertionError('Graph linkage mutation accepted')
for i in range(4):
    a=allocations.copy();a[i]+=4096
    try:decode.validate_graph(rows,1,a)
    except AssertionError:pass
    else:raise AssertionError('Wrong native allocation accepted')
(out/'modeled-proof.json').write_text(json.dumps(rows)+'\n')
r=dict(passed=True,actual276_graph=True,proof278_model_only=True,old276_requalified=False,
       graph_mutations_rejected=len(mutations),native_allocation_mutations_rejected=4,
       files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()})
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:b for a,b in r.items() if a!='files'},indent=2))
