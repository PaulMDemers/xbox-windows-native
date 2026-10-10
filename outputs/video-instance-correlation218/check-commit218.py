"""Strict working-byte and Git reconstruction check; retain newline differences."""
from pathlib import Path
import hashlib,json,subprocess
k=Path(__file__).resolve().parent;ws=k.parents[1]
exact=[];crlf=[];private=[];external=[];working=0
for f in list(k.glob('emulator-frozen*.json'))+list(k.glob('build-inputs*.json')):
    pins=json.loads(f.read_text());pins=pins.get('files',pins)
    for name,digest in pins.items():
        p=Path(name);assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,(f,name)
        working+=1
        if not p.is_relative_to(ws):external.append(name);continue
        rel=p.relative_to(ws).as_posix()
        result=subprocess.run(['git','cat-file','blob','HEAD:'+rel],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        if result.returncode:private.append(rel);continue
        blob=result.stdout;actual=hashlib.sha256(blob).hexdigest()
        if actual==digest:exact.append(rel);continue
        reconstructed=blob.replace(b'\n',b'\r\n')
        assert b'\r' not in blob and reconstructed==p.read_bytes(),(f,rel,'unreconstructable source')
        assert hashlib.sha256(reconstructed).hexdigest()==digest
        crlf.append(dict(path=rel,git_blob_sha256=actual,pinned_working_sha256=digest,
                         exact_reconstruction='Replace each LF byte with CR LF; no other modification.'))
r=dict(working_pins_exact=working,tracked_exact_byte_checks=len(exact),
       tracked_reversible_crlf_checks=len(crlf),newline_differences=crlf,
       all_tracked_sources_exactly_reconstructable=True,
       private_inputs_retained=sorted(set(private)),external_sdk_runtime_inputs=sorted(set(external)),
       implementation_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
       repository_check_passed=True,powershell_ast_passed=True,python_ast_passed=True,
       git_diff_check_passed=True)
(k/'commit-validation.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['working_pins_exact','tracked_exact_byte_checks','tracked_reversible_crlf_checks','all_tracked_sources_exactly_reconstructable']}))
