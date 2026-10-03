"""Read only selected boot files from the preserved Windows 2000 PC fixture."""
from pathlib import Path
import json,hashlib,subprocess
root=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
kit=root/'outputs/native-windows-physical-nt5'
source=root/'outputs/native-windows-nt5/artifacts/windows2000-pc-base.qcow2'
raw=Path('/home/paul/xbox-windows-native/fixtures/physical-nt5-extraction.raw')
target=kit/'package'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
expected='59d7e920b19f10a05ba3a914f05c90e43764f2a7506a8bb16e816b781c54785e'
assert sha(source)==expected
assert not raw.exists()
audit=json.loads((root/'outputs/native-windows-nt5-handoff/boot-driver-audit.json').read_text())
files=['WINNT/system32/ntoskrnl.exe','WINNT/system32/config/system']
files+=['WINNT/'+d['image_path'].replace('\\','/') for d in audit['drivers']]
files+=['WINNT/system32/drivers/'+n+'.sys' for n in ['fastfat','classpnp','scsiport','pciidex','wmilib']]
files+=['WINNT/system32/'+n for n in ['c_1252.nls','c_437.nls','l_intl.nls']]
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
 cmd=['/home/paul/xbox-windows-native/toolchains/7zip/root/usr/lib/7zip/7z','x','-y','-ssc-',f'-o{target}',str(raw),*files]
 r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,check=True)
 (kit/'build-logs/extraction.log').write_text(r.stdout)
 actual={p.relative_to(target).as_posix().casefold():p for p in (target/'WINNT').rglob('*') if p.is_file()}
 assert all(n.casefold() in actual for n in files),set(n.casefold() for n in files)-set(actual)
 assert sha(actual['winnt/system32/config/system'])==audit['system_sha256']
 assert sha(source)==expected
 report={'source_sha256':expected,'source_preserved':True,'selected_files_only':True,'files':{p.relative_to(target).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in actual.values()}}
 (kit/'windows-files.json').write_text(json.dumps(report,indent=2)+'\n')
 print(len(actual),'files',sum(p.stat().st_size for p in actual.values()),'bytes')
finally:
 assert raw.resolve().parent==Path('/home/paul/xbox-windows-native/fixtures').resolve()
 raw.unlink(missing_ok=True)
