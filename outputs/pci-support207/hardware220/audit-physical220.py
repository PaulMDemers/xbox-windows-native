"""Offline physical220 preflight/collection audit. Never writes a hive or contacts a console."""
import argparse,hashlib,importlib,importlib.util,json,struct,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;repo=k.parents[2]
sys.path.insert(0,str(repo/'outputs/setup-wizard-automation201'))
from common import hive
sys.path.insert(0,str(k.parent))
from inventory import snapshot
sys.path.insert(0,str(k))
analyze=importlib.import_module('analyze-inventory').analyze
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()

def save(path,result):
    with path.open('x',encoding='utf-8') as f:f.write(json.dumps(result,indent=2)+'\n')

def data(row):
    b=(repo/row['path']).read_bytes();assert sha(b)==row['sha256'];assert len(b)==row['bytes'];return b

def inspect_hive(row):
    b=data(row);r=hive(repo/row['path']);words=struct.unpack('<128I',b[:512]);checksum=0
    for word in words[:127]:checksum^=word
    checksum=0xfffffffe if checksum==0xffffffff else 1 if checksum==0 else checksum
    r.update(header_sequences_equal=words[1]==words[2],header_checksum_valid=words[127]==checksum)
    return r

def configuration(values):
    # Keep every value in device/class/service/policy subtrees. Do not conceal
    # a natural PnP change; a difference holds closure for explicit review.
    tokens=('\\enum\\','\\services\\','\\control\\class','\\control\\deviceclasses',
            '\\control\\video','\\control\\crashcontrol')
    return {key:value for key,value in values.items() if key=='\\Select' or any(t in key.lower() for t in tokens)}

def pci(values):
    cs='ControlSet%03d'%values['\\Select']['Current']['decoded']
    return {key:value for key,value in values.items() if key.startswith('\\'+cs+'\\Enum\\PCI\\') and len(key.split('\\'))==6}

def audit(phase):
    record=k/'physical001.json';p=read(record)
    dest=k/('physical001-preflight.json' if phase=='before' else 'physical001-audit.json')
    assert not dest.exists();assert p.get('capture_complete_utc')
    phases=['before'] if phase=='before' else ['before','after']
    if phase=='after':assert p.get('collected_utc') and not p['startup_enabled']
    for name in phases:
        for row in p[name].values():
            if row:data(row)
    r=dict(scope=__doc__,record_sha256=sha(record.read_bytes()),hives=[],physical_function_qualified=False,
           ordinary_qualified=False,normal_shutdown_qualified=False,full_allocation_audited=False)
    for ph in phases:
        for name in ('system','software','default','sam','security'):
            r['hives'].append(dict(phase=ph,name=name,**inspect_hive(p[ph][name])))
    r['hives_valid']=all(v['parsed'] and v['header_sequences_equal'] and v['header_checksum_valid'] for v in r['hives'])
    old=snapshot(repo/p['before']['system']['path']);r['incoming_pci']=pci(old)
    r['incoming_protected_exact']=all(v['matched'] and v['actual']==v['expected']==p['before'][v['path']]['sha256'] for v in p['before_checks'])
    review=read(k/'build001-review.json')
    r['helper_review_valid']=review['passed'] and all(sha((k/'artifacts/build001'/name).read_bytes())==review[name.split('.')[0]+'_sha256'] for name in ('inventory.exe','observer.exe'))
    if phase=='before':
        r['rehearsal_passed']=read(k/'emulator003/audit.json')['diagnostic_usable']
        r['ready_for_read_only_trial']=r['hives_valid'] and r['incoming_protected_exact'] and r['helper_review_valid'] and r['rehearsal_passed']
        save(dest,r);print(json.dumps({key:r[key] for key in ('hives_valid','incoming_protected_exact','ready_for_read_only_trial')}));return
    new=snapshot(repo/p['after']['system']['path']);r['returned_pci']=pci(new)
    a,b=configuration(old),configuration(new)
    r['configuration_delta']=[dict(path=key,before=a.get(key),after=b.get(key)) for key in sorted(set(a)|set(b)) if a.get(key)!=b.get(key)]
    r['configuration_unchanged']=not r['configuration_delta']
    r['startup_restored']=data(p['before']['startup.cmd'])==data(p['after']['startup.cmd']) and p['startup_backup_exact']
    r['protected_exact']=all(v['matched'] and v['sha256']==p['before'][v['path']]['sha256'] for v in p['after_checks']) and len(p['after_checks'])==len(p['before_checks'])
    r['inventory_complete']=False
    if p['after'].get('inventory.log'):
        observed=analyze(data(p['after']['inventory.log']));save(k/'physical001-inventory.json',observed);r['inventory_complete']=observed['completed']
    r['observer_complete']=False
    if p['after'].get('observer.log'):
        spec=importlib.util.spec_from_file_location('pci220_observer',repo/'outputs/device-durability189/analyze.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        observed=module.analyze(data(p['after']['observer.log']));save(k/'physical001-observer.json',observed);r['observer_complete']=observed['completed']
    r['helpers_exit_zero']=bool(p['after'].get('result.txt') and data(p['after']['result.txt']).decode('ascii').splitlines()==['INVENTORY_EXIT 0','OBSERVER_EXIT 0'])
    a=data(p['before']['setupapi.log']);b=data(p['after']['setupapi.log']);r['setupapi_history_preserved']=b.startswith(a)
    if b.startswith(a):save(k/'physical001-setupapi-delta.json',dict(new_bytes=len(b)-len(a),text=b[len(a):].decode('cp1252')))
    r['event_history_preserved']=True;r['new_events']={}
    for name,label in (('sysevent.evt','system'),('appevent.evt','application')):
        decoded=[]
        for ph in ('before','after'):
            out=k/('physical001-'+ph+'-'+label+'-events.json');assert not out.exists()
            subprocess.run([sys.executable,str(repo/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(repo/p[ph][name]['path']),'--output',str(out)],check=True,stdout=subprocess.DEVNULL)
            decoded.append(read(out)['records'])
        a,b=decoded;by={v['record']:v for v in b};r['event_history_preserved'] &= all(by.get(v['record'])==v for v in a)
        boundary=max((v['record'] for v in a),default=0);r['new_events'][label]=[v for v in b if v['record']>boundary]
    r['warnings_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in (1,2)]
    r['normal_shutdown_event_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
    r['dashboard_return_recorded']=bool(p.get('dashboard_reply') and p.get('collected_utc'))
    r['baseline_restored']=r['startup_restored'] and r['protected_exact'] and r['configuration_unchanged'] and r['hives_valid'] and r['dashboard_return_recorded']
    r['diagnostic_usable']=r['baseline_restored'] and r['inventory_complete'] and r['observer_complete'] and r['helpers_exit_zero'] and p['helpers_exact'] and r['event_history_preserved'] and r['setupapi_history_preserved']
    r['limits']='Read-only OS identification. No direct PCI/SMBus/codec probe, full physical allocation audit or performance qualification. EventLog6006 and dashboard access do not alone prove a normal user restart.'
    save(dest,r);print(json.dumps({key:r[key] for key in ('baseline_restored','configuration_unchanged','diagnostic_usable','normal_shutdown_event_count')},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=('before','after'));audit(ap.parse_args().phase)
