"""Static exact source, option, image layout and warning review before stock fixture."""
import collections,hashlib,importlib.util,json,re,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('E:/xwn334/build001')
dest=K/'binary-review001.json';assert not dest.exists()
sys.path.insert(0,str(W/'work/python-packages'));import pefile
s=importlib.util.spec_from_file_location('layout',W/'outputs/launcher-relocation293/review.py');mod=importlib.util.module_from_spec(s);s.loader.exec_module(mod)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((K/'build001.json').read_text());assert r['status']=='compiled'
for n,v in r['outputs'].items():assert sha(P/n)==v['sha256']
assert r['definitions']['XBOX_NATIVE_FATX_E_BOOT']=='ON' and r['definitions']['XBOX_NATIVE_FATX_F_BOOT']=='OFF' and r['definitions']['XBOX_NATIVE_EXTENDED_NT5_BOOT']=='OFF'
b,sec,sym=mod.elf(P/'image-crom.elf');assert sec['.text']['va']==0x2600000
end=max(v['va']+v['size'] for v in sec.values() if v['flags']&2);assert end==sym['BSS_END']['va'] and 0x2800000-end>=262144
assert b'/Applications/XWNEBoot/freeldr.sys\0' in b and b'/Applications/XWNFBoot/freeldr.sys\0' not in b
pe=pefile.PE(str(P/'rosload.exe'));assert pe.FILE_HEADER.Machine==0x14c and not getattr(pe,'DIRECTORY_ENTRY_IMPORT',[])
assert pe.OPTIONAL_HEADER.CheckSum==pe.generate_checksum()
def warns(p):return collections.Counter(x.split('warning:',1)[1].strip() for x in p.read_text(errors='replace').splitlines() if 'warning:' in x)
parent=warns(Path('E:/xwn300/build001/candidate001.log'))
actual=warns(P/'nt5.log')+warns(P/'cromwell.log')
# Compare warning messages; parent300 also builds miniport/bootvid targets.
unknown=set(actual)-set(parent)
assert not unknown,unknown
result=dict(passed=True,physical_access=False,guest_qualified=False,source_review_sha256=sha(K/'source-review001.json'),build_sha256=sha(K/'build001.json'),outputs=r['outputs'],bss_end=end,stack_headroom=0x2800000-end,rosload_imports=[],checksum_verified=True,profile_tests=r['profile_tests'],warnings=dict(actual),new_warning_messages=[],scope='Static E boot path/options and retained HD layout only; no stock-drive runtime or physical qualification.')
dest.write_text(json.dumps(result,indent=2)+'\n');print('Stock E binary review passed')
