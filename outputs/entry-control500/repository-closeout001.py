import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;R=K.parent.parent
def git(*args):return subprocess.check_output(['git',*args],cwd=R)
def write(p,v):p.write_bytes((json.dumps(v,indent=2)+'\n').encode())
write(K/'repository-check001.json',dict(session=60277,closed=True,exit_code=0,tracked_files_checked=37481,binary_media_and_credential_pattern_checks_passed=True))
note='''# 500 repository closeout complete; autonomous-return kit is next

Repository60277 CLOSED PASS37481 trackedfiles. AllownedprocessesCLOSED.
500host/package/final-review complete; checkGitHEAD/upstreamforpublicationstatus.
NoFTP/stage/launch/hook.499candidateNEVERexecuted. Historical497screenquestion
stillunknown; noadditionalpermissionneededfornewjustifieddiagnostic. Read500NEXT:
NEWbounded496runner/hookpairedwithunused499entryprobe, actualdispatcher/cleanup
tests andfreshnamespace beforeonephysicalrequest. Do notmodifyfrozen500nohookkit.
C23042068480B,E21499871232B;20GiBprojectedguard. Deadline14UTC/closeout13:50.

'''
for name in ['CONTINUATION.md','STATUS.md']:
 p=R/'outputs/engineering-notes'/name;p.write_bytes(note.encode()+p.read_bytes())
subprocess.run(['git','add','.gitattributes','outputs/entry-control500','outputs/engineering-notes/CONTINUATION.md','outputs/engineering-notes/STATUS.md'],cwd=R,check=True)
names=git('diff','--cached','--name-only','-z').decode().strip('\0').split('\0');rows=[]
for n in names:
 b=(R/n).read_bytes();assert git('show',':'+n)==b,n
 rows.append(dict(path=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
write(K/'git-byte-review001.json',dict(passed=True,files=rows))
subprocess.run(['git','add','outputs/entry-control500/git-byte-review001.json'],cwd=R,check=True)
n='outputs/entry-control500/git-byte-review001.json';assert git('show',':'+n)==(R/n).read_bytes()
subprocess.run(['git','diff','--cached','--check'],cwd=R,check=True)
subprocess.run(['git','commit','-m','Bound entry diagnostic collection and owned controller lifetimes'],cwd=R,check=True,timeout=90)
subprocess.run(['git','-c','http.version=HTTP/1.1','push','origin','main'],cwd=R,check=True,timeout=120)
print(git('log','-1','--format=%H').decode().strip())
assert not git('status','--porcelain','--untracked-files=no').strip()
assert git('rev-parse','HEAD')==git('rev-parse','origin/main')
