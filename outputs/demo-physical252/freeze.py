"""Fresh physical audio stage pins; combined runtime prerequisite is mandatory."""
import ast
from common001 import *
ticket()
assert read(k/'before-audit002.json')['passed'] and read(k/'providers001.json')['passed']
assert read(canonical/'outputs/demo-integration251/emu001/combined-review.json')['scoped_combined_passed']
dest=k/'frozen001.json';assert not dest.exists()
root=helpers()
for p in k.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for path,row in before()['files'].items():assert sha(incoming(path))==row['sha256'] and row['second_read_exact']
inputs=list(k.glob('*.py'))+[k/'PLAN.md',k/'capture002.json',k/'before-audit002.json',k/'providers001.json',
    root/'MANIFEST.json',canonical/'outputs/demo-integration251/emu001/combined-review.json',
    canonical/'outputs/native-windows-fatx-preflight/artifacts/default.xbe',
    canonical/'outputs/native-windows-fatx-preflight/analyze.py']
inputs += [p for p in root.rglob('*') if p.is_file()]
save(dest,{str(p.resolve()):sha(p.read_bytes()) for p in inputs})
save(k/'ready001.json',dict(prepared=True,physical_qualified=False,strict_qualification_passed=False,
    source_package_commit='7cdb191bd2ef72e24001370726f97a7383a7250b',
    rollback_capture=str(k/'capture002.json'),captured_files=len(before()['files']),
    single_installation_only=True,combined_emulator_scope_passed=True,
    limits='Known whole-boot Ftdisk49 failure retained; new physical result required. No video staged here.'))
print('Incoming capture, reviewed physical payload and combined emulator gate pinned')
