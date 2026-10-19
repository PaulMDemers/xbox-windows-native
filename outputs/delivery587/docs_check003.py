"""Check changed guide links, documented CLI flags and Bash syntax without executing builds."""
import datetime,json,re,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
names=['README.md','docs/build-test-kits.md','docs/building.md','docs/build-to-boot.md',
       'docs/tester-bundles.md','docs/testers.md','docs/tester-report-template.md']
links=[];blocks=[]
for name in names:
 p=W/name;text=p.read_text(encoding='utf-8-sig')
 for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
  if '://' in target or target.startswith('#'):continue
  plain=target.split('#')[0];dest=(p.parent/plain).resolve()
  assert dest.exists(),(name,target)
  if '#' in target and dest.suffix=='.md':
   anchor=target.split('#',1)[1]
   headings=re.findall(r'^#+ (.+)$',dest.read_text(encoding='utf-8-sig'),re.M)
   slugs=[re.sub(r'[^\w\- ]','',s.lower()).replace(' ','-') for s in headings]
   assert anchor in slugs,(name,target)
  links.append(dict(source=name,target=target))
 if name=='docs/build-test-kits.md':blocks=re.findall(r'```sh\n(.*?)```',text,re.S)
syntax=subprocess.run(['wsl','-d','Ubuntu','-u','paul','--','bash','-n'],input='\n'.join(blocks).encode('utf-8'),capture_output=True,timeout=20)
assert syntax.returncode==0,syntax.stderr
cli=(W/'tools/tester_bundle.py').read_text()
for flag in ['--root','--kind','--output','--manifest','--private-windows','--console-only','--defer-launcher']:
 assert flag in cli,flag
r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=names,
 local_links_checked=len(links),bash_blocks_syntax_checked=len(blocks),
 documented_packager_flags_present=True,passed=True,
 limits='Documentation/link/shell-syntax review only. Commands were not executed as builds, Windows setup, ZIP creation, transfers or hardware tests.')
out=K/'docs-check003.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
