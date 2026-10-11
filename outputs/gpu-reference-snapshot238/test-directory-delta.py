"""Actual capture parser boundaries: empty roots and duplicate allocation ownership."""
import ast,hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'directory-parser-test001.json';assert not dest.exists();source=k/'directory-delta.py';tree=ast.parse(source.read_text());functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='inventory'];ns=dict(struct=struct,hashlib=hashlib);exec(compile(ast.Module(body=functions,type_ignores=[]),str(source),'exec'),ns)
root=k/'artifacts/directory-parser-test001';assert not root.exists();root.mkdir()
def entry(name,child):
 b=bytearray(64);n=name.encode();b[0]=len(n);b[1]=16;b[2:2+len(n)]=n;struct.pack_into('<I',b,44,child);return struct.pack('<4I',2,1,1,0)+b
head=struct.pack('<4I',1,1,1,0)+bytes(64);tail=struct.pack('<4I',5,1,2,0)+bytes(64);checks=0
p=root/'empty.bin';p.write_bytes(head+entry('empty1',0)+entry('empty2',0)+tail);files,row=ns['inventory'](p);assert not files and row['directories']==3;checks+=1
for name,raw in [('duplicate',head+entry('one',2)+entry('two',2)+tail),('unknown-parent',struct.pack('<4I',1,3,3,0)+bytes(64)+tail),('unterminated',head+entry('one',0)),('short',head+b'x')]:
 p=root/(name+'.bin');p.write_bytes(raw)
 try:ns['inventory'](p)
 except AssertionError:checks+=1
 else:raise AssertionError(name+' accepted')
dest.write_text(json.dumps(dict(passed=True,checks=checks,actual_parser_source_executed=True,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),guest_launch=False,recollection=False),indent=2)+'\n');print('238 directory parser checks',checks)
