"""Cold genuine resource-only PnP trial audit; no hardware qualification."""
import contextlib, importlib, importlib.util, json, struct, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;repo=k.parents[2]
sys.path.insert(0,str(repo/'outputs/setup-wizard-automation201'))
from common import ColdIO, readers, hive, sha, read, save, scan
sys.path.insert(0,str(k.parent))
from inventory import snapshot
out=k/'emulator001';art=out/'artifacts/audit';assert not art.exists();art.mkdir()
dest=out/'audit.json';assert not dest.exists()
run=read(out/'run.json');assert run['closed'] and run['source_unchanged']
f=read(out/'fixture.json');base=out/'artifacts/source.qcow2';disk=out/'artifacts/runtime/hdd.qcow2'
assert sha(base)==f['source_sha256']
r=dict(scope=__doc__,physical_access=False,ordinary_qualified=False,persistent_binding_qualified=False,
       normal_shutdown_qualified=False,hardware_ready=False,files=[],hives=[],logs={},new_events={})
with contextlib.ExitStack() as stack:
    before,after=[readers(stack.enter_context(ColdIO(p)),p) for p in (base,disk)]
    for name,digest in f['files'].items():
        v,path=name.split('/',1)
        if path.lower().startswith('winnt/system32/config/') or path.lower() in ('winnt/setupapi.log','winnt/system32/xwn-video-trace.bin'):continue
        try:actual=__import__('hashlib').sha256(after[v].read(path)).hexdigest()
        except KeyError:actual=None
        r['files'].append(dict(path=name,before=digest,after=actual,matched=actual==digest))
    for name in ('install.log','lifecycle.log','install-exit.txt','probe-exit.txt'):
        try:data=after['F'].read('xwnpcilife3/'+name)
        except KeyError:continue
        (art/name).write_bytes(data);r['logs'][name]=data.decode('ascii',errors='backslashreplace')
    for name in ('system','software','default','sam','security'):
        p=art/('after-'+name);p.write_bytes(after['F'].read('winnt/system32/config/'+name))
        try:result=hive(p)
        except Exception as e:result=dict(parsed=False,error=repr(e))
        header=p.read_bytes()[:512];words=struct.unpack('<128I',header);checksum=0
        for word in words[:127]:checksum^=word
        if checksum==0xffffffff:checksum=0xfffffffe
        elif checksum==0:checksum=1
        result.update(header_sequences_equal=words[1]==words[2],header_checksum_valid=checksum==words[127])
        r['hives'].append(dict(name=name,**result))
    vals=snapshot(art/'after-system');cs='ControlSet%03d'%vals['\\Select']['Current']['decoded']
    before_system=out/'artifacts/before-system';old_vals=snapshot(before_system)
    binding_keys=lambda v:{key:data for key,data in v.items() if any(token in key.lower() for token in ('\\enum\\pci\\','\\control\\class\\','\\control\\deviceclasses\\')) or ('\\services\\' in key.lower() and key.lower().endswith(('\\xwnsmb','\\xwnrsc','\\xwnfatx','\\xboxvnt5','\\nvnetnt5')))}
    r['binding_state_unchanged']=binding_keys(vals)==binding_keys(old_vals)
    a,b=binding_keys(old_vals),binding_keys(vals)
    delta=[dict(path=key,before=a.get(key),after=b.get(key)) for key in sorted(set(a)|set(b)) if a.get(key)!=b.get(key)]
    r['binding_delta']=delta
    expected=k.parent/'hardware220/emulator001/diagnosis.json'
    assert sha(expected)=='e182364e26979c5be2fdf1f19f35784f48cec4b4d570d4c93ea766a1e39b67e5'
    r['matches_reviewed_fixture_transition']=delta==read(expected)['binding_delta']
    r['select']=vals['\\Select'];r['pci_targets']=[]
    for key,data in sorted(vals.items()):
        if key.startswith('\\'+cs+'\\Enum\\PCI\\') and len(key.split('\\'))==6 and any(x in key.upper() for x in ('DEV_01B4','DEV_01C1')):
            d=data.get('Driver',{}).get('decoded');s=data.get('Service',{}).get('decoded')
            r['pci_targets'].append(dict(instance=key,values=data,driver_key=vals.get('\\'+cs+'\\Control\\Class\\'+d,{}) if d else None,
                                        service_key=vals.get('\\'+cs+'\\Services\\'+s,{}) if s else None))
    a=before['F'].read('winnt/setupapi.log');b=after['F'].read('winnt/setupapi.log')
    (art/'before-setupapi.log').write_bytes(a);(art/'after-setupapi.log').write_bytes(b)
    r['setupapi_history_preserved']=b.startswith(a)
    if b.startswith(a):
        delta=b[len(a):].decode('cp1252',errors='backslashreplace')
        (out/'setupapi-delta.txt').write_text(delta,encoding='utf-8');r['setupapi_new_bytes']=len(b)-len(a)
    r['event_history_preserved']=True
    for name,label in (('sysevent.evt','system'),('appevent.evt','application')):
        decoded=[]
        for phase,rr in (('before',before),('after',after)):
            p=art/(phase+'-'+name);p.write_bytes(rr['F'].read('winnt/system32/config/'+name));d=out/(phase+'-'+label+'-events.json')
            subprocess.run([sys.executable,str(repo/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(p),'--output',str(d)],check=True,stdout=subprocess.DEVNULL)
            decoded.append(read(d)['records'])
        a,b=decoded;by={v['record']:v for v in b};r['event_history_preserved'] &= all(by.get(v['record'])==v for v in a)
        boundary=max((v['record'] for v in a),default=0);r['new_events'][label]=[v for v in b if v['record']>boundary]
scan(disk,art/'allocation');allocation=read(art/'allocation.json')
r['allocation_passed']=allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
r['integrity_passed']=bool(r['allocation_passed'] and all(v['parsed'] and v['header_checksum_valid'] and v['header_sequences_equal'] for v in r['hives']) and all(v['matched'] for v in r['files']) and r['setupapi_history_preserved'] and r['event_history_preserved'])
r['warnings_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in (1,2)]
r['install_exit_zero']=r['logs'].get('install-exit.txt','').splitlines()==['INSTALL_EXIT 0']
r['lifecycle_completed']='RESOURCE_ONLY_PNP_LIFECYCLE_END' in r['logs'].get('lifecycle.log','')
r['normal_shutdown_event_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
r['whole_boot_passed']=False
r['diagnostic_usable']=r['integrity_passed']
r['limits']='Resource-only PnP test; evaluate actual devnode, resource and SetupAPI data before qualification. No telemetry or hardware qualification. Inherited Ftdisk49 retained.'
save(dest,r);print(json.dumps({key:r[key] for key in ('install_exit_zero','lifecycle_completed','integrity_passed','normal_shutdown_event_count','logs','warnings_errors')},indent=2))
