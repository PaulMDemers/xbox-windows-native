"""Exact E path, HD reservation, layout and inherited warnings; no runtime claim."""
import collections,hashlib,importlib.util,json,re
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=Path('E:/xwn374/build001')
assert not (K/'review001.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((K/'build001.json').read_text());assert r['status']=='compiled'
for n,v in r['outputs'].items():assert sha(O/n)==v['sha256']
s=importlib.util.spec_from_file_location('layout',W/'outputs/launcher-relocation293/review.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
b,sec,sym=m.elf(O/'image-crom.elf');assert sec['.text']['va']==0x2600000
end=max(v['va']+v['size'] for v in sec.values() if v['flags']&2);assert end==sym['BSS_END']['va'] and 0x2800000-end>=262144
assert b'/Applications/XWNEBoot/freeldr.sys\0' in b and b'/Applications/XWNFBoot/freeldr.sys\0' not in b
assert 'XWN_HD_TIMING_720P=1' in r['flags'] and '1080' not in r['flags']
def warns(p):return collections.Counter(re.sub(r'/home/paul/xbox-windows-native/build/[^ ]+/obj/','SOURCE/obj/',x.split('warning:',1)[1].strip()) for x in p.read_text(errors='replace').splitlines() if 'warning:' in x)
actual=warns(O/'cromwell.log');parent=warns(Path('E:/xwn334/build001/cromwell.log'));assert not set(actual)-set(parent),set(actual)-set(parent)
out=dict(passed=True,build_sha256=sha(K/'build001.json'),outputs=r['outputs'],bss_end=end,stack_headroom=0x2800000-end,warnings=dict(actual),new_warning_messages=[],physical_qualified=False,guest_qualified=False)
(K/'review001.json').write_text(json.dumps(out,indent=2)+'\n');print('E 720p static review passed')
