"""Fresh observation-only controller; no preparation or launch on invocation."""
import json
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'owned-reuse275'
build=json.loads((k/'renderer-build002.json').read_text());assert build['passed'] and build['borrowed_sources_restored']
names=['model.py','protocol.py','objects.py','oracle.py','proof.py','graph_base.py','graph_extra.py','terminal.py','backend.py','trace.py','prepare.py','Run.ps1','audit.py','analyze-disk-delta.py']
for name in names:
    s=(old/name).read_text().replace('xwn275','xwn276').replace('owned-reuse275','callback-inventory276').replace('4754','4764').replace('4755','4765')
    if name=='prepare.py':
        s=s.replace('boundary274-build002/xemu-boundary274.exe','callback276-build002/xemu-callback276.exe').replace('3c3c61fff0615a2e2781b90a3f4ed9a6b119e343222e5defdcad4f0ea4cd806e',build['executable_sha256'])
    if name=='backend.py':
        s=s.replace("self.set('xwn-ledger265','capture,1')","self.set('xwn-ledger265','observe276')")
        s=s.replace("        if numbers(s).get('pages'):self.pages('initial',s,1)","        inventory=self.get('xwn-callbacks276');self.r['callback_inventory_report']=inventory;self.save()\n        if numbers(s).get('pages'):self.pages('initial',s,1)")
        s=s.replace("        validate_report(s,1);assert self.get('xwn-ledger265-report')==s","        assert self.get('xwn-ledger265-report')==s\n        self.r['inventory_collection_completed']=True;self.save()\n        raise RuntimeError('Observation-only276 closed after initial refusal; no guest resume or observer arm')")
        s=s.replace("sha256=hashlib.sha256(s.encode()).hexdigest()))","sha256=hashlib.sha256(s.encode()).hexdigest()))\n            self.r[kind+'_pages']=list(manifest);self.save()")
    if name=='trace.py':
        s=s.replace('from backend import Backend','from backend import Backend\nfrom atomic_json import write_json')
        s=s.replace("    p=out/'trace.partial.json';p.write_text(json.dumps(r,indent=2)+'\\n');p.replace(out/'trace.json')","    write_json(out/'trace.json',r)")
        a="    reply=monitor(4764,s,quit);r['monitor'].append(dict(command=s,reply=reply,utc=utc()));save();return reply"
        b="""    reply=monitor(4764,s,quit);entry=dict(command=s,utc=utc())
    if len(reply)>4096:
        p=private/('monitor-'+str(len(r['monitor'])).zfill(4)+'.txt');assert not p.exists();p.write_bytes(reply.encode())
        entry.update(private_reply=str(p),sha256=sha(reply.encode()),bytes=len(reply.encode()))
    else:entry['reply']=reply
    r['monitor'].append(entry);save();return reply"""
        assert a in s;s=s.replace(a,b)
    p=k/name;assert not p.exists();p.write_text(s)
for name in ['atomic_json.py','test-atomic-json.py']:
    p=k/name;assert not p.exists();p.write_bytes((k.parent/'surface-bridge260'/name).read_bytes())
print('Created276 observation-only runtime; no child or launch')
