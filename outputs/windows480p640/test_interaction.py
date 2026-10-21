from pathlib import Path
import json,hashlib
from result_parser import analyze
k=Path(__file__).resolve().parent;out=k/'interaction-tests001.json';assert not out.exists()
b=(k.parent/'windows480p639/probe-result001.txt').read_bytes().replace(b'case=639',b'case=640')
assert analyze(b)['passed'];assert analyze(b.replace(b'input1.bytes=7',b'input1.bytes=9').replace(b'input2.bytes=7',b'input2.bytes=9'))['passed']
neg=[]
for key in ['input.seed_created','input.seed_written','input1.started','input1.closed','input1.readback','input1.matches','input2.started','input2.closed','input2.readback','input2.unchanged','input.complete']:
 assert not analyze(b.replace((key+'=1').encode(),(key+'=0').encode()))['passed'];neg.append(key)
assert not analyze(b.replace(b'input2.bytes=7',b'input2.bytes=9'))['passed'];neg.append('unequal accepted lengths')
out.write_text(json.dumps(dict(passed=True,physical_access=False,actual639_receipt_as_parser_input=True,positive_cases=2,negative_cases=neg,parser_sha256=hashlib.sha256((k/'result_parser.py').read_bytes()).hexdigest()),indent=2)+'\n')
print('Interaction parser cases PASS')
