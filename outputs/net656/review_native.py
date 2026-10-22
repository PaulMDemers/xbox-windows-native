"""Read-only static review of the final retained native build; no CPU execution."""
import datetime,hashlib,json,re,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/mnt/c/xwn651/source001');S=Path('/mnt/c/xwn656/source005');B=Path('/mnt/c/xwn656/review001')
assert not B.exists() and not (K/'review-native001.json').exists()
B.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
try:
 build=json.loads((K/'native005.json').read_text());assert build['status']=='compiled-dormant'
 for n,v in build['source_pins'].items():assert sha(K/n)==v,n
 model=json.loads((K/'host004.json').read_text());assert model['status']=='pass'
 for n in ('nic.c','nic.h','test.c'):assert sha(K/n)==model['source_pins'][n]
 paths=subprocess.check_output(['git','-C',str(P),'ls-files','-z']).decode().strip('\0').split('\0')
 changed=[n for n in paths if (P/n).read_bytes()!=(S/n).read_bytes()]
 assert changed==['Makefile','drivers/Makefile'];r['changed_parent_files']=changed
 expected={'BSS_END','_bss','xbox_ram','PciReadDword','PciReadWord','PciWriteWord','admission656','send656'}
 for stem in ('net656_core','net656_native','net656_admission'):
  obj=S/'obj'/(stem+'.o');raw=subprocess.check_output(['nm','-u',str(obj)],text=True)
  symbols={line.split()[-1] for line in raw.splitlines() if line.strip()}
  assert symbols==(expected if stem=='net656_native' else set()),(stem,symbols)
  r.setdefault('undefined_symbols',{})[stem]=sorted(symbols)
  dis=subprocess.check_output(['objdump','-dr',str(obj)],text=True)
  (B/(stem+'.disassembly.txt')).write_text(dis)
  assert not re.search(r'\b(?:sti|cli|wrmsr|invlpg|popf[lw]?)\b',dis)
  assert not re.search(r'\bmov\s+[^\n]*,%cr[0-9]',dis)
  r.setdefault('objects',{})[stem]=dict(sha256=sha(obj),wbinvd_instructions=len(re.findall(r'\bwbinvd\b',dis)))
 uses=[]
 for obj in (S/'obj').glob('*.o'):
  raw=subprocess.check_output(['nm','-u',str(obj)],stderr=subprocess.DEVNULL,text=True)
  if 'NativeSend656' in raw:uses.append(obj.name)
 assert not uses;r['objects_referencing_native_entry']=uses
 r.update(passed=True,source_pins_exact=True,models_are_not_native_execution=True)
except BaseException as e:r['failure']=repr(e);raise
finally:(K/'review-native001.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(passed=r['passed'],changed_parent_files=r.get('changed_parent_files'),physical_access=False)))
