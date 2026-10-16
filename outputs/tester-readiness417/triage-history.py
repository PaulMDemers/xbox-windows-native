"""Classify credential-pattern matches without emitting matched values."""
import collections,hashlib,importlib.util,json,pathlib,re,subprocess
K=pathlib.Path(__file__).resolve().parent;W=K.parent.parent
spec=importlib.util.spec_from_file_location('scan',W/'tools/audit-public-readiness.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
objects={line.partition(' ')[0]:line.partition(' ')[2] for line in m.git('rev-list','--objects','--all').decode().splitlines()}
proc=subprocess.Popen(['git','cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
counts=collections.Counter();review=[];blobs=set()
for oid,path in objects.items():
 proc.stdin.write((oid+'\n').encode());proc.stdin.flush();header=proc.stdout.readline().split();data=proc.stdout.read(int(header[2]));assert proc.stdout.read(1)==b'\n'
 if header[1]!=b'blob':continue
 for match in re.finditer(m.PATTERNS['credential_literal_review'],data):
  blobs.add(oid);line=data[:match.start()].count(b'\n')+1
  value=match.group().decode(errors='replace')
  if re.search(r'''\.login\(\s*['"]xbox['"]\s*,\s*['"]xbox['"]''',value):kind='default-xbox-login'
  elif '.login(' in value and ('os.environ' in value or 'environ[' in value):kind='environment-variable-login'
  elif re.fullmatch(r'''(?i)Password\s*=\s*["'](?:yes|no|true|false)["']''',value):kind='unattended-setup-boolean'
  else:kind='manual-review'
  counts[kind]+=1
  if kind=='manual-review':review.append(dict(object=oid,path=path,line=line,match_sha256=hashlib.sha256(match.group()).hexdigest()))
proc.stdin.close();proc.stdout.close();assert proc.wait()==0
r=dict(blobs_with_matches=len(blobs),counts=dict(counts),manual_review=review,scope='Every credential-pattern match in reachable local Git blobs. Values never included. Pattern classification is not a comprehensive secret audit.')
(K/'credential-triage001.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
