"""After ordinary closure only: preserve frozen sources and correct inherited metadata."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'physical-scope-correction.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for case in ['control001','candidate001']:
 assert read(k/('emu-'+case)/'closure.json')['closed'] and read(k/('emu-'+case)/'audit.json')['scoped_display_passed']
assert not (k/'physical-ready.json').exists() and not (k/'control001/physical.json').exists()
frozen=read(k/'emulator-frozen.json');art=k/'artifacts/ordinary-source-closed211';art.mkdir(exist_ok=False)
replacements={
 'prepare-package.py':('Exact208 scalar UC stores OFF/ON with118 metadata, text bounds and clocks OFF both','Exact210 upload accounting OFF/ON with119 metadata, text bounds ON and scalar/body clocks OFF'),
 'physical-controller.py':('Exact208 scalar UC stores OFF/ON, clocks and text bounds OFF both','Exact210 upload accounting OFF/ON, text bounds ON and scalar/body clocks OFF'),
 'prepare-physical.py':('Only208 scalar UC stores OFF/ON; clocks/text bounds OFF both, exact206 v11 probe','Only210 upload accounting OFF/ON; text bounds ON, scalar/body clocks OFF, new211 v12 probe'),
 'audit-physical.py':('Scalar stores OFF/ON synchronous GDI plus actual window observation, text bounds and clocks OFF both','Upload accounting OFF/ON synchronous GDI and separated move/paint/readback phases, text bounds ON and scalar/body clocks OFF')
}
changes={}
class MetadataOnly(ast.NodeTransformer):
 def visit_Constant(self,node):
  if isinstance(node.value,str):
   for a,b in replacements.values():node.value=node.value.replace(a,b)
  return node
for name,(before,after) in replacements.items():
 p=k/name;original=p.read_bytes();assert sha(p)==frozen[p.relative_to(ws).as_posix()]
 source=original.decode();assert source.count(before)==1,name;new=source.replace(before,after)
 assert ast.dump(MetadataOnly().visit(ast.parse(source)))==ast.dump(ast.parse(new)),name
 archive=art/name;archive.write_bytes(original);p.write_text(new,newline='\n')
 changes[name]=dict(before_sha256=hashlib.sha256(original).hexdigest(),after_sha256=sha(p),ordinary_source_archive=archive.relative_to(ws).as_posix(),archive_sha256=sha(archive),literal_before=before,literal_after=after)
r=dict(passed=True,physical_access=False,guest_launch=False,ordinary_cases_closed_before_change=True,
 ordinary_frozen_manifest_sha256=sha(k/'emulator-frozen.json'),changes=changes,
 limits='Only four inherited descriptions corrected after ordinary closure. No gate/control flow/import/driver/probe changes; frozen ordinary bytes privately preserved. Physical ready will separately freeze current sources.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Closed ordinary sources preserved; physical description literals corrected only')
