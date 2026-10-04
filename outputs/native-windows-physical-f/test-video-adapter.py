"""Exercise the compiled adapter checkpoint and its earlier failure guard."""
import pathlib
k=pathlib.Path(__file__).resolve().parent
text=(k/'test-video-diagnostic.py').read_text();text=text[:text.index('\nresults=[]')].replace("artifacts/xboxvnt5-diagnostic.sys","artifacts/xboxvnt5-adapter.sys");exec(text)
results=[]
for failure in [False,True]:
 m=Diagnostic(range_status=55 if failure else 0);assert m.run('_DriverEntry@8',(1,2))==0
 try:
  m.init_adapter();raise AssertionError('Expected adapter checkpoint')
 except DiagnosticStop:
  expected=(0xe0580001,2,55,0,0) if failure else (0xe0580001,8,0xfd000000,0xf0000000,0x8000000)
  assert m.failure==expected;results.append([hex(v) for v in m.failure])
r={'scope':'Compiled adapter checkpoint and prior range-failure guard','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'all_imports_resolve':True,'tests':results,'passed':True}
(k/'video-adapter-test.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
