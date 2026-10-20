"""Validate the explicit tool portion of this small fixed copy-script grammar."""
import re
from pathlib import PurePosixPath
def validate(script,files,rows,number):
 expected={f'{name}{number}.EXE' for name in ['RUN','VERIFY']}
 built={PurePosixPath(r['path'].replace('\\','/')).name.upper():r for r in rows}
 assert set(built)==expected
 assert {n for n in files if n.upper().endswith('.EXE') and '/' not in n}==expected
 for n in expected:
  assert files[n]['sha256']==built[n]['sha256'] and files[n]['bytes']==built[n]['bytes']
 lines=script.splitlines();copies=[]
 for i,line in enumerate(lines):
  if line.startswith('copy D:'):
   match=re.fullmatch(r'copy D:\\([A-Z0-9]+\.EXE) C:\\xwn'+str(number)+r'-kit\\([A-Z0-9]+\.EXE)',line)
   assert match,line
   source,destination=match.groups();assert source==destination and source in expected
   assert i+1<len(lines) and lines[i+1]=='if errorlevel 1 goto fail'
   copies.append(source)
 assert copies==[f'RUN{number}.EXE',f'VERIFY{number}.EXE']
 verify=f'C:\\xwn{number}-kit\\VERIFY{number}.EXE'
 assert lines.count(verify)==1 and lines.index(verify)>max(i for i,s in enumerate(lines) if s.startswith('copy D:'))
 assert lines[lines.index(verify)+1]=='if errorlevel 1 goto fail'
 assert f'if not exist D:\\VERIFY{number}.EXE goto fail' in lines
 assert not re.search(r'\b(?:RUN|TRACE|VERIFY)(?!'+str(number)+r'\b)\d+\.EXE',script)
 return dict(passed=True,tool_copies=copies,verifier=verify,scope='Exact harness tool copy names, hashes and verifier ordering; game members checked separately by media and guest verifier.')
