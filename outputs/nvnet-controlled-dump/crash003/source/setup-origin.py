"""Create a new crash kit; never alter or relaunch any earlier crash attempt."""
from pathlib import Path
import hashlib,json
kit=Path(__file__).resolve().parent;k=kit.parent/'nvnet-controlled-dump';old=kit.parent/'controlled-dump-observe'
assert not k.exists();k.mkdir();(k/'artifacts').mkdir()
unchanged=['trigger.c','probe.c','Build.ps1','review.py','build-review.json','hal-review.json','fatx-review.json','layouts.json','kernel-review.json','atomic_json.py']
changed=['common.py','configuration.py','cold-map.py','prepare.py','Run.ps1','preflight.py','supervise.py','record-closure.py','audit-crash.py','trace.py']
for n in unchanged:(k/n).write_bytes((old/n).read_bytes())
for n in changed:
    s=(old/n).read_text().replace('controlled-dump-observe','nvnet-controlled-dump').replace('crash002','crash003')
    if n=='prepare.py':
        s=s.replace("baseline=read(","assert read(k.parent/'nvnet-shutdown-resident/candidate001/audit.json')['strict_qualification_passed']\nassert read(k.parent/'nvnet-shutdown-resident/control001/audit.json')['strict_qualification_passed']\nbaseline=read(")
        s=s.replace("'classpnp.sys','ftdisk.sys'", "'classpnp.sys','ftdisk.sys','nvnetnt5.sys','ndis.sys'")
        s=s.replace('w.flush()', "nv=read(k/'nvnet-review.json')['candidate001'];np=k.parent/'nvnet-shutdown-resident/artifacts'/nv['name'];assert sha(np)==nv['sha256']\nrow=next(v for v in protected if v['volume']=='F' and v['path']=='winnt/system32/drivers/nvnetnt5.sys');nv_before=row['sha256'];m.replace(w,row['path'],np.read_bytes());row['sha256']=sha(np)\nw.flush()")
        s=s.replace('build_review_sha256=',"nvnet_before_sha256=nv_before,nvnet_after_sha256=nv['sha256'],nvnet_review_sha256=sha(k/'nvnet-review.json'),build_review_sha256=")
    if n=='preflight.py':
        s=s.replace("'setup.py'","'setup-origin.py'").replace("'make-modules.py'","'modules-review.py'")
        s=s.replace("'fatx-review.json','fixture-crash003.json'", "'fatx-review.json','nvnet-review.json','fixture-crash003.json'")
        s=s.replace("f=read(k/'fixture-crash003.json');", "f=read(k/'fixture-crash003.json');assert sha(k/'nvnet-review.json')==f['nvnet_review_sha256'];")
    if n=='trace.py':
        s=s.replace('entry=None;ret=None;', 'entry=None;ret=None;nv_shutdown=None;nv_idle=None;nv_return=None;nv_entry=None;')
        s=s.replace("row['dump_context']=dump_context();remove(bc)", "row['dump_context']=dump_context();remove(bc)\n            nvbase=next(v['base'] for v in loaded if v['name'].lower()=='nvnetnt5.sys');sites=read(k/'nvnet-review.json')['candidate001']['functions']\n            nv_shutdown=nvbase+int(sites['_MiniportShutdown@4']['rva'],16);nv_idle=nvbase+int(sites['_NvNetIdleTransmitter']['rva'],16)\n            row['nvnet_pins']=[pin(nv_shutdown),pin(nv_idle)];arm(nv_shutdown);arm(nv_idle)")
        s=s.replace("elif a in stages:","elif a==nv_shutdown:\n            row['kind']='nvnet_shutdown_entry';nv_entry=dict(stack=regs['ESP'],thread=row['thread']);nv_return=u32(regs['ESP']);row['adapter']=hex(u32(regs['ESP']+4));row['caller_pin']=pin(nv_return);arm(nv_return);remove(a)\n        elif a==nv_idle:\n            row['kind']='nvnet_idle_entry';row['arguments']=[hex(v) for v in struct.unpack('<2I',g.read(regs['ESP']+4,8))];remove(a)\n        elif a==nv_return:\n            row['kind']='nvnet_shutdown_return';assert row['thread']==nv_entry['thread'] and regs['ESP']==nv_entry['stack']+8;remove(a)\n        elif a in stages:")
    (k/n).write_text(s)
for n in ['probe.exe','trigger.sys']:(k/'artifacts'/n).write_bytes((old/'artifacts'/n).read_bytes())
(k/'nvnet-review.json').write_bytes((kit/'nvnet-review.json').read_bytes())
(k/'setup-origin.py').write_bytes(Path(__file__).read_bytes())
print('New crash003 scripts only; not prepared or launched')
