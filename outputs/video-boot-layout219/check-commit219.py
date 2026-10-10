"""Verify closed working pins, staged-source reconstruction and syntax, without guest work."""
import ast,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'commit-validation.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
index=[];private=[];external=[];checked=0
pair=read(k/'pair-review.json');assert pair['passed'] and not pair['strict_overall_qualified'] and not pair['runtime_tail_guard_qualified']
archive=k/pair['original_full_review']['private_path'];assert sha(archive)==pair['original_full_review']['sha256']
full=read(archive);assert full['source_sha256']==sha(k/'review-pair.py') and pair['source_sha256']==full['source_sha256']
assert pair['summary_author_sha256']==sha(k/'summarize-pair.py')
compiled=read(k/'compiled-reset-review.json');assert compiled['source_sha256']==sha(k/'review-compiled-reset.py')
for name,case in compiled['cases'].items():assert sha(k/'artifacts/reset-disassembly'/(name+'.txt'))==case['disassembly_sha256']
for frozen in [read(k/'emulator-frozen.json'),read(k/'observer002-frozen.json'),full['input_pins']]:
 for name,digest in frozen.items():
  path=Path(name);path=path if path.is_absolute() else ws/path
  assert sha(path)==digest,(name,'working pin changed');checked+=1
  if not path.is_relative_to(ws):external.append(str(path));continue
  rel=path.relative_to(ws).as_posix();result=subprocess.run(['git','cat-file','blob',':'+rel],cwd=ws,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
  if result.returncode:private.append(rel);continue
  blob=result.stdout;original=path.read_bytes();row=dict(path=rel,working_sha256=digest,index_sha256=hashlib.sha256(blob).hexdigest())
  if blob==original:row['exact']=True
  else:
   assert original.replace(b'\r\n',b'\n')==blob,(rel,'unreconstructable staged pin')
   a=blob.splitlines(keepends=True);b=original.splitlines(keepends=True);assert len(a)==len(b)
   positions=[i for i,line in enumerate(b) if line.endswith(b'\r\n')]
   reconstructed=b''.join(line[:-1]+b'\r\n' if i in positions else line for i,line in enumerate(a))
   assert reconstructed==original and hashlib.sha256(reconstructed).hexdigest()==digest
   row.update(exact=False,crlf_line_indices=positions,reconstruction='Convert LF to CRLF at these zero-based splitlines(keepends=True) indices only.')
  index.append(row)
files=list(k.glob('*.py'))
for path in files:ast.parse(path.read_text(),filename=str(path))
subprocess.run(['git','diff','--cached','--check'],cwd=ws,check=True)
subprocess.run([__import__('sys').executable,str(ws/'tools/check-repository.py')],cwd=ws,check=True)
r=dict(passed=True,source_sha256=sha(Path(__file__)),working_pins_checked=checked,index_checks=index,private_inputs=sorted(set(private)),external_inputs=sorted(set(external)),all_tracked_pins_exactly_reconstructable=True,python_ast_files=len(files),repository_check_passed=True,git_diff_check_passed=True,full_pair_private_preserved=True,strict_overall_qualified=False,runtime_tail_guard_qualified=False,physical_access=False,guest_launch=False,base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ws,text=True).strip())
dest.write_text(json.dumps(r,indent=2)+'\n');print('Closed working/index evidence and syntax checks PASS:',checked)
