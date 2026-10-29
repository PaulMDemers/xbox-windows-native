"""Stage scoped public evidence; verify exact index bytes and repository exclusions."""
from pathlib import Path
import subprocess,re,json,hashlib
K=Path(__file__).resolve().parent;W=K.parents[1]
git=lambda *a:subprocess.check_output(['git','-C',str(W),*a])
assert not git('diff','--cached','--name-only').strip(),'Existing staging must be reviewed separately'
paths=[p for p in K.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not re.fullmatch(r'model\d{3}\.json',p.name)]
paths += [W/'outputs/engineering-notes'/n for n in ['CONTINUATION.md','STATUS.md']]
for p in paths:
 b=p.read_bytes();assert len(b)<5*1024*1024 and b'\0' not in b and not b.startswith(b'MZ'),str(p)
 assert p.suffix.lower() in ['.py','.json','.md','.c','.h','.s','.ld',''] or p.name in ['.gitattributes','.gitignore'],str(p)
relative=[p.relative_to(W).as_posix() for p in paths]
for i in range(0,len(relative),40):git('add','-f','--',*relative[i:i+40])
staged=git('diff','--cached','--name-only','-z').decode().strip('\0').split('\0')
assert set(staged)==set(relative)
for name in staged:assert git('show',':'+name)==(W/name).read_bytes(),name
for name in relative:
 if '/native-vblank-bit801/' in name:assert git('check-attr','text','--',name).decode().strip().endswith(': unset'),name
script=W/'tools/check-repository.py'
code=script.read_text().replace("'ls-files', '-z'","'diff', '--cached', '--name-only', '-z'")
exec(compile(code,str(script),'exec'),{'__file__':str(script),'__name__':'__main__'})
git('-c','core.whitespace=cr-at-eol,-blank-at-eof','diff','--cached','--check')
print('PASS',len(staged),'scoped public paths; exact staged bytes and new kit attributes')
