"""Pin actual NV2A model and compiled native read table, independent of retired header-layout check."""
import hashlib,json,re,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'model-review002.json';assert not dest.exists()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
src=k.parent/'video-transfer-protocol215/artifacts/source/hw/xbox/nv2a';old=read(k/'inventory.json')
for name,h in old['source_pins'].items():assert sha(src/name)==h,name
table=[r['offset'] for r in old['offsets']];assert len(table)==16
c=(k/'retirement.c').read_text();part=c[c.index('X224Offsets'):c.index('void x224_sample')]
assert [int(v,16) for v in re.findall(r'0x[0-9a-f]+',part)]==table
encoded=struct.pack('<16I',*table);native=[]
for case in ['control001','candidate001']:
    path=k/'artifacts/build002'/case/'resident.sys';data=path.read_bytes();expected=read(k/'build-review002.json')['binaries'][case]['sha256'];assert sha(path)==expected
    assert data.count(encoded)==1;pe=pefile.PE(str(path));off=data.index(encoded);rva=pe.get_rva_from_offset(off)
    section=pe.get_section_by_rva(rva);assert section.Name.rstrip(b'\0')==b'.rdata' and not section.Characteristics&0x02000000
    native.append(dict(case=case,sha256=expected,table_rva=rva,table_bytes=encoded.hex(),nondiscardable=True))
fifo=(src/'pfifo.c').read_text();graph=(src/'pgraph/pgraph.c').read_text()
assert 'TODO: should we become busy here??' in fifo and 'if (dma_get_v == dma_put_v) break;' in fifo
assert 'r = NV_PFIFO_RUNOUT_STATUS_LOW_MARK; /* low mark empty */' in fifo
assert 'NV_PGRAPH_STATUS' not in graph and 'r = pgraph_reg_r(pg, addr);' in graph
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),native_tables=native,
    source_pins=old['source_pins'],offsets=old['offsets'],limits=old['limits'],gpu_ownership_qualified=False,physical_access=False),indent=2)+'\n');print('Model/compiled native224 table PASS')
