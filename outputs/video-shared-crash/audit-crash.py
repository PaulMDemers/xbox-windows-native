"""Cold read-only audit of the single intentional crash; no recovery or gate waiver."""
import contextlib,re,struct,subprocess,sys
from common import *
from allocation import scan
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
out=k/'crash001';art=out/'artifacts';art.mkdir(exist_ok=True);dest=out/'audit.json';assert not dest.exists()
f=read(k/'fixture-crash001.json');disk=ws/'work/runs/nt5-video-shared-crash-crash001/hdd.qcow2';base=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name']
assert (disk.parent/'cleanup.json').exists() and sha(base)==f['fixture_sha256']
for v in f['parents']:assert sha(Path(v['path']))==v['sha256']
oracle=read(out/'before-pagefile-map.json');absolute=oracle['partition_offset']+oracle['requested_65536'][0]['volume_byte_offset'];alias=absolute%(1<<37)
r=dict(scope=__doc__,physical_access=False,intentional_crash=True,ordinary_qualified=False,crash_disk_sha256=sha(disk),protected=[],payloads=[],hives=[],new_events={},pagefile_disk_offset=absolute,lba28_alias_offset=alias)
with contextlib.ExitStack() as stack:
    ios=[stack.enter_context(ColdIO(p)) for p in [base,disk]];before,after=[readers(io,p) for io,p in zip(ios,[base,disk])]
    try:intent=after['F'].read('xwndump103/intent.log');(art/'intent.log').write_bytes(intent);r['intent']=intent.decode('ascii',errors='backslashreplace')
    except KeyError:r['intent']=None
    r['intent_exact']=r['intent']=='INTENT E058D103 44554D50 00000103 00010000 00000001\r\nDRIVER_READY; WAITING_30000_MS\r\nTRIGGER_ONCE\r\n'
    for row in f['protected']:
        h=m.sha(after[row['volume']].read(row['path']));r['protected'].append(dict(**row,after_sha256=h,matched=h==row['sha256']))
    for row in f['payloads']:
        h=m.sha(after['F'].read(row['path']));r['payloads'].append(dict(path=row['path'],sha256=h,matched=h==row['sha256']))
    r['startup_unchanged']=m.sha(after['F'].read(STARTUP))==f['startup_sha256']
    for name in HIVES:
        b=after['F'].read('winnt/system32/config/'+name);p=art/('after-'+name);p.write_bytes(b);v=dict(name=name,sha256=m.sha(b),parsed=False,sequence=list(struct.unpack_from('<2I',b,4)))
        try:
            h=hivex.Hivex(str(p));todo=[h.root()];seen=set();count=0
            while todo:
                n=todo.pop();assert n not in seen;seen.add(n);h.node_name(n)
                for item in h.node_values(n):h.value_key(item);h.value_value(item);count+=1
                todo.extend(h.node_children(n))
            v.update(parsed=True,keys=len(seen),values=count)
        except Exception as exc:v['error']=repr(exc)
        r['hives'].append(v)
    r['event_history_preserved']=True
    for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
        rows=[]
        for phase,rr in [('before',before),('after',after)]:
            p=art/(phase+'-'+name);p.write_bytes(rr['F'].read('winnt/system32/config/'+name));target=out/(phase+'-'+label+'-events.json')
            subprocess.run([sys.executable,str(ws/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(p),'--output',str(target)],check=True,stdout=subprocess.DEVNULL);rows.append(read(target)['records'])
        a,b=rows;by={v['record']:v for v in b};r['event_history_preserved'] &= all(by.get(v['record'])==v for v in a);boundary=max((v['record'] for v in a),default=0);r['new_events'][label]=[v for v in b if v['record']>boundary]
    pagefiles=[];alias_bytes=[]
    for phase,rr,io in zip(['before','after'],[before,after],ios):
        b=rr['F'].read('pagefile.sys');assert len(b)==96*1024*1024
        (art/(phase+'-pagefile-prefix.bin')).write_bytes(b[:65536]);pagefiles.append(dict(phase=phase,sha256=m.sha(b),prefix_sha256=m.sha(b[:65536]),header8=b[:8].hex(),bugcheck_fields=[hex(v) for v in struct.unpack_from('<5I',b,0x28)]))
        io.seek(absolute);assert io.read(65536)==b[:65536]
        io.seek(alias);ab=io.read(65536);alias_bytes.append(ab);(art/(phase+'-alias.bin')).write_bytes(ab)
    r['pagefiles']=pagefiles;r['alias_unchanged']=alias_bytes[0]==alias_bytes[1]
    r['dump_header_matches']=pagefiles[1]['header8']==b'PAGEDUMP'.hex() and pagefiles[1]['bugcheck_fields']==['0xe058d103','0x44554d50','0x103','0x10000','0x1']
trace=disk.parent/'cpu-trace.log';r['disk_trace_sha256']=sha(trace);writes=[]
for line in trace.read_text(errors='replace').splitlines():
    v=re.search(r'^blk_co_pwritev .* offset (\d+) bytes (\d+) flags (\S+)',line)
    if v:
        offset,size=int(v[1]),int(v[2]);writes.append(dict(offset=offset,size=size,flags=v[3]))
r['traced_writes']=len(writes);r['pagefile_prefix_writes']=[v for v in writes if v['offset']<absolute+65536 and v['offset']+v['size']>absolute]
r['alias_writes']=[v for v in writes if v['offset']<alias+65536 and v['offset']+v['size']>alias]
scan(disk,art);a=read(out/'allocation.json');r['allocation_passed']=a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count'];r['allocation_sha256']=sha(out/'allocation.json')
t=read(out/'trace.json');last=next((v for v in t['events'] if v.get('kind')=='dump_return'),None)
r['dump_routine_success']=t['status']=='dump_return_observed' and last is not None and last['returned_boolean']==1 and last['final_status']=='0x0'
r['warnings_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in [1,2]]
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
r['integrity_passed']=r['allocation_passed'] and all(v['parsed'] for v in r['hives']) and all(v['matched'] for v in r['protected']+r['payloads']) and r['startup_unchanged']
r['dump_write_evidence_passed']=r['intent_exact'] and r['dump_routine_success'] and r['dump_header_matches'] and bool(r['pagefile_prefix_writes']) and r['alias_unchanged'] and not r['alias_writes']
r['recovery_qualified']=False;r['physical_qualified']=False
r['limits']='Deliberate crash diagnostic: no normal shutdown expected and no ordinary strict PASS claimed. Dump return/header/high-LBA trace and unchanged28-bit alias are separate from complete dump-format validation, exhaustive post-crash write containment and actual reboot recovery.'
save(dest,r);print(json.dumps({n:r[n] for n in ['intent_exact','dump_routine_success','dump_header_matches','alias_unchanged','integrity_passed','dump_write_evidence_passed','normal_shutdown_count','warnings_errors']},indent=2))
