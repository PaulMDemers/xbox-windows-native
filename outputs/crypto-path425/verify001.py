"""Independent review of this closed trace, with actual-evidence mutation controls."""
import copy,hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((K/'sites003.json').read_text());pe=pefile.PE('E:/xwn425/build002/trace.exe')
original=json.loads((K/'emu001/trace.json').read_text())
dest=K/'trace-verification001.json';assert not dest.exists()
def qualify(r):
    assert r['status']=='all_checkpoints_complete' and r['phase']==6
    assert r['guest_resumed'] and r['physical_mode_after']=='0'
    assert not r['armed_remaining'] and not r['incomplete_indices'] and not r['unpaired_returns']
    assert not r.get('error') and not r.get('teardown_error') and r['ordinary_qualified'] is False
    assert len(r['checkpoints'])==7 and len(r['events'])==145
    owner=r['owner'];assert owner['image']=='trace.exe'
    base=plan['image_base'];cp=base+plan['checkpoint']['rva']
    for i,c in enumerate(r['checkpoints']):
        assert c['phase']==i and c['identity']==owner
        s=c['state'];assert len(s)==10 and s[0]==0x42504250 and s[1]==max(0,i-1)
        assert s[2:5]==[owner['pid'],owner['tid'],plan['ntdll_base']] and s[9]==base
        assert s[5:9]==[plan['ntdll_base']+a['rva'] for a in plan['apis']]
        ret=c['return_address'];instruction=pe.get_data(ret-base-5,5)
        assert instruction[0]==0xe8 and ret+struct.unpack('<i',instruction[1:])[0]==cp
    stages=[c['utc'] for c in r['checkpoints']];assert stages==sorted(stages)
    for i,e in enumerate(r['events']):
        assert e['index']==i and e['paired'] and not e['pending'] and e['status']!=0x103
        assert e['status_hex']==f"{e['status']:08x}" and 0<=e['phase']<6
        assert stages[e['phase']]<=e['utc']<=e['return_utc']<=stages[e['phase']+1]
        assert e['owned_probe_thread']==(e['identity']==owner)
        assert e['identity']['image'] in ['trace.exe','services.exe']
        name=e['object_name'];assert len(name['name'].encode('utf-16le'))==name['name_bytes']
        assert name['absolute_name_observed']==(name['root_handle']==0 and name['name'].startswith('\\'))
    rows=[]
    expected=[(30,1,43,False,2,'trace.exe'),(31,1,69,False,2,'trace.exe'),
              (83,2,44,True,2,'trace.exe'),(112,3,69,False,3,'trace.exe'),(130,4,44,True,2,'services.exe')]
    for index,phase,n,directory,disposition,image in expected:
        e=r['events'][index];o=e['object_name'];parts=o['name'].split('\\');leaf=parts[-1]
        assert e['api']=='NtCreateFile' and e['phase']==phase and e['status']==0xc0000106
        assert o['absolute_name_observed'] and o['root_handle']==0
        assert len(leaf.encode('cp437'))==n and e['identity']['image']==image
        assert bool(e['arguments'][8]&1)==directory and e['arguments'][7]==disposition
        if phase==2:assert '\\Microsoft\\Crypto\\RSA\\S-1-5-21-' in o['name']
        if phase==3:assert '\\Microsoft\\Crypto\\RSA\\MachineKeys\\' in o['name']
        if phase==4:assert '\\Microsoft\\Protect\\S-1-5-21-' in o['name']
        rows.append({'event':index,'phase':phase,'process':image,'path':o['name'],'leaf_oem_bytes':n,
                     'directory':directory,'disposition':disposition,'ntstatus':e['status_hex']})
    assert r['events'][83]['object_name']['name'].split('\\')[-1]==r['events'][130]['object_name']['name'].split('\\')[-1]
    for i in [138,139,140]:
        e=r['events'][i];assert e['phase']==5 and e['status']==0 and e['identity']['image']=='services.exe'
        assert '\\Microsoft\\Protect\\S-1-5-18\\' in e['object_name']['name']
    for pin in r['pins']:
        if 'expected' in pin:assert pin['bytes']==pin['expected']
    return rows
rows=qualify(original);count=0
def reject(r):
    global count
    try:qualify(r)
    except (AssertionError,KeyError,ValueError,IndexError,UnicodeError):count+=1;return
    raise AssertionError('Mutated proof accepted')
for i in range(145):
    for field,value in [('paired',False),('pending',True),('status_hex','bad'),('index',999),('phase',6)]:
        r=copy.deepcopy(original);r['events'][i][field]=value;reject(r)
for i in [30,31,83,112,130]:
    for field,value in [('name','\\??\\C:\\short'),('root_handle',4),('absolute_name_observed',False)]:
        r=copy.deepcopy(original);r['events'][i]['object_name'][field]=value;reject(r)
    for field,pos in [('arguments',7),('arguments',8)]:
        r=copy.deepcopy(original);r['events'][i][field][pos]^=1;reject(r)
    r=copy.deepcopy(original);r['events'][i]['status']=0;r['events'][i]['status_hex']='00000000';reject(r)
for i in range(7):
    for field,value in [('phase',99),('return_address',0),('identity',{})]:
        r=copy.deepcopy(original);r['checkpoints'][i][field]=value;reject(r)
    for j in range(10):
        r=copy.deepcopy(original);r['checkpoints'][i]['state'][j]^=1;reject(r)
for field,value in [('status','incomplete'),('guest_resumed',False),('physical_mode_after','1'),('armed_remaining',[1]),('incomplete_indices',[0]),('unpaired_returns',[{}]),('ordinary_qualified',True)]:
    r=copy.deepcopy(original);r[field]=value;reject(r)
frozen=json.loads((K/'emu001/frozen.json').read_text())
for path,h in frozen.items():assert sha(W/path)==h,path
assert sha(Path('E:/xwn425/build002/trace.exe'))==plan['native_sha256']
proof=json.loads((W/'outputs/crypto-persistence423/ntfs-independent001.json').read_text())
machine=rows[3]['path'].split('\\')[-1]
assert any(x['path'].endswith('/machinekeys/'+machine) for x in proof['rows'])
out={'passed':True,'scope':'Actual native syscall boundary paths/statuses; no kernel internal dispatch or RPC call-ID trace',
     'trace_sha256':sha(K/'emu001/trace.json'),'events':145,'paired':145,'checkpoints':7,'owned_probe_events':sum(e['owned_probe_thread'] for e in original['events']),
     'service_events':sum(e['identity']['image']=='services.exe' for e in original['events']), 'name_too_long_requests':rows,
     'machine_key_leaf_matches_ntfs_control':True,'actual_mutations_rejected':count,'frozen_inputs_exact':len(frozen),
     'rpc_causality_qualified':False,'ordinary_qualified':False,'physical_access':False}
dest.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['passed','events','paired','checkpoints','actual_mutations_rejected']}))
