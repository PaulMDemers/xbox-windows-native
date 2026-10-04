"""Execute the compiled entry checkpoint with the modeled NT5 calling convention."""
import pathlib
k=pathlib.Path(__file__).resolve().parent
text=(k/'test-video-diagnostic.py').read_text();text=text[:text.index('\nresults=[]')].replace("artifacts/xboxvnt5-diagnostic.sys","artifacts/xboxvnt5-entry.sys");exec(text)
m=Diagnostic()
try:
 m.run('_DriverEntry@8',(0x11112222,0x33334444));raise AssertionError('Entry checkpoint did not stop')
except DiagnosticStop:
 assert m.failure==(0xe0580001,0,0x11112222,0x33334444,0x56454e54)
r={'scope':'Compiled miniport DriverEntry checkpoint with modeled NT5 calling convention','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'all_imports_resolve':True,'bugcheck':[hex(v) for v in m.failure],'passed':True}
(k/'video-entry-test.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
