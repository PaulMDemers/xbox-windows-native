"""Independent receipt branch checks; synthetic only."""
import json,hashlib
from pathlib import Path
from result_parser import analyze
K=Path(__file__).resolve().parent
ns={"__file__":str(K/"test_parser.py")}
exec((K/"test_parser.py").read_text().split("b=enc(pairs)")[0],ns)
pairs=ns["pairs"];enc=ns["enc"]
i=next(i for i,(k,v) in enumerate(pairs) if k=="miniport.enumerate")
base=pairs[:i];tail=pairs[i+3:]
variants=[[("miniport.enumerate",0)],[("miniport.enumerate",1),("miniport.open",0),("miniport.error",5)],[("miniport.enumerate",1),("miniport.open",1),("miniport.query",0),("miniport.bytes",0),("miniport.error",1)],[("miniport.enumerate",1),("miniport.open",1),("miniport.query",1),("miniport.bytes",80),("miniport.width",720),("miniport.height",480),("miniport.pitch",2880),("miniport.bpp",32),("miniport.geometry",1)]]
negative=0
for variant in variants:
    assert analyze(enc(base+variant+tail))["passed"]
    for j in range(len(variant)):
        assert not analyze(enc(base+variant[:j]+variant[j+1:]+tail))["passed"];negative+=1
for key,value in [("primary.flags",0x1006),("primary.pitch",2560),("miniport.pitch",2560),("miniport.bytes",79),("miniport.geometry",0)]:
    altered=[(k,value if k==key else v) for k,v in base+variants[-1]+tail]
    assert not analyze(enc(altered))["passed"];negative+=1
out=K/"parser-query-tests001.json";assert not out.exists()
out.write_text(json.dumps(dict(passed=True,synthetic_only=True,positive_cases=len(variants),negative_cases=negative,parser_sha256=hashlib.sha256((K/"result_parser.py").read_bytes()).hexdigest()),indent=2)+"\n")
print("Query variant parser checks PASS",len(variants),negative)
