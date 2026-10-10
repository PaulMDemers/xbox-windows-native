"""Inspect already cold-extracted hives/events; never access a running disk."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;repo=k.parents[1];case=sys.argv[1]
assert re.fullmatch('emu[0-9]{3}',case)
run=repo/('work/runs/nt5stortrace-'+case);assert (run/'cleanup.json').exists()
assert (k/(case+'-review.json')).exists()
out=k/case;dest=out/'details.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(physical_access=False,case=case,hives={},new_events={},event_history_preserved=True)
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
for name in ['system','software','default','sam','security']:
    h=hivex.Hivex(str(run/('after-'+name)));todo=[('',h.root())];seen=set();count=0;selected={}
    while todo:
        path,node=todo.pop();assert node not in seen;seen.add(node);h.node_name(node)
        keep=name=='system' and any(s in path.lower() for s in ['vid_045e&pid_0202','services/xwnxid','745a17a0-74d3-11d0-b6fe-00a0c90f57da'])
        values={}
        for v in h.node_values(node):
            key=h.value_key(v);kind,data=h.value_value(v);count+=1
            if keep:
                value=data.hex()
                if kind in [1,2,7]:value=data.decode('utf-16le',errors='replace').rstrip('\0')
                elif kind==4 and len(data)==4:value=int.from_bytes(data,'little')
                values[key]=dict(type=kind,value=value)
        if keep:selected[path]=values
        for child in h.node_children(node):todo.append((path+'/'+h.node_name(child),child))
    r['hives'][name]=dict(parsed=True,keys=len(seen),values=count,sha256=sha(run/('after-'+name)))
    if selected:r['xid_registry']=selected
decoder=repo/'outputs/native-windows-physical-f/decode-legacy-events.py'
r['event_decoder_sha256']=sha(decoder)
for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
    decoded=[]
    for phase in ['before','after']:
        target=out/(phase+'-'+label+'-events.json')
        subprocess.run([sys.executable,'-B',str(decoder),str(run/(phase+'-'+name)),'--output',str(target)],check=True,stdout=subprocess.DEVNULL)
        decoded.append(read(target)['records'])
    before,after=decoded;by={e['record']:e for e in after}
    r['event_history_preserved'] &= all(by.get(e['record'])==e for e in before)
    boundary=max((e['record'] for e in before),default=0)
    r['new_events'][label]=[e for e in after if e['record']>boundary]
before=(run/'before-setupapi.log').read_bytes();after=(run/'after-setupapi.log').read_bytes()
r['setupapi_history_preserved']=after.startswith(before)
if r['setupapi_history_preserved']:
    (run/'setupapi-delta.txt').write_text(after[len(before):].decode('cp1252',errors='replace'))
r['warnings_errors']=[e for group in r['new_events'].values() for e in group if e['type'] in [1,2]]
r['normal_shutdown_count']=sum(e['source']=='EventLog' and e['event_id']==6006 for e in r['new_events']['system'])
r['strict_events_passed']=not r['warnings_errors'] and not r['new_events']['application']
r['ordinary_boot_qualified']=False
r['scope']='Cold hive traversal, selected USB/HID registry state and record-number event delta. Diagnostic guest may be paused for framebuffer capture or host-stopped. Not physical or ordinary-boot qualification.'
dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['event_history_preserved','setupapi_history_preserved','normal_shutdown_count','strict_events_passed','warnings_errors']}))
