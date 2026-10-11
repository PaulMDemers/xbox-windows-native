"""New parser ABI includes only defined246 diagnostic phases; old tests retained."""
from pathlib import Path
k=Path(__file__).resolve().parent
p=k/'lifecycle246.py';assert not p.exists()
s=(k/'lifecycle.py').read_text().replace("  else:raise AssertionError(('Unknown NV phase',phase))","  elif 60<=phase<=68:\n   assert ref==0\n  else:raise AssertionError(('Unknown NV phase',phase))")
p.write_text(s)
p=k/'test-lifecycle002.py';assert not p.exists();p.write_text((k/'test-lifecycle.py').read_text().replace('from lifecycle import parse','from lifecycle246 import parse').replace('lifecycle-test001','lifecycle-test002').replace("k/'lifecycle.py'","k/'lifecycle246.py'"))
p=k/'analyze-lifecycle002.py';s=p.read_text().replace('from lifecycle import parse','from lifecycle246 import parse');p.write_text(s)
p=k/'prelaunch-review.py';s=p.read_text().replace("'lifecycle-test001'","'lifecycle-test002','closed-test001'");p.write_text(s)
p=k/'trace.py';s=p.read_text();a=" if g:\n  if not stopped:"
assert s.count(a)==1
s=s.replace(a,''' if frontend_requested and frontend_reopened and not r.get('frontend_scope_passed'):
  try:
   deadline=time.monotonic()+8
   while True:
    reply=cmd('qom-get '+r['nv2a_qom_path']+' xwn-frontend246-report')
    r['frontend_failure_reopen_report']=reply;save()
    if re.search(r'(?<![a-z_])state=5(?:[, ]|$)',reply):break
    assert time.monotonic()<deadline;time.sleep(.025)
   r['frontend_failure_reopen_acknowledged']=True
  except Exception as exc:r['frontend_failure_reopen_ack_error']=repr(exc);quarantined=True
 if g:
  if not stopped:''')
p.write_text(s)
# Current host intervention source changed only final closure: refresh derived
# adapters in new result namespaces rather than overwriting old passed results.
for name,dest in [('test-pair.py','pair-test002'),('test-guards003.py','guard-test004')]:
 p=k/name.replace('.py','-updated.py');assert not p.exists()
 s=(k/name).read_text().replace('pair-test001',dest).replace('guard-test003',dest);p.write_text(s)
p=k/'prelaunch-review.py';s=p.read_text().replace("'pair-test001'","'pair-test002'").replace("'guard-test003'","'guard-test004'");p.write_text(s)
print('New ABI/cleanup adapters prepared; no guest launched')
