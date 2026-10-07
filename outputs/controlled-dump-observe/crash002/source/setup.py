"""New crash002 observer; preserve failed crash001 and reuse exact compiled trigger."""
from pathlib import Path
import json,hashlib
k=Path(__file__).resolve().parent;old=k.parent/'controlled-dump';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
unchanged=['trigger.c','probe.c','Build.ps1','review.py','build-review.json','hal-review.json','fatx-review.json','layouts.json','modules.json','kernel-review.json','atomic_json.py','make-modules.py']
changed=['common.py','configuration.py','cold-map.py','prepare.py','Run.ps1','preflight.py','supervise.py','record-closure.py','audit-crash.py']
for n in unchanged:(k/n).write_bytes((old/n).read_bytes())
for n in changed:(k/n).write_text((old/n).read_text().replace('controlled-dump','controlled-dump-observe').replace('crash001','crash002'))
t=(old/'trace.py').read_text().replace('controlled-dump','controlled-dump-observe').replace('crash001','crash002')
bad="row['storage_pins']={n:pin(next(v['base'] for v in loaded if v['name'].lower()==n)+pes[n].OPTIONAL_HEADER.AddressOfEntryPoint) for n in ['hal.dll','xwnfatx.sys','atapi.sys','disk.sys','classpnp.sys','ftdisk.sys']}"
good="row['resident_dispatch_pins']={n:pin(next(v['base'] for v in loaded if v['name'].lower()==n)+rva) for n,rva in [('hal.dll',0x8290),('xwnfatx.sys',int(read(k/'fatx-review.json')['candidate001']['resident_functions']['_VfatFileSystemControl']['rva'],16))]}"
assert bad in t;t=t.replace(bad,good)
t=t.replace("initret=K+0x21ed4","initret=K+0x21ed4;precall=K+0x2b141")
t=t.replace('for a in [bc,dump,initret]','for a in [bc,dump,initret,precall]')
t=t.replace("elif a==dump:\n", "elif a==precall:\n            row['kind']='pre_dump_call';row['context']=dump_context()\n        elif a==dump:\n")
t=t.replace("except BaseException as exc:\n    r.update", "except BaseException as exc:\n    import traceback\n    r['host_traceback']=traceback.format_exc()\n    r.update")
(k/'trace.py').write_text(t)
# This kit is derived once, not by rerunning the old setup programs.
p=k/'preflight.py';t=p.read_text().replace("'setup-kit.py','setup-trace.py'","'setup.py'");t=t.replace("'layouts.json','fixture-crash002.json'","'layouts.json','fatx-review.json','fixture-crash002.json'");p.write_text(t)
(k/'artifacts').mkdir()
for n in ['probe.exe','trigger.sys']:(k/'artifacts'/n).write_bytes((old/'artifacts'/n).read_bytes())
(k/'derivation.json').write_text(json.dumps(dict(parent_kit='controlled-dump',parent_source_sha256={n:sha(old/n) for n in unchanged+changed+['trace.py']},change='Replace discarded PE entrypoint pins with resident HAL/FATX dispatch pins. Add pre-dump call observation and host traceback. Same trigger/probe binaries; no driver/settings patch.'),indent=2)+'\n')
print('New crash002 kit generated, never prepared/launched')
