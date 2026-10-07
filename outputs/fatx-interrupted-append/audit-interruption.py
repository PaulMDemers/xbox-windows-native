"""Read a closed intentionally interrupted guest; never qualify an ordinary boot."""
import contextlib,hashlib,importlib,json,struct,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['001','002','003']
out=k/case;art=out/'artifacts';dest=out/'interruption-audit.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
f=read(k/('fixture-'+case+'.json'));trace=read(out/'trace.json')
source=out/'trace-source.py' if (out/'trace-source.py').exists() else k/'trace.py'
assert sha(source.read_bytes())==trace['source_sha256']
assert sha((k/'sites.json').read_bytes())==trace['sites_sha256']
run=ws/('work/runs/nt5-fatx-interrupted-append-'+case)
assert (run/'cleanup.json').exists() and trace.get('ended_utc')
sys.path.insert(0,str(k.parent/'native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
sys.path.insert(0,str(k.parent/'fatx-mapped-eof'));from coldio import ColdIO
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
base=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name']
assert m.filehash(base)==f['fixture_sha256']
control=k.parent/'fatx-paging-buffer/002';normal=(control/'artifacts/after-setupapi.log').read_bytes()
assert sha(normal)==trace['control_log_sha256']
target=trace['target'];expected=normal[target:target+220]
assert sha(expected)==trace['expected_warning_sha256']
checkpoint=trace.get('checkpoint_reached',False)
exit_record=read(out/'exit-observation.json')
# The monitor socket reset when the owned xemu exited with code0 after HMP quit.
# Preserve the raw misleadingly named resume_error; no resume was attempted.
quit_disconnect=(trace.get('resume_error')=="ConnectionResetError(10054, 'An existing connection was forcibly closed by the remote host', None, 10054, None)"
    and bool(trace.get('quit_requested_utc')) and exit_record['owned_emulator_exit_code']==0 and exit_record['owned_pid_absent'])
r=dict(scope=__doc__,case=case,physical_access=False,ordinary_qualified=False,physical_qualified=False,
       intentional_interruption=True,trace_sha256=sha((out/'trace.json').read_bytes()),checkpoint_reached=checkpoint,
       trace_guards_passed=bool(checkpoint and trace.get('guest_held_stopped') and trace.get('guest_resumed') is False and not trace.get('prefix_write_observed') and not trace.get('armed_breakpoints_remaining') and not trace.get('pending_write_count') and not trace.get('pending_cache_count') and (not trace.get('resume_error') or quit_disconnect)),
       quit_socket_reset_classified=quit_disconnect,raw_exit_protocol_error=trace.get('resume_error'),exit_observation_sha256=sha((out/'exit-observation.json').read_bytes()),
       payloads=[],hives=[],new_events={},event_decode_errors=[])
for e in trace['events']:
    if e.get('buffer_file'):
        data=(art/e['buffer_file']).read_bytes();assert sha(data)==e['buffer_sha256'] and len(data)==e['length']
if checkpoint:
    e=trace['events'][trace['checkpoint_buffer_index']];ret=trace['events'][trace['checkpoint_return_index']]
    assert e['byteoffset']==target+111 and e['length']==trace.get('checkpoint_length',109) and (art/e['buffer_file']).read_bytes()[:109]==expected[111:]
    assert ret['entry_index']==e['write_entry_index'] and ret['status']==0 and ret['iosb_information_before_dispatch_completion']==e['length']
    r['checkpoint_source_and_return_verified']=True
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
with contextlib.ExitStack() as stack:
    bio=stack.enter_context(ColdIO(base));aio=stack.enter_context(ColdIO(run/'hdd.qcow2'))
    before=m.Writer(bio,m.fatx.open_partition(bio,base,'F'))
    after=m.Writer(aio,m.fatx.open_partition(aio,run/'hdd.qcow2','F'))
    old=before.read('winnt/setupapi.log');cold=after.read('winnt/setupapi.log')
    (art/'after-setupapi.log').write_bytes(cold)
    # Resolve THIS closed file's chain, independent of normal control topology.
    at=1
    for part in ['winnt','setupapi.log']:
        _,_,entry=after.directory(at)['entries'][part];at=struct.unpack_from('<I',entry,44)[0]
    chain=list(after.chain(at));ci,co=divmod(target,after.p.cluster_size)
    assert ci<len(chain) and co+220<=after.p.cluster_size
    absolute=after.p.cluster_offset(chain[ci])+co
    aio.seek(absolute);raw=aio.read(220);bio.seek(absolute);prior_raw=bio.read(220)
    (art/'after-target-raw.bin').write_bytes(raw);(art/'before-target-raw.bin').write_bytes(prior_raw)
    r['target']=dict(logical_offset=target,log_bytes=len(cold),chain=chain,absolute_byte_offset=absolute,lba=absolute//512,
        file_target_present=len(cold)>=target+220,file_and_raw_agree=cold[target:target+220]==raw,
        before_raw_sha256=sha(prior_raw),after_raw_sha256=sha(raw),expected_sha256=sha(expected),
        before_raw_all_zero=not any(prior_raw),first111_same_as_before=raw[:111]==prior_raw[:111],
        first111_all_zero=not any(raw[:111]),first111_expected=raw[:111]==expected[:111],
        following109_expected=raw[111:]==expected[111:],entire_warning_expected=raw==expected,
        before_log_prefix_preserved=cold.startswith(old),cold_log_sha256=sha(cold))
    for item in f['payloads']+f['preserved_payloads']:
        if item['path']=='winnt/system32/xwn-video-trace.bin':continue
        digest=sha(after.read(item['path']));r['payloads'].append(dict(path=item['path'],sha256=digest,matched=digest==item['sha256']))
    for name in ['system','software','default','sam','security']:
        data=after.read('winnt/system32/config/'+name);path=art/('after-'+name);path.write_bytes(data)
        row=dict(name=name,sha256=sha(data),sequence1=int.from_bytes(data[4:8],'little'),sequence2=int.from_bytes(data[8:12],'little'))
        try:
            h=hivex.Hivex(str(path));todo=[h.root()];seen=set();values=0
            while todo:
                node=todo.pop();assert node not in seen;seen.add(node)
                for v in h.node_values(node):h.value_key(v);h.value_value(v);values+=1
                todo.extend(h.node_children(node))
            row.update(parsed=True,keys=len(seen),values=values)
        except Exception as exc:row.update(parsed=False,error=repr(exc))
        r['hives'].append(row)
    for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
        decoded=[]
        for prefix,w in [('before',before),('after',after)]:
            path=art/(prefix+'-'+name);path.write_bytes(w.read('winnt/system32/config/'+name));output=out/(prefix+'-'+label+'-events.json')
            p=subprocess.run([sys.executable,str(k.parent/'native-windows-physical-f/decode-legacy-events.py'),str(path),'--output',str(output)],capture_output=True,text=True)
            if p.returncode:r['event_decode_errors'].append(dict(label=label,phase=prefix,returncode=p.returncode,error=p.stderr));break
            decoded.append(read(output)['records'])
        if len(decoded)==2:
            a,b=decoded;boundary=max((v['record'] for v in a),default=0)
            r['new_events'][label]=[v for v in b if v['record']>boundary]
    for path in ['xwnidle/result.log','xwnidle/windows.log','xwnidle/drawing.log']:
        try:data=after.read(path)
        except KeyError:r.setdefault('missing_helper_logs',[]).append(path);continue
        (art/('interrupted-'+Path(path).name)).write_bytes(data)
        r.setdefault('helper_logs',{})[path]=data.decode('cp1252')
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events'].get('system',[]))
r['split_reproduced']=bool(r['trace_guards_passed'] and r['target']['file_and_raw_agree'] and r['target']['before_raw_all_zero'] and r['target']['first111_all_zero'] and r['target']['following109_expected'])
r['limits']='Intentional guest stop with HMP host quit differs from physical power loss. No Windows normal shutdown or full installation is expected or qualified. Parsed hives and consistent allocation do not establish completed transaction durability. This mechanism does not establish the original physical incident cause; its reboot method remains unknown.'
dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['checkpoint_reached','trace_guards_passed','target','split_reproduced','normal_shutdown_count','hives']},indent=2))
