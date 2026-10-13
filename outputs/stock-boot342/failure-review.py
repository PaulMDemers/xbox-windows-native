"""Resolve the failed event gate from collected hives; no physical access or waiver."""
import hashlib,json,struct,sys
from pathlib import Path
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
K=Path(__file__).resolve().parent;dest=K/'failure-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(K/'physical001/audit.json');old=read(K.parent/'hd-large-physical331/failure-review.json')
maps=[]
for phase in ['before001','physical001']:
    p=K/'artifacts'/phase/'E/winnt/system32/config/system';h=hivex.Hivex(str(p))
    n=h.node_get_child(h.root(),'MountedDevices');v=h.node_get_value(n,'\\DosDevices\\F:');typ,b=h.value_value(v)
    assert typ==3 and len(b)==12 and struct.unpack('<IQ',b)==(0xaa55,2359820288)
    maps.append(dict(phase=phase,system_sha256=sha(p),value=b.hex(),partition_byte_offset=2359820288))
events=[v for v in a['interval_warning_errors'] if v['source']=='Srv' and v['event_id']==2013]
assert len(events)==1 and events[0]['strings']==['\\Device\\LanmanServer','F:']
r=dict(physical_access=False,scoped_passed=a['scoped_combined_passed'],strict_passed=a['strict_qualification_passed'],
       interval_event=events[0],current_and_before_F_mapping=maps,
       historical_message_resource=old['historical_message_resource'],
       mapping_interpretation='Windows F: remains dashboard C: at byte offset2359820288. New Windows C: is dashboard E, Windows D: is dashboard F.',
       limits='No dashboard C access, capacity query, cleanup, policy change or event suppression. The message is a low-space warning; current C free space and its cause remain unmeasured. Ftdisk49 on new HarddiskVolume1 also remains a strict failure. Moving Windows to E did not resolve the warning. No gate changed.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Current before/after Windows F mapping confirmed dashboard C; failed gates retained')
