import hashlib,json,re
from pathlib import Path
root=Path.cwd()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sets={'399':json.loads((root/'outputs/demo-integration399/frozen.json').read_text()),'401':json.loads((root/'outputs/public-source401/source003.json').read_text())['input_sha256']}
records={}
for name, pins in sets.items():
    mismatches=[k for k,v in pins.items() if sha(root/k)!=v]
    assert not mismatches,(name,mismatches)
    records[name]={'inputs':len(pins),'all_exact':True}
files=[Path(p) for p in ['README.md','NOTICE.md','CONTRIBUTING.md','src/README.md','upstream/README.md']]+[Path('docs')/p for p in ['architecture.md','building.md','installation.md','display-configuration.md','troubleshooting.md','recovery-guide.md','development.md','licensing.md','provenance.md']]
count=0
for p in files:
    text=p.read_text(encoding='utf-8')
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if '://' in target or target.startswith('#'):continue
        target=target.split('#')[0]
        assert (p.parent/target).exists(),(str(p),target)
        count+=1
    assert not re.search(r'C:/Users/Paul|/home/paul|192\.168\.|D:\\|D:/',text),str(p)
records['new_guides']={'files':len(files),'local_links':count,'all_exist':True,'private_host_path_scan':True}
records['source_files']=sum(len(p['files']) for p in json.loads(Path('upstream/components.json').read_text())['profiles'])
Path('outputs/release-readiness403/docs-invariants001.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records))
