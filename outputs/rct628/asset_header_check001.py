"""Independent C-table check against all pinned asset names, sizes and digests."""
import ast,hashlib,json,re
from pathlib import Path
K=Path(__file__).resolve().parent
def validate(source,expected):
    rows=re.findall(r'\{("(?:[^"\\]|\\.)*"),(\d+),\{([\d,]+)\}\}',source)
    actual={}
    for literal,size,digest in rows:
        name=ast.literal_eval(literal).replace('\\','/')
        assert name not in actual,'duplicate name'
        actual[name]=dict(bytes=int(size),sha1=bytes(map(int,digest.split(','))).hex())
    assert len(rows)==503 and set(actual)==set(expected),'asset namespace mismatch'
    assert all(v=={k:expected[n][k] for k in v} for n,v in actual.items()),'size/digest mismatch'
    return True
if __name__=='__main__':
    source=(K/'assets.h').read_text();expected=json.loads((K/'asset-integrity001.json').read_text())
    assert validate(source,expected)
    rejected=[]
    for name,mutation in [('size',source.replace('5823602','5863602')),('filename',source.replace('u(5827)','u(5867)')),('digest',source.replace('133,136,102','132,136,102',1)),('duplicate',source.replace('CSG1.DAT','CSG1.1'))]:
        assert mutation!=source
        try:validate(mutation,expected)
        except AssertionError:rejected.append(name)
        else:raise AssertionError('mutation accepted: '+name)
    out=K/'asset-header-review001.json';assert not out.exists()
    out.write_text(json.dumps(dict(passed=True,rows=503,rejected_mutations=rejected,header_sha256=hashlib.sha256((K/'assets.h').read_bytes()).hexdigest(),metadata_sha256=hashlib.sha256((K/'asset-integrity001.json').read_bytes()).hexdigest()),indent=2)+'\n')
    print('All 503 C rows match; four metadata mutations rejected')
